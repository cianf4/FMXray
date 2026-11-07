from datetime import date

from PySide6.QtWidgets import QComboBox, QLineEdit
from pytestqt.qtbot import QtBot

from fmxray.application.filter_layout import FILTER_TABS
from fmxray.application.filters import EMPTY, FilterState, Range
from fmxray.ui.filters_dialog import FiltersDialog
from fmxray.ui.pitch import PitchWidget
from fmxray.ui.range_slider import RangeControl


def _dialog(qtbot: QtBot) -> FiltersDialog:
    dialog = FiltersDialog()
    qtbot.addWidget(dialog)
    return dialog


def test_one_tab_per_filter_tab(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    titles = [dialog.tabs.tabText(i) for i in range(dialog.tabs.count())]
    assert titles == [tab.title for tab in FILTER_TABS]


def test_every_field_has_a_control(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    for tab in FILTER_TABS:
        for block in tab.blocks:
            for name in block.fields:
                assert dialog.control(name) is not None, name
    assert isinstance(dialog.control("pos_dc"), PitchWidget)


def test_slider_emits_state(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    control = dialog.control("determination")
    assert isinstance(control, RangeControl)
    with qtbot.waitSignal(dialog.state_changed) as blocker:
        control.set_range(Range(15, None), emit=True)
    state = blocker.args[0]
    assert isinstance(state, FilterState)
    assert state.ranges == {"determination": Range(15, None)}


def test_range_at_bounds_is_no_filter(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    control = dialog.control("determination")
    assert isinstance(control, RangeControl)
    control.set_range(Range(1, 20), emit=True)
    assert dialog.state() == EMPTY


def test_text_range_parses_values(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    control = dialog.control("contract_end")
    assert isinstance(control, RangeControl)
    control.set_range(Range(None, date(2027, 6, 30)), emit=True)
    assert dialog.state().ranges == {"contract_end": Range(None, date(2027, 6, 30))}


def test_set_state_updates_controls(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    state = FilterState(
        ranges={"age": Range(15, 21)},
        flags={"free_agent": True},
        positions={"dc": 18},
        texts={"club_name": "roma"},
    )
    dialog.set_state(state)
    assert dialog.state() == state
    age = dialog.control("age")
    assert isinstance(age, RangeControl) and age.range() == Range(15, 21)
    flag = dialog.control("free_agent")
    assert isinstance(flag, QComboBox) and flag.currentText() == "Yes"
    club = dialog.control("club_name")
    assert isinstance(club, QLineEdit) and club.text() == "roma"
    pitch = dialog.control("pos_dc")
    assert isinstance(pitch, PitchWidget) and pitch.selection() == {"dc": 18}


def test_choices_from_options(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog.set_options("traits", ["dictates_tempo", "moves_into_channels"])
    dialog.set_state(FilterState(choices={"traits": frozenset({"dictates_tempo"})}))
    assert dialog.checked_options("traits") == ["dictates_tempo"]


def test_locked_disables_controls(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog.set_locked(True)
    assert not dialog.tabs.isEnabled()
    assert dialog.lock_label.isVisibleTo(dialog)
    dialog.set_locked(False)
    assert dialog.tabs.isEnabled()


def test_reset_tab(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog.set_state(FilterState(ranges={"age": Range(15, 21), "determination": Range(15, None)}))
    with qtbot.waitSignal(dialog.state_changed):
        dialog.reset_tab("Attributes")
    assert dialog.state() == FilterState(ranges={"age": Range(15, 21)})
    dialog.reset_all()
    assert dialog.state() == EMPTY


def test_counts_label(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog.set_counts(3, 37)
    assert dialog.counts_label.text() == "3 active filters · 37 players"
