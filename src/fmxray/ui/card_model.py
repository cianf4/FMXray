"""Everything the QML player card shows, already formatted and coloured.

The QML side only lays it out and animates the changes; this object is what the tests read.
"""

from collections.abc import Mapping, Sequence

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication

from fmxray.domain.fields import PLAYER_CATALOG, POSITIONS, FieldGroup, Provenance, Unit
from fmxray.domain.profile import profile
from fmxray.domain.snapshot import SnapshotMeta
from fmxray.ui.pitch import PLACES, position_label
from fmxray.ui.table_model import format_money, format_value
from fmxray.ui.theme import TOKENS, attribute_band

ABILITY_SCALE = 200  # CA and PA run 1-200
_UNITS = {s.name: s.unit for s in PLAYER_CATALOG.fields}


def _shown(group: FieldGroup) -> tuple[str, ...]:
    return tuple(s.name for s in PLAYER_CATALOG.in_group(group) if not s.name.endswith("_raw"))


# Tab title -> (group title, fields) blocks.
TABS: tuple[tuple[str, tuple[tuple[str, Sequence[str]], ...]], ...] = (
    ("Attributes", tuple((g.value.capitalize(), _shown(g)) for g in (
        FieldGroup.TECHNICAL, FieldGroup.MENTAL, FieldGroup.PHYSICAL, FieldGroup.GOALKEEPING,
    ))),
    ("Hidden", (
        ("Hidden", _shown(FieldGroup.HIDDEN)),
        ("Personality", _shown(FieldGroup.PERSONALITY)),
    )),
    ("Contract", (
        ("Contract", (*_shown(FieldGroup.CONTRACT), "contract_left")),
        ("Value", _shown(FieldGroup.VALUE)),
        ("Loan", _shown(FieldGroup.LOAN)),
    )),
    ("Positions", (("Feet", _shown(FieldGroup.FEET)),)),
)  # fmt: skip
_CARD_FIELDS = frozenset(f for _, blocks in TABS for _, fields in blocks for f in fields)


def summary_line(values: Mapping[str, object]) -> str:
    """'18 · Club Aurora · DC, DM' with '-' for what is missing."""
    positions = values.get("natural_positions")
    parts = (values.get("age"), values.get("club_name"), positions or None)
    return " · ".join(format_value(part) for part in parts)


def _rated_colour(value: object) -> str:
    band = attribute_band(value) if isinstance(value, int) else None
    return TOKENS[band] if band else TOKENS["text"]


def _text(field: str, value: object) -> str:
    if _UNITS.get(field) is Unit.MONEY_INTERNAL and isinstance(value, int):
        return format_money(value)
    return format_value(value)


def _fraction(value: object) -> float:
    if not isinstance(value, int):
        return 0.0
    return min(max(value / ABILITY_SCALE, 0.0), 1.0)


class CardModel(QObject):
    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._values: Mapping[str, object] = {}
        self._unconfirmed = False

    def set_player(self, meta: SnapshotMeta, values: Mapping[str, object]) -> None:
        self._values = values
        self._unconfirmed = any(
            meta.provenance.get(f) is Provenance.UNCONFIRMED for f in _CARD_FIELDS
        )
        self.changed.emit()

    def clear(self) -> None:
        self._values = {}
        self._unconfirmed = False
        self.changed.emit()

    @Slot()
    def copyName(self) -> None:
        """Puts the name on the clipboard, to paste into FM's search."""
        clipboard = QGuiApplication.clipboard()
        name = self._values.get("name")
        if clipboard is not None and isinstance(name, str):
            clipboard.setText(name)

    def _empty(self) -> bool:
        return not self._values

    def _name(self) -> str:
        if self._empty():
            return ""
        name = self._values.get("name")
        return name if isinstance(name, str) else "-"

    def _initials(self) -> str:
        name = self._values.get("name")
        if not isinstance(name, str):
            return ""
        words = name.split()
        return "".join(w[0] for w in (words[:1] + words[-1:] if len(words) > 1 else words))

    def _summary(self) -> str:
        return "" if self._empty() else summary_line(self._values)

    def _ca(self) -> str:
        return "-" if self._empty() else format_value(self._values.get("ca"))

    def _pa(self) -> str:
        return "-" if self._empty() else format_value(self._values.get("pa"))

    def _ca_fraction(self) -> float:
        return _fraction(self._values.get("ca"))

    def _pa_fraction(self) -> float:
        return _fraction(self._values.get("pa"))

    def _growth(self) -> str:
        ca, pa = self._values.get("ca"), self._values.get("pa")
        if not isinstance(ca, int) or not isinstance(pa, int):
            return ""
        return self.tr("room to grow %1").replace("%1", str(pa - ca))

    def _areas(self) -> list[dict[str, object]]:
        return [
            {
                "name": self.tr(area.name),
                "value": area.value or 0.0,
                "label": "-" if area.value is None else f"{area.value:.1f}",
            }
            for area in profile(self._values)
        ]

    def _tabs(self) -> list[dict[str, object]]:
        return [
            {
                "title": self.tr(title),
                "groups": [
                    {
                        "title": self.tr(group),
                        "rows": [
                            {
                                "label": field.replace("_", " "),
                                "value": _text(field, self._values.get(field)),
                                "color": _rated_colour(self._values.get(field))
                                if _UNITS.get(field) is Unit.DISPLAY_1_20
                                else TOKENS["text"],
                            }
                            for field in fields
                        ],
                    }
                    for group, fields in blocks
                ],
            }
            for title, blocks in TABS
        ]

    def _positions(self) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for code in POSITIONS:
            rating = self._values.get(f"pos_{code}")
            row, column = PLACES[code]
            result.append(
                {
                    "label": position_label(code),
                    "row": row,
                    "column": column,
                    "value": format_value(rating) if isinstance(rating, int) else "",
                    "color": _rated_colour(rating),
                }
            )
        return result

    def _get_unconfirmed(self) -> bool:
        return self._unconfirmed

    empty = Property(bool, _empty, notify=changed)
    name = Property(str, _name, notify=changed)
    initials = Property(str, _initials, notify=changed)
    summary = Property(str, _summary, notify=changed)
    ca = Property(str, _ca, notify=changed)
    pa = Property(str, _pa, notify=changed)
    caFraction = Property(float, _ca_fraction, notify=changed)
    paFraction = Property(float, _pa_fraction, notify=changed)
    growth = Property(str, _growth, notify=changed)
    areas = Property(list, _areas, notify=changed)
    tabs = Property(list, _tabs, notify=changed)
    positions = Property(list, _positions, notify=changed)
    unconfirmed = Property(bool, _get_unconfirmed, notify=changed)
