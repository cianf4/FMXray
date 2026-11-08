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
    assert card.summary_label.text().startswith("- · ")


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


def test_compact_header(qtbot: QtBot) -> None:
    card = _card(qtbot)
    values = make_player_frame(1, ca=[131], pa=[188], natural_positions=[["DC", "DM"]]).to_dicts()[
        0
    ]
    card.show_player(make_meta(), values)
    assert card.summary_label.text() == f"{values['age']} · {values['club_name']} · DC, DM"
    assert (card.ca_label.text(), card.pa_label.text()) == ("131", "188")


def test_attributes_coloured_by_band(qtbot: QtBot) -> None:
    from fmxray.ui.theme import TOKENS

    card = _card(qtbot)
    card.show_player(make_meta(), make_player_frame(1, finishing=[3], passing=[18]).to_dicts()[0])
    assert TOKENS["band_1"] in card.field_label("finishing").styleSheet()
    assert TOKENS["band_4"] in card.field_label("passing").styleSheet()
    card.clear()
    assert card.field_label("finishing").styleSheet() == ""


def test_attributes_fit_a_narrow_card(qtbot: QtBot) -> None:
    from PySide6.QtCore import QPoint

    card = _card(qtbot)
    card.resize(340, 900)
    card.show()
    card.show_player(make_meta(), make_player_frame(1).to_dicts()[0])
    qtbot.wait(50)
    for name in ("handling", "punching", "acceleration"):
        label = card.field_label(name)
        right = label.mapTo(card, QPoint(label.width(), 0)).x()
        assert right <= card.width(), name
        assert label.width() >= label.fontMetrics().horizontalAdvance(label.text()), name
