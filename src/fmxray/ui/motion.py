"""Light motion, all with Qt's own animation engine and the same short duration."""

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPropertyAnimation,
    QVariantAnimation,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from fmxray.ui.theme import ANIMATION_MS, TOKENS

UNCONSTRAINED = 16_777_215  # QWIDGETSIZE_MAX


def _animation(target: QObject, prop: bytes) -> QPropertyAnimation:
    animation = QPropertyAnimation(target, prop, target)
    animation.setDuration(ANIMATION_MS)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    return animation


def grow_in(widget: QWidget) -> QPropertyAnimation:
    """A new chip opens from zero width, then is free to resize."""
    animation = _animation(widget, b"maximumWidth")
    animation.setStartValue(0)
    animation.setEndValue(max(widget.sizeHint().width(), 1))
    animation.finished.connect(lambda: widget.setMaximumWidth(UNCONSTRAINED))
    widget.setMaximumWidth(0)
    animation.start()
    return animation


def fade_in(window: QWidget) -> QPropertyAnimation:
    """A top-level window appears with its opacity rising (no-op where unsupported)."""
    animation = _animation(window, b"windowOpacity")
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.start()
    return animation


class HoverFade(QObject):
    """Tints a button's background towards the border colour while the pointer is over it."""

    def __init__(self, button: QWidget) -> None:
        super().__init__(button)
        self._button = button
        self._rest, self._hover = QColor(TOKENS["raised"]), QColor(TOKENS["border"])
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._paint)
        self._animation.finished.connect(self._settle)
        button.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Enter:
            self._run(self._hover)
        elif event.type() == QEvent.Type.Leave:
            self._run(self._rest)
        return False

    def _run(self, target: QColor) -> None:
        current = self._animation.currentValue()
        self._animation.stop()
        self._animation.setStartValue(current if isinstance(current, QColor) else self._rest)
        self._animation.setEndValue(target)
        self._animation.start()

    def _paint(self, color: object) -> None:
        if isinstance(color, QColor):
            self._button.setStyleSheet(f"background: {color.name()};")

    def _settle(self) -> None:
        if self._animation.endValue() == self._rest:
            self._button.setStyleSheet("")  # back to the theme's style sheet
