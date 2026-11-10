"""Qt table model over a search result; sorting and filtering happen in Polars."""

from collections.abc import Mapping, Sequence
from datetime import date

import polars as pl
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt, Signal
from PySide6.QtGui import QColor, QFont

from fmxray.domain.fields import PLAYER_CATALOG, Provenance, Unit
from fmxray.domain.text import humanize
from fmxray.ui.theme import TOKENS, attribute_band

type _Index = QModelIndex | QPersistentModelIndex

NEW_MARK = "● "
UNCONFIRMED_MARK = " ⓘ"
_RATED = frozenset(s.name for s in PLAYER_CATALOG.fields if s.unit is Unit.DISPLAY_1_20)
_MONEY = frozenset(s.name for s in PLAYER_CATALOG.fields if s.unit is Unit.MONEY_INTERNAL)
ENUM_FIELDS = frozenset({"contract_squad_status", "traits"})  # snake_case values from the save
PILL_ROLE = Qt.ItemDataRole.UserRole + 1  # the 1-20 value of rated columns, for the delegate


BIG_NUMBER = 10_000  # from here on, thousands get a separator
_TITLES = {
    "ca": "CA", "pa": "PA", "club_name": "Club", "natural_positions": "Positions",
    "accomplished_positions": "Other positions", "transfer_value": "Value", "contract_wage": "Wage",
}  # fmt: skip


def column_title(name: str) -> str:
    if name in _TITLES:
        return _TITLES[name]
    if name.startswith("pos_"):
        return "ST" if name == "pos_stc" else name.removeprefix("pos_").upper()
    return humanize(name)


def format_value(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float):
        return f"{value:g}"
    if isinstance(value, int) and abs(value) >= BIG_NUMBER:
        return f"{value:,}"
    return str(value)


def format_money(value: int | None) -> str:
    """'4.2M', '950K', '999': short enough for a column, the full value goes in the tooltip."""
    if value is None:
        return "-"
    size = abs(value)
    if round(size / 1_000, 1) >= 1_000:
        scale, suffix = 1_000_000, "M"
    elif size >= 1_000:
        scale, suffix = 1_000, "K"
    else:
        return str(value)
    sign = "-" if value < 0 else ""
    return f"{sign}{size / scale:.1f}".removesuffix(".0") + suffix


def format_field(name: str, value: object) -> str:
    """A field's value as shown: compact money, readable enum values, else format_value."""
    if name in _MONEY and isinstance(value, int) and not isinstance(value, bool):
        return format_money(value)
    if name in ENUM_FIELDS and isinstance(value, str):
        return humanize(value)
    if name in ENUM_FIELDS and isinstance(value, list):
        return ", ".join(humanize(str(v)) for v in value)
    return format_value(value)


class PlayerTableModel(QAbstractTableModel):
    sort_requested = Signal(str, bool)  # field, descending

    def __init__(self) -> None:
        super().__init__()
        self._columns: tuple[str, ...] = ()
        self._values: list[list[object]] = []
        self._uids: list[int] = []
        self._provenance: Mapping[str, Provenance] = {}
        self._new: frozenset[int] = frozenset()
        self._numeric: frozenset[str] = frozenset()
        self._number_font = QFont(TOKENS["font_numbers"])

    def set_result(
        self,
        frame: pl.DataFrame,
        columns: Sequence[str],
        provenance: Mapping[str, Provenance],
        new_uids: frozenset[int] = frozenset(),
    ) -> None:
        self.beginResetModel()
        self._columns = tuple(columns)
        # ponytail: whole columns as Python lists, fine at 126k rows; window them past ~1M.
        self._values = [frame[c].to_list() for c in self._columns]
        self._uids = frame["uid"].to_list()
        self._provenance = provenance
        self._new = new_uids
        self._numeric = frozenset(c for c in self._columns if frame.schema[c].is_numeric())
        self.endResetModel()

    @property
    def columns(self) -> tuple[str, ...]:
        return self._columns

    def all_unconfirmed(self) -> bool:
        """True when every shown field is unconfirmed: then one note replaces per-column marks."""
        known = [self._provenance[c] for c in self._columns if c in self._provenance]
        return bool(known) and all(p is Provenance.UNCONFIRMED for p in known)

    def uid_at(self, row: int) -> int:
        return self._uids[row]

    def row_of(self, uid: int) -> int | None:
        try:
            return self._uids.index(uid)
        except ValueError:
            return None

    def rowCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self._uids)

    def columnCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self._columns)

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid():
            return None
        row, column = index.row(), index.column()
        value = self._values[column][row]
        name = self._columns[column]
        money = name in _MONEY and isinstance(value, int) and not isinstance(value, bool)
        if role == Qt.ItemDataRole.DisplayRole:
            text = format_field(name, value)
            if column == 0 and self._uids[row] in self._new:
                return NEW_MARK + text
            return text
        if role == Qt.ItemDataRole.ForegroundRole:
            if column == 0 and self._uids[row] in self._new:
                return QColor(TOKENS["new"])
            if self._columns[column] in _RATED and isinstance(value, int):
                band = attribute_band(value)
                return QColor(TOKENS[band]) if band else None
        numeric = self._columns[column] in self._numeric
        if role == Qt.ItemDataRole.TextAlignmentRole and numeric:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.FontRole and numeric:
            return self._number_font
        if role == PILL_ROLE:
            return value if name in _RATED else None
        if role == Qt.ItemDataRole.ToolTipRole and money:
            return format_value(value)
        if role == Qt.ItemDataRole.ToolTipRole and column == 0 and self._uids[row] in self._new:
            return self.tr("New since the previous snapshot")
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> object:
        if orientation != Qt.Orientation.Horizontal or not 0 <= section < len(self._columns):
            return None
        name = self._columns[section]
        unconfirmed = self._provenance.get(name) is Provenance.UNCONFIRMED
        if role == Qt.ItemDataRole.DisplayRole:
            marked = unconfirmed and not self.all_unconfirmed()
            return column_title(name) + (UNCONFIRMED_MARK if marked else "")
        if role == Qt.ItemDataRole.TextAlignmentRole and name in self._numeric:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.ToolTipRole and unconfirmed:
            return self.tr("unconfirmed: the save reader has not verified this field for this game")
        return None

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        if 0 <= column < len(self._columns):
            self.sort_requested.emit(self._columns[column], order == Qt.SortOrder.DescendingOrder)
