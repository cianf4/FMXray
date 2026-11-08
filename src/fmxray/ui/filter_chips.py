"""The active filters as removable chips next to the quick filters."""

from collections.abc import Sequence

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QWidget

from fmxray.application.filters import Chip
from fmxray.ui.icons import icon
from fmxray.ui.motion import grow_in

ADVANCED_KEY = "advanced"


class FilterChips(QWidget):
    chip_removed = Signal(str)  # Chip.key
    advanced_removed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._buttons: dict[str, QToolButton] = {}

    def set_chips(self, chips: Sequence[Chip], advanced: str | None = None) -> None:
        before = set(self._buttons)
        for button in self._buttons.values():
            self._layout.removeWidget(button)
            button.deleteLater()
        self._buttons.clear()
        if advanced is not None:
            self._add(
                ADVANCED_KEY, self.tr("Advanced filter"), self.tr("From the text bar: ") + advanced
            )
        for chip in chips:
            self._add(chip.key, chip.label, self.tr("Remove this filter"))
        for key, button in self._buttons.items():
            if key not in before:  # only chips that just appeared grow in
                grow_in(button)

    def _add(self, key: str, label: str, tooltip: str) -> None:
        button = QToolButton(self)
        button.setProperty("role", "chip")
        button.setText(label)
        button.setToolTip(tooltip)
        button.setIcon(icon("close", "chip_text"))
        button.setIconSize(QSize(12, 12))
        button.setToolButtonStyle(button.toolButtonStyle().ToolButtonTextBesideIcon)
        button.setLayoutDirection(button.layoutDirection().RightToLeft)  # the x after the text
        if key == ADVANCED_KEY:
            button.clicked.connect(self.advanced_removed)
        else:
            button.clicked.connect(lambda: self.chip_removed.emit(key))
        self._layout.addWidget(button)
        self._buttons[key] = button

    def remove_button(self, key: str) -> QToolButton:
        return self._buttons[key]

    def labels(self) -> list[str]:
        return [button.text() for button in self._buttons.values()]
