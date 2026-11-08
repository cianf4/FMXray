"""Saved searches in a narrow rail that opens into a list; the "new" total stays visible."""

from collections.abc import Sequence
from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSignalBlocker, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from fmxray.ui.icons import icon
from fmxray.ui.theme import ANIMATION_MS

SIDEBAR_CLOSED_PX = 44
SIDEBAR_OPEN_PX = 220


@dataclass(frozen=True)
class SavedEntry:
    name: str
    query_text: str
    new: int  # players new since the previous snapshot


class SavedSidebar(QWidget):
    search_chosen = Signal(str)
    toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("savedSidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._open = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 10, 6, 10)
        self.toggle_button = QToolButton(self)
        self.toggle_button.setIcon(icon("saved"))
        self.toggle_button.setIconSize(QSize(18, 18))
        self.toggle_button.setToolTip(self.tr("Saved searches"))
        self.toggle_button.clicked.connect(lambda: self.set_open(not self._open))
        self.badge = QLabel(self)
        self.badge.setProperty("role", "badge")
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list = QListWidget(self)
        self.list.currentItemChanged.connect(self._chosen)
        layout.addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.list, 1)
        self._animation = QPropertyAnimation(self, b"maximumWidth", self)
        self._animation.setDuration(ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._apply(SIDEBAR_CLOSED_PX)

    def set_entries(self, entries: Sequence[SavedEntry]) -> None:
        with QSignalBlocker(self.list):
            self.list.clear()
            for entry in entries:
                text = entry.name + (f"  +{entry.new}" if entry.new else "")
                item = QListWidgetItem(text, self.list)
                item.setData(Qt.ItemDataRole.UserRole, entry.name)
                item.setToolTip(entry.query_text)
        total = sum(entry.new for entry in entries)
        self.badge.setText(f"+{total}" if total else "")
        self.badge.setToolTip(self.tr("New players in your saved searches"))
        self.badge.setVisible(bool(total))

    def badge_text(self) -> str:
        return self.badge.text()

    def is_open(self) -> bool:
        return self._open

    def set_open(self, open_: bool, animate: bool = True) -> None:
        self._open = open_
        self.list.setVisible(open_)
        target = SIDEBAR_OPEN_PX if open_ else SIDEBAR_CLOSED_PX
        if animate:
            self._animation.stop()
            self._animation.setStartValue(self.maximumWidth())
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self._apply(target)
        self.toggled.emit(open_)

    def _apply(self, width: int) -> None:
        self.setMinimumWidth(SIDEBAR_CLOSED_PX)
        self.setMaximumWidth(width)

    def _chosen(self, item: QListWidgetItem | None) -> None:
        if item is not None:
            self.search_chosen.emit(item.data(Qt.ItemDataRole.UserRole))
