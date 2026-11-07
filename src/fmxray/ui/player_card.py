"""Side panel with every field of the selected player."""

from collections.abc import Mapping, Sequence

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from fmxray.domain.fields import PLAYER_CATALOG, POSITIONS, FieldGroup, Provenance
from fmxray.domain.snapshot import SnapshotMeta
from fmxray.ui.pitch import PitchWidget
from fmxray.ui.table_model import UNCONFIRMED_MARK, format_value


def _shown(group: FieldGroup) -> tuple[str, ...]:
    return tuple(s.name for s in PLAYER_CATALOG.in_group(group) if not s.name.endswith("_raw"))


_HEADER = ("age", "club_name", "natural_positions", "ca", "pa")
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


class PlayerCard(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._labels: dict[str, QLabel] = {}
        self._groups: dict[str, tuple[QGroupBox, Sequence[str]]] = {}
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self.name_label = QLabel(self)
        self.name_label.setProperty("role", "title")
        self.copy_button = QPushButton(self.tr("Copy name"), self)
        self.copy_button.setToolTip(self.tr("Copy the name, to paste it into FM's search"))
        self.copy_button.clicked.connect(self._copy_name)
        top.addWidget(self.name_label, 1)
        top.addWidget(self.copy_button)
        layout.addLayout(top)
        header = QFormLayout()
        for name in _HEADER:
            header.addRow(name, self._label(name))
        layout.addLayout(header)

        tabs = QTabWidget(self)
        for tab_title, blocks in _TABS:
            page = QWidget()
            grid = QGridLayout(page)
            for column, (title, fields) in enumerate(blocks):
                grid.addWidget(self._group(title, fields), 0, column)
            if tab_title == "Positions":
                self.pitch = PitchWidget(selectable=False)
                grid.addWidget(self.pitch, 1, 0, 1, max(1, len(blocks)))
            tabs.addTab(page, self.tr(tab_title))
        layout.addWidget(tabs, 1)
        self.clear()

    def _label(self, name: str) -> QLabel:
        label = QLabel("-", self)
        self._labels[name] = label
        return label

    def _group(self, title: str, fields: Sequence[str]) -> QGroupBox:
        box = QGroupBox(self.tr(title), self)
        form = QFormLayout(box)
        for name in fields:
            form.addRow(name.replace("_", " "), self._label(name))
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
        for field, label in self._labels.items():
            label.setText(format_value(values.get(field)))
        for title, (box, fields) in self._groups.items():
            unconfirmed = any(meta.provenance.get(f) is Provenance.UNCONFIRMED for f in fields)
            box.setTitle(self.tr(title) + (UNCONFIRMED_MARK if unconfirmed else ""))
            box.setToolTip(self.tr("unconfirmed fields") if unconfirmed else "")
        ratings = {}
        for code in POSITIONS:
            rating = values.get(f"pos_{code}")
            ratings[code] = rating if isinstance(rating, int) else None
        self.pitch.set_ratings(ratings)

    def clear(self) -> None:
        self.name_label.setText("")
        self.copy_button.setEnabled(False)
        for label in self._labels.values():
            label.setText("-")
        self.pitch.set_ratings({})

    def _copy_name(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.name_label.text())
