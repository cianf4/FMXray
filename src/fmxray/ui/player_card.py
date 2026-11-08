"""Side panel with every field of the selected player, under a compact three-line header."""

from collections.abc import Mapping, Sequence

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import (
    QFormLayout,
    QGraphicsOpacityEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from fmxray.domain.fields import PLAYER_CATALOG, POSITIONS, FieldGroup, Provenance, Unit
from fmxray.domain.snapshot import SnapshotMeta
from fmxray.ui.icons import icon
from fmxray.ui.pitch import PitchWidget
from fmxray.ui.table_model import UNCONFIRMED_MARK, format_value
from fmxray.ui.theme import ANIMATION_MS, TOKENS, attribute_band

FIGURE_POINT_SIZE = 20  # CA and PA in the header
_RATED = frozenset(s.name for s in PLAYER_CATALOG.fields if s.unit is Unit.DISPLAY_1_20)


def _shown(group: FieldGroup) -> tuple[str, ...]:
    return tuple(s.name for s in PLAYER_CATALOG.in_group(group) if not s.name.endswith("_raw"))


# Tab title -> (group title, fields) blocks.
_TABS: tuple[tuple[str, tuple[tuple[str, Sequence[str]], ...]], ...] = (
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


def summary_line(values: Mapping[str, object]) -> str:
    """'18 · Club Aurora · DC, DM' with '-' for what is missing."""
    positions = values.get("natural_positions")
    parts = (values.get("age"), values.get("club_name"), positions or None)
    return " · ".join(format_value(part) for part in parts)


class PlayerCard(QWidget):
    def __init__(self, parent: QWidget | None = None, animate: bool = True) -> None:
        super().__init__(parent)
        self._animate = animate
        self._labels: dict[str, QLabel] = {}
        self._groups: dict[str, tuple[QGroupBox, Sequence[str]]] = {}
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.name_label = QLabel(self)
        self.name_label.setProperty("role", "title")
        self.copy_button = QPushButton(icon("copy"), self.tr("Copy"), self)
        self.copy_button.setIconSize(QSize(14, 14))
        self.copy_button.setToolTip(self.tr("Copy the name, to paste it into FM's search"))
        self.copy_button.clicked.connect(self._copy_name)
        top.addWidget(self.name_label, 1)
        top.addWidget(self.copy_button)
        layout.addLayout(top)
        self.summary_label = QLabel(self)
        self.summary_label.setProperty("role", "muted")
        layout.addWidget(self.summary_label)
        figures = QHBoxLayout()
        self.ca_label, self.pa_label = self._figure("CA", figures), self._figure("PA", figures)
        figures.addStretch(1)
        layout.addLayout(figures)

        self.tabs = QTabWidget(self)
        for tab_title, blocks in _TABS:
            page = QWidget()
            grid = QGridLayout(page)
            for column, (title, fields) in enumerate(blocks):
                # Two blocks per row, so a 300px card never clips a column.
                grid.addWidget(self._group(title, fields), column // 2, column % 2)
            if tab_title == "Positions":
                self.pitch = PitchWidget(selectable=False)
                grid.addWidget(self.pitch, 1, 0, 1, 2)
            self.tabs.addTab(page, self.tr(tab_title))
        layout.addWidget(self.tabs, 1)

        self._fade = QGraphicsOpacityEffect(self)
        self._fade.setOpacity(1.0)
        self.setGraphicsEffect(self._fade)
        self._fade_animation = QPropertyAnimation(self._fade, b"opacity", self)
        self._fade_animation.setDuration(ANIMATION_MS)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.clear()

    def _figure(self, caption: str, row: QHBoxLayout) -> QLabel:
        box = QVBoxLayout()
        title = QLabel(caption, self)
        title.setProperty("role", "muted")
        value = QLabel("-", self)
        value.setProperty("role", "figure")
        font = QFont(TOKENS["font_numbers"])
        font.setPointSize(FIGURE_POINT_SIZE)
        font.setWeight(QFont.Weight.DemiBold)
        value.setFont(font)
        box.addWidget(title)
        box.addWidget(value)
        row.addLayout(box)
        row.addSpacing(16)
        return value

    def _group(self, title: str, fields: Sequence[str]) -> QGroupBox:
        box = QGroupBox(self.tr(title), self)
        form = QFormLayout(box)
        for name in fields:
            label = QLabel("-", box)
            label.setProperty("role", "number")
            self._labels[name] = label
            form.addRow(name.replace("_", " "), label)
        self._groups[title] = (box, fields)
        return box

    def field_label(self, name: str) -> QLabel:
        return self._labels[name]

    def group_title(self, title: str) -> str:
        return self._groups[title][0].title()

    def show_player(self, meta: SnapshotMeta, values: Mapping[str, object]) -> None:
        name = values.get("name")
        self.name_label.setText(name if isinstance(name, str) else "-")
        self.copy_button.setEnabled(isinstance(name, str))
        self.summary_label.setText(summary_line(values))
        self.ca_label.setText(format_value(values.get("ca")))
        self.pa_label.setText(format_value(values.get("pa")))
        for field, label in self._labels.items():
            value = values.get(field)
            label.setText(format_value(value))
            band = attribute_band(value) if field in _RATED and isinstance(value, int) else None
            label.setStyleSheet(f"color: {TOKENS[band]};" if band else "")
        for title, (box, fields) in self._groups.items():
            unconfirmed = any(meta.provenance.get(f) is Provenance.UNCONFIRMED for f in fields)
            box.setTitle(self.tr(title) + (UNCONFIRMED_MARK if unconfirmed else ""))
            box.setToolTip(self.tr("unconfirmed fields") if unconfirmed else "")
        ratings = {}
        for code in POSITIONS:
            rating = values.get(f"pos_{code}")
            ratings[code] = rating if isinstance(rating, int) else None
        self.pitch.set_ratings(ratings)
        if self._animate:
            self._fade_animation.stop()
            self._fade_animation.setStartValue(0.35)
            self._fade_animation.setEndValue(1.0)
            self._fade_animation.start()

    def clear(self) -> None:
        self.name_label.setText("")
        self.copy_button.setEnabled(False)
        self.summary_label.setText("")
        self.ca_label.setText("-")
        self.pa_label.setText("-")
        for label in self._labels.values():
            label.setText("-")
            label.setStyleSheet("")
        self.pitch.set_ratings({})

    def _copy_name(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.name_label.text())
