"""Qt table model over a search result; sorting and filtering happen in Polars."""

from collections.abc import Mapping, Sequence
from datetime import date

import polars as pl
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt, Signal
from PySide6.QtGui import QColor

from fmxray.domain.fields import PLAYER_CATALOG, Provenance, Unit
from fmxray.ui.theme import TOKENS, attribute_band

type _Index = QModelIndex | QPersistentModelIndex

NEW_MARK = "● "
UNCONFIRMED_MARK = " ⓘ"
_RATED = frozenset(s.name for s in PLAYER_CATALOG.fields if s.unit is Unit.DISPLAY_1_20)


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
    return str(value)


class PlayerTableModel(QAbstractTableModel):
    sort_requested = Signal(str, bool)  # field, descending

    def __init__(self) -> None:
        super().__init__()
        self._columns: tuple[str, ...] = ()
        self._values: list[list[object]] = []
        self._uids: list[int] = []
        self._provenance: Mapping[str, Provenance] = {}
        self._new: frozenset[int] = frozenset()

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
        self.endResetModel()

    @property
    def columns(self) -> tuple[str, ...]:
        return self._columns

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
        if role == Qt.ItemDataRole.DisplayRole:
            text = format_value(value)
            if column == 0 and self._uids[row] in self._new:
                return NEW_MARK + text
            return text
        if role == Qt.ItemDataRole.ForegroundRole:
            if column == 0 and self._uids[row] in self._new:
                return QColor(TOKENS["new"])
            if self._columns[column] in _RATED and isinstance(value, int):
                band = attribute_band(value)
                return QColor(TOKENS[band]) if band else None
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
            return name + (UNCONFIRMED_MARK if unconfirmed else "")
        if role == Qt.ItemDataRole.ToolTipRole and unconfirmed:
            return self.tr("unconfirmed: the save reader has not verified this field for this game")
        return None

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        if 0 <= column < len(self._columns):
            self.sort_requested.emit(self._columns[column], order == Qt.SortOrder.DescendingOrder)
