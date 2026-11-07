from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from fmxray.domain.search.parser import NATURAL_THRESHOLD, POSITION_THRESHOLD
from fmxray.ui.pitch import PitchWidget


def _pitch(qtbot: QtBot, selectable: bool = True) -> PitchWidget:
    pitch = PitchWidget(selectable=selectable)
    qtbot.addWidget(pitch)
    return pitch


def test_click_adds_natural_position(qtbot: QtBot) -> None:
    pitch = _pitch(qtbot)
    with qtbot.waitSignal(pitch.selection_changed) as blocker:
        qtbot.mouseClick(pitch.button("dc"), Qt.MouseButton.LeftButton)
    assert blocker.args == [{"dc": NATURAL_THRESHOLD}]


def test_second_click_removes(qtbot: QtBot) -> None:
    pitch = _pitch(qtbot)
    qtbot.mouseClick(pitch.button("dc"), Qt.MouseButton.LeftButton)
    qtbot.mouseClick(pitch.button("dc"), Qt.MouseButton.LeftButton)
    assert pitch.selection() == {}


def test_level_menu_sets_accomplished(qtbot: QtBot) -> None:
    pitch = _pitch(qtbot)
    menu = pitch.button("dm").menu()
    assert menu is not None
    accomplished = next(a for a in menu.actions() if a.text().startswith("Accomplished"))
    accomplished.trigger()
    assert pitch.selection() == {"dm": POSITION_THRESHOLD}
    assert "15" in pitch.button("dm").text()


def test_set_selection_shows_thresholds(qtbot: QtBot) -> None:
    pitch = _pitch(qtbot)
    pitch.set_selection({"stc": 12})
    assert pitch.button("stc").isChecked()
    assert pitch.selection() == {"stc": 12}


def test_read_only_ignores_clicks(qtbot: QtBot) -> None:
    pitch = _pitch(qtbot, selectable=False)
    pitch.set_ratings({"dc": 18, "gk": None})
    qtbot.mouseClick(pitch.button("dc"), Qt.MouseButton.LeftButton)
    assert pitch.selection() == {}
    assert "18" in pitch.button("dc").text()
    assert "-" in pitch.button("gk").text()
