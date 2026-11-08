from PySide6.QtWidgets import QDialog, QPushButton
from pytestqt.qtbot import QtBot

from fmxray.ui.motion import fade_in, grow_in
from fmxray.ui.theme import ANIMATION_MS


def test_grow_in_ends_unconstrained(qtbot: QtBot) -> None:
    button = QPushButton("age ≤ 21")
    qtbot.addWidget(button)
    animation = grow_in(button)
    assert animation.duration() == ANIMATION_MS and button.maximumWidth() == 0
    qtbot.waitUntil(lambda: button.maximumWidth() > 100_000, timeout=2000)


def test_fade_in_reaches_full_opacity(qtbot: QtBot) -> None:
    dialog = QDialog()
    qtbot.addWidget(dialog)
    animation = fade_in(dialog)
    assert animation.endValue() == 1.0
