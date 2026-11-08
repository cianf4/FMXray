"""Saved searches: a narrow rail that opens a floating list; the "new" total stays visible."""

from collections.abc import Sequence
from dataclasses import dataclass

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSignalBlocker,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QFrame,
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
    """A fixed rail in the layout; its list opens as a panel floating over the neighbours.

    The panel lives outside any layout, so opening it never re-lays out the table.
    """

    search_chosen = Signal(str)
    toggled = Signal(bool)

    def __init__(self, overlay_parent: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("savedSidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(SIDEBAR_CLOSED_PX)
        self._open = False
        self._overlay_parent = overlay_parent
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
        layout.addWidget(self.toggle_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)

        self.panel = QFrame(overlay_parent)
        self.panel.setObjectName("savedPanel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(8, 10, 8, 10)
        title = QLabel(self.tr("Saved searches"), self.panel)
        title.setProperty("role", "muted")
        self.list = QListWidget(self.panel)
        self.list.currentItemChanged.connect(self._chosen)
        panel_layout.addWidget(title)
        panel_layout.addWidget(self.list, 1)
        self.panel.hide()
        self._animation = QPropertyAnimation(self.panel, b"geometry", self)
        self._animation.setDuration(ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.finished.connect(self._settled)
        overlay_parent.installEventFilter(self)

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
        self._animation.stop()
        start = self._panel_rect(0) if self.panel.isHidden() else self.panel.geometry()
        target = self._panel_rect(SIDEBAR_OPEN_PX if open_ else 0)
        if open_:
            self.panel.setGeometry(start)
            self.panel.show()
            self.panel.raise_()
        if animate:
            self._animation.setStartValue(start)
            self._animation.setEndValue(target)
            self._animation.start()
        else:
            self.panel.setGeometry(target)
            self._settled()
        self.toggled.emit(open_)

    def _panel_rect(self, width: int) -> QRect:
        top_left = self.mapTo(self._overlay_parent, QPoint(self.width(), 0))
        return QRect(top_left.x(), 0, width, self._overlay_parent.height())

    def _settled(self) -> None:
        if not self._open:
            self.panel.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._overlay_parent and event.type() == QEvent.Type.Resize and self._open:
            self._animation.stop()
            self.panel.setGeometry(self._panel_rect(SIDEBAR_OPEN_PX))
        return False

    def _chosen(self, item: QListWidgetItem | None) -> None:
        if item is not None:
            self.search_chosen.emit(item.data(Qt.ItemDataRole.UserRole))
