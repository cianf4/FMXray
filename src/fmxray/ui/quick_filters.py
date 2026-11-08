"""The strip of most-used filters above the table; shares its FilterState with the dialog."""

from dataclasses import replace

from PySide6.QtCore import QSignalBlocker, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QWidget,
    QWidgetAction,
)

from fmxray.application.filter_layout import QUICK_FIELDS
from fmxray.application.filters import (
    EMPTY,
    FilterState,
    Range,
    with_positions,
    with_range,
)
from fmxray.ui.icons import icon
from fmxray.ui.pitch import PitchWidget
from fmxray.ui.range_slider import RangeControl

MIN_ONLY_FIELDS = frozenset({"ca", "pa"})  # the full range is in the dialog
QUICK_EDIT_PX = 64  # free-text boxes (age) stay narrow in the strip


class QuickFilters(QWidget):
    state_changed = Signal(object)  # FilterState
    open_all_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = EMPTY
        self._ranges: dict[str, RangeControl] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # The main way into the filters: first, and styled as the primary action.
        self.all_button = QPushButton(icon("filters", "primary_text"), "", self)
        self.all_button.setProperty("role", "primary")
        self.all_button.setToolTip(self.tr("Every filter, by tab: positions, attributes, hidden…"))
        self.all_button.clicked.connect(self.open_all_requested)
        layout.addWidget(self.all_button)
        for name in QUICK_FIELDS:
            min_only = name in MIN_ONLY_FIELDS
            control = RangeControl(name, self, min_only=min_only)
            control.range_changed.connect(self._range_edited)
            for edit in control.findChildren(QLineEdit):
                edit.setMaximumWidth(QUICK_EDIT_PX)
            title = name.upper() if len(name) == 2 else name.capitalize()
            layout.addWidget(QLabel(f"{title} \u2265" if min_only else title, self))  # ≥
            layout.addWidget(control)
            self._ranges[name] = control

        self.pitch = PitchWidget(selectable=True)
        self.pitch.selection_changed.connect(self._positions_edited)
        positions = QToolButton(self)
        positions.setText(self.tr("Positions"))
        positions.setIcon(icon("positions"))
        positions.setToolButtonStyle(positions.toolButtonStyle().ToolButtonTextBesideIcon)
        positions.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(positions)
        action = QWidgetAction(menu)
        action.setDefaultWidget(self.pitch)
        menu.addAction(action)
        positions.setMenu(menu)
        layout.addWidget(positions)

        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText(self.tr("Name or club"))
        self.name_edit.textChanged.connect(self._name_edited)
        layout.addWidget(self.name_edit, 1)
        self.set_active_count(0)

    def _edit(self, state: FilterState) -> None:
        self._state = state
        self.state_changed.emit(state)

    def _range_edited(self, name: str, value: Range) -> None:
        self._edit(with_range(self._state, name, value))

    def _positions_edited(self, selection: dict[str, int]) -> None:
        self._edit(with_positions(self._state, selection, self._state.positions_mode))

    def _name_edited(self, text: str) -> None:
        self._edit(replace(self._state, name_or_club=text.strip()))

    def range_control(self, name: str) -> RangeControl:
        return self._ranges[name]

    def set_state(self, state: FilterState) -> None:
        """Shows `state` without emitting `state_changed`."""
        self._state = state
        for name, control in self._ranges.items():
            control.set_range(state.ranges.get(name, Range()))
        with QSignalBlocker(self.name_edit):
            self.name_edit.setText(state.name_or_club)
        self.pitch.set_selection(state.positions)

    def set_active_count(self, count: int) -> None:
        text = (
            self.tr("All filters · %1").replace("%1", str(count))
            if count
            else self.tr("All filters")
        )
        self.all_button.setText(text)

    def set_locked(self, locked: bool) -> None:
        for child in (*self._ranges.values(), self.pitch, self.name_edit):
            child.setEnabled(not locked)
