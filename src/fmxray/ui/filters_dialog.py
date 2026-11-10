"""The "All filters" window: one tab per FilterTab, one box per FilterBlock."""

from collections.abc import Sequence

import polars as pl
from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from fmxray.application.filter_layout import FILTER_TABS, ControlKind, FilterTab, control_kind
from fmxray.application.filters import (
    EMPTY,
    FilterState,
    Mode,
    Range,
    with_choices,
    with_flag,
    with_positions,
    with_range,
    with_text,
    without_fields,
)
from fmxray.domain.search.parser import SEARCH_SCHEMA
from fmxray.domain.search.spec import Value
from fmxray.domain.text import humanize
from fmxray.ui.motion import fade_in
from fmxray.ui.pitch import PitchWidget
from fmxray.ui.range_slider import RangeControl

BLOCKS_PER_ROW = 3
_FLAG_TEXTS = ("Any", "Yes", "No")


def _mode_box(parent: QWidget) -> QComboBox:
    box = QComboBox(parent)
    box.addItems([Mode.ANY.value, Mode.ALL.value])
    return box


class FiltersDialog(QDialog):
    state_changed = Signal(object)  # FilterState

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("All filters"))
        self.setModal(False)
        self._state = EMPTY
        self._controls: dict[str, QWidget] = {}
        self._lists: dict[str, QListWidget] = {}
        self._modes: dict[str, QComboBox] = {}
        self._pitch = PitchWidget(selectable=True)
        self._positions_mode = _mode_box(self)

        layout = QVBoxLayout(self)
        self.lock_label = QLabel(self.tr("Advanced filter from the text bar"), self)
        self.lock_label.setProperty("role", "error")
        self.lock_label.hide()
        layout.addWidget(self.lock_label)
        self.tabs = QTabWidget(self)
        for tab in FILTER_TABS:
            self.tabs.addTab(self._tab_page(tab), self.tr(tab.title))
        layout.addWidget(self.tabs, 1)

        bottom = QHBoxLayout()
        self.counts_label = QLabel(self)
        self.counts_label.setProperty("role", "muted")
        reset, close = QPushButton(self.tr("Reset all"), self), QPushButton(self.tr("Close"), self)
        reset.clicked.connect(self.reset_all)
        close.clicked.connect(self.close)
        bottom.addWidget(self.counts_label, 1)
        bottom.addWidget(reset)
        bottom.addWidget(close)
        layout.addLayout(bottom)

        self._pitch.selection_changed.connect(lambda _sel: self._positions_edited())
        self._positions_mode.currentIndexChanged.connect(lambda _i: self._positions_edited())

    # --- building -------------------------------------------------------------------

    def _tab_page(self, tab: FilterTab) -> QWidget:
        page = QWidget()
        grid = QGridLayout(page)
        reset = QPushButton(self.tr("Reset tab"), page)
        reset.clicked.connect(lambda: self.reset_tab(tab.title))
        grid.addWidget(reset, 0, BLOCKS_PER_ROW - 1, Qt.AlignmentFlag.AlignRight)
        for index, block in enumerate(tab.blocks):
            box = QGroupBox(self.tr(block.title), page)
            form = QFormLayout(box)
            if any(f.startswith("pos_") for f in block.fields):
                form.addRow(self._pitch)
                form.addRow(self.tr("Combine"), self._positions_mode)
            for name in block.fields:
                if name.startswith("pos_"):
                    self._controls[name] = self._pitch
                    continue
                form.addRow(humanize(name), self._control(name, box))
            grid.addWidget(box, 1 + index // BLOCKS_PER_ROW, index % BLOCKS_PER_ROW)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        return scroll

    def _control(self, name: str, parent: QWidget) -> QWidget:
        kind = control_kind(name)
        widget: QWidget
        if kind is ControlKind.RANGE:
            ranged = RangeControl(name, parent)
            ranged.range_changed.connect(self._range_edited)
            widget = ranged
        elif kind is ControlKind.TEXT:
            edit = QLineEdit(parent)
            edit.textChanged.connect(
                lambda text, n=name: self._edit(with_text(self._state, n, text))
            )
            widget = edit
        elif kind is ControlKind.FLAG:
            combo = QComboBox(parent)
            combo.addItems([self.tr(t) for t in _FLAG_TEXTS])
            combo.currentIndexChanged.connect(lambda i, n=name: self._flag_edited(n, i))
            widget = combo
        else:  # CHOICE
            widget = QWidget(parent)
            column = QVBoxLayout(widget)
            column.setContentsMargins(0, 0, 0, 0)
            options = QListWidget(widget)
            options.setMaximumHeight(120)
            options.itemChanged.connect(lambda _item, n=name: self._choices_edited(n))
            column.addWidget(options)
            self._lists[name] = options
            if isinstance(SEARCH_SCHEMA[name], pl.List):
                mode = _mode_box(widget)
                mode.currentIndexChanged.connect(lambda _i, n=name: self._choices_edited(n))
                column.addWidget(mode)
                self._modes[name] = mode
        self._controls[name] = widget
        return widget

    # --- edits from the controls ---------------------------------------------------

    def _edit(self, state: FilterState) -> None:
        self._state = state
        self.state_changed.emit(state)

    def _range_edited(self, name: str, value: Range) -> None:
        self._edit(with_range(self._state, name, value))

    def _text_edited(self, name: str, text: str) -> None:
        self._edit(with_text(self._state, name, text))

    def _flag_edited(self, name: str, index: int) -> None:
        self._edit(with_flag(self._state, name, (None, True, False)[index]))

    def _choices_edited(self, name: str) -> None:
        mode = Mode(self._modes[name].currentText()) if name in self._modes else Mode.ANY
        values = frozenset(self.checked_options(name))
        self._edit(with_choices(self._state, name, values, mode))

    def _positions_edited(self) -> None:
        mode = Mode(self._positions_mode.currentText())
        self._edit(with_positions(self._state, self._pitch.selection(), mode))

    # --- public API -----------------------------------------------------------------

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        fade_in(self)

    def choice_fields(self) -> tuple[str, ...]:
        return tuple(self._lists)

    def control(self, name: str) -> QWidget:
        return self._controls[name]

    def state(self) -> FilterState:
        return self._state

    def set_options(self, name: str, values: Sequence[Value]) -> None:
        """Values offered by a choice field (from the snapshot)."""
        options = self._lists[name]
        with QSignalBlocker(options):
            options.clear()
            chosen = self._state.choices.get(name, frozenset())
            for value in values:
                item = QListWidgetItem(
                    humanize(value) if isinstance(value, str) else str(value), options
                )
                item.setData(Qt.ItemDataRole.UserRole, value)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                checked = value in chosen
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def checked_options(self, name: str) -> list[Value]:
        options = self._lists[name]
        items = (options.item(i) for i in range(options.count()))
        checked = Qt.CheckState.Checked
        return [i.data(Qt.ItemDataRole.UserRole) for i in items if i.checkState() == checked]

    def set_state(self, state: FilterState) -> None:
        """Shows `state` in the controls without emitting `state_changed`."""
        self._state = state
        for name, widget in self._controls.items():
            with QSignalBlocker(widget):
                if isinstance(widget, RangeControl):
                    widget.set_range(state.ranges.get(name, Range()))
                elif isinstance(widget, QLineEdit):
                    widget.setText(state.texts.get(name, ""))
                elif isinstance(widget, QComboBox):
                    flag = state.flags.get(name)
                    widget.setCurrentIndex(0 if flag is None else (1 if flag else 2))
        for name in self._lists:
            chosen = sorted(state.choices.get(name, ()), key=str)
            self.set_options(name, list(dict.fromkeys([*self._option_values(name), *chosen])))
            if name in self._modes:
                with QSignalBlocker(self._modes[name]):
                    self._modes[name].setCurrentText(state.choice_modes.get(name, Mode.ANY).value)
        with QSignalBlocker(self._positions_mode):
            self._positions_mode.setCurrentText(state.positions_mode.value)
        self._pitch.set_selection(state.positions)

    def _option_values(self, name: str) -> list[Value]:
        options = self._lists[name]
        return [options.item(i).data(Qt.ItemDataRole.UserRole) for i in range(options.count())]

    def set_locked(self, locked: bool) -> None:
        self.tabs.setEnabled(not locked)
        self.lock_label.setVisible(locked)

    def set_counts(self, active: int, players: int) -> None:
        text = self.tr("%1 active filters · %2 players")
        self.counts_label.setText(text.replace("%1", str(active)).replace("%2", str(players)))

    def reset_tab(self, title: str) -> None:
        tab = next(t for t in FILTER_TABS if t.title == title)
        names = frozenset(f for block in tab.blocks for f in block.fields)
        state = without_fields(self._state, names)
        self.set_state(state)
        self._edit(state)

    def reset_all(self) -> None:
        self.set_state(EMPTY)
        self._edit(EMPTY)
