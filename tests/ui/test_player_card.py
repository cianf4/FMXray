from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtWidgets import QLabel
from pytestqt.qtbot import QtBot

from fmxray.domain.fields import ATTRIBUTES
from fmxray.ui.player_card import PlayerCard
from tests.factories import make_meta, make_player_frame


def _card(qtbot: QtBot) -> PlayerCard:
    card = PlayerCard()
    qtbot.addWidget(card)
    return card


def test_qml_loads(qtbot: QtBot) -> None:
    card = _card(qtbot)
    assert card.view.status() == QQuickWidget.Status.Ready
    assert card.view.errors() == []


def test_copy_name_to_clipboard(qtbot: QtBot) -> None:
    card = _card(qtbot)
    card.show_player(make_meta(), make_player_frame(1).to_dicts()[0])
    card.copy_name()
    clipboard = QGuiApplication.clipboard()
    assert clipboard is not None and clipboard.text() == "Ünal Çelik"


def test_shows_player_without_errors(qtbot: QtBot) -> None:
    card = _card(qtbot)
    card.resize(360, 900)
    card.show()
    qtbot.waitExposed(card)
    card.show_player(make_meta(), make_player_frame(1, finishing=[17]).to_dicts()[0])
    root = card.view.rootObject()
    assert root is not None
    hexagon = root.findChild(QObject, "hexagon")
    assert hexagon is not None
    assert isinstance(hexagon.property("v0"), float)
    card.show_player(
        make_meta(), make_player_frame(1, **{a: [None] for a in ATTRIBUTES}).to_dicts()[0]
    )
    card.clear()
    assert card.view.errors() == []


def test_qml_error_is_shown(qtbot: QtBot) -> None:
    card = PlayerCard(qml=Path("missing.qml"))
    qtbot.addWidget(card)
    labels = card.findChildren(QLabel)
    assert any("missing.qml" in label.text() for label in labels)


def test_no_qml_errors_on_close(qtbot: QtBot, qtlog: Any) -> None:
    card = PlayerCard()
    card.show_player(make_meta(), make_player_frame(1).to_dicts()[0])
    card.show()
    qtbot.waitExposed(card)
    card.close()
    card.deleteLater()
    qtbot.wait(50)
    assert not [r.message for r in qtlog.records if "TypeError" in r.message]
