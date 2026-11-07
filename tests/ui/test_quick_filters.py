from pytestqt.qtbot import QtBot

from fmxray.application.filters import FilterState, Range
from fmxray.ui.quick_filters import QuickFilters


def _quick(qtbot: QtBot) -> QuickFilters:
    quick = QuickFilters()
    qtbot.addWidget(quick)
    return quick


def test_age_and_pa(qtbot: QtBot) -> None:
    quick = _quick(qtbot)
    quick.range_control("age").set_range(Range(15, 21), emit=True)
    with qtbot.waitSignal(quick.state_changed) as blocker:
        quick.range_control("pa").set_range(Range(180, None), emit=True)
    assert blocker.args[0] == FilterState(ranges={"age": Range(15, 21), "pa": Range(180, None)})


def test_name_or_club(qtbot: QtBot) -> None:
    quick = _quick(qtbot)
    with qtbot.waitSignal(quick.state_changed) as blocker:
        quick.name_edit.setText("roma")
    assert blocker.args[0] == FilterState(name_or_club="roma")


def test_shared_state_with_dialog(qtbot: QtBot) -> None:
    quick = _quick(qtbot)
    quick.set_state(FilterState(ranges={"ca": Range(140, None)}, positions={"dc": 18}))
    assert quick.range_control("ca").range() == Range(140, None)
    assert quick.pitch.selection() == {"dc": 18}
    quick.set_active_count(4)
    assert "4" in quick.all_button.text()


def test_open_all(qtbot: QtBot) -> None:
    quick = _quick(qtbot)
    with qtbot.waitSignal(quick.open_all_requested):
        quick.all_button.click()
