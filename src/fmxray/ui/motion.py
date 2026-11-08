"""Light motion, all with Qt's own animation engine and the same short duration."""

from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    QPropertyAnimation,
)
from PySide6.QtWidgets import QWidget

from fmxray.ui.theme import ANIMATION_MS

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
