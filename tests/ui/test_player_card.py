from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from pytestqt.qtbot import QtBot

from fmxray.domain.fields import ATTRIBUTES, PERSONALITY, Provenance
from fmxray.ui.player_card import PlayerCard
from tests.factories import make_meta, make_player_frame


def _card(qtbot: QtBot) -> PlayerCard:
    card = PlayerCard()
    qtbot.addWidget(card)
    return card


def test_copy_name_to_clipboard(qtbot: QtBot) -> None:
    card = _card(qtbot)
    card.show_player(make_meta(), make_player_frame(1).to_dicts()[0])
    qtbot.mouseClick(card.copy_button, Qt.MouseButton.LeftButton)
    clipboard = QGuiApplication.clipboard()
    assert clipboard is not None and clipboard.text() == "Ünal Çelik"


def test_incomplete_record(qtbot: QtBot) -> None:
    card = _card(qtbot)
    values = make_player_frame(1, name=[None], age=[None]).to_dicts()[0]
    card.show_player(make_meta(), values)
    assert card.name_label.text() == "-"
    assert not card.copy_button.isEnabled()
    assert card.field_label("age").text() == "-"


def test_attribute_tabs_show_all_attributes(qtbot: QtBot) -> None:
    card = _card(qtbot)
    card.show_player(make_meta(), make_player_frame(1, finishing=[17]).to_dicts()[0])
    for name in (*ATTRIBUTES, *PERSONALITY):
        assert card.field_label(name) is not None
    assert card.field_label("finishing").text() == "17"


def test_unconfirmed_group_marked(qtbot: QtBot) -> None:
    card = _card(qtbot)
    card.show_player(make_meta(), make_player_frame(1).to_dicts()[0])
    assert card.group_title("Technical").endswith("ⓘ")
    verified = {name: Provenance.VERIFIED for name in make_meta().provenance}
    card.show_player(make_meta(provenance=verified), make_player_frame(1).to_dicts()[0])
    assert card.group_title("Technical") == "Technical"


def test_clear_empties_card(qtbot: QtBot) -> None:
    card = _card(qtbot)
    card.show_player(make_meta(), make_player_frame(1).to_dicts()[0])
    card.clear()
    assert card.name_label.text() == ""
    assert not card.copy_button.isEnabled()
    assert card.field_label("finishing").text() == "-"
