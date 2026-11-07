"""A pitch with the 15 positions: pick positions for a filter, or show a player's ratings."""

from collections.abc import Mapping

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QInputDialog, QMenu, QToolButton, QWidget

from fmxray.domain.fields import POSITIONS
from fmxray.domain.search.parser import NATURAL_THRESHOLD, POSITION_THRESHOLD

# (row, column) on a 7 x 3 grid, attack at the top.
_PLACES: Mapping[str, tuple[int, int]] = {
    "stc": (0, 1),
    "aml": (1, 0), "amc": (1, 1), "amr": (1, 2),
    "ml": (2, 0), "mc": (2, 1), "mr": (2, 2),
    "wbl": (3, 0), "dm": (3, 1), "wbr": (3, 2),
    "dl": (4, 0), "dc": (4, 1), "dr": (4, 2),
    "sw": (5, 1),
    "gk": (6, 1),
}  # fmt: skip
assert set(_PLACES) == set(POSITIONS)


def position_label(code: str) -> str:
    return "ST" if code == "stc" else code.upper()


class PitchWidget(QWidget):
    selection_changed = Signal(dict)  # position code -> minimum rating

    def __init__(self, selectable: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selectable = selectable
        self._selection: dict[str, int] = {}
        self._buttons: dict[str, QToolButton] = {}
        grid = QGridLayout(self)
        for code, (row, column) in _PLACES.items():
            button = QToolButton(self)
            button.setText(position_label(code))
            button.setMinimumWidth(64)
            if selectable:
                button.setCheckable(True)
                button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
                button.setMenu(self._level_menu(code, button))
                button.clicked.connect(lambda checked, c=code: self._toggled(c, checked))
            grid.addWidget(button, row, column)
            self._buttons[code] = button

    def _level_menu(self, code: str, button: QToolButton) -> QMenu:
        menu = QMenu(button)
        natural = menu.addAction(self.tr("Natural (18+)"))
        natural.triggered.connect(lambda: self._set_level(code, NATURAL_THRESHOLD))
        accomplished = menu.addAction(self.tr("Accomplished (15+)"))
        accomplished.triggered.connect(lambda: self._set_level(code, POSITION_THRESHOLD))
        custom = menu.addAction(self.tr("Custom minimum…"))
        custom.triggered.connect(lambda: self._ask_level(code))
        return menu

    def _ask_level(self, code: str) -> None:
        current = self._selection.get(code, NATURAL_THRESHOLD)
        title, label = self.tr("Minimum rating"), position_label(code)
        value, ok = QInputDialog.getInt(self, title, label, current, 1, 20)
        if ok:
            self._set_level(code, value)

    def _toggled(self, code: str, checked: bool) -> None:
        if checked:
            self._set_level(code, NATURAL_THRESHOLD)
        else:
            self._selection.pop(code, None)
            self._refresh(code)
            self.selection_changed.emit(dict(self._selection))

    def _set_level(self, code: str, threshold: int) -> None:
        self._selection[code] = threshold
        self._refresh(code)
        self.selection_changed.emit(dict(self._selection))

    def _refresh(self, code: str) -> None:
        button = self._buttons[code]
        threshold = self._selection.get(code)
        button.setChecked(threshold is not None)
        suffix = "" if threshold is None else f" ≥{threshold}"
        button.setText(position_label(code) + suffix)

    def button(self, code: str) -> QToolButton:
        return self._buttons[code]

    def selection(self) -> dict[str, int]:
        return dict(self._selection)

    def set_selection(self, thresholds: Mapping[str, int]) -> None:
        """Shows a selection without emitting `selection_changed`."""
        self._selection = dict(thresholds)
        for code in self._buttons:
            self._refresh(code)

    def set_ratings(self, ratings: Mapping[str, int | None]) -> None:
        for code, button in self._buttons.items():
            rating = ratings.get(code)
            button.setText(f"{position_label(code)} {'-' if rating is None else rating}")
