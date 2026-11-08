from pytestqt.qtbot import QtBot

from fmxray.application.filters import Chip
from fmxray.ui.filter_chips import FilterChips


def _chips(qtbot: QtBot) -> FilterChips:
    chips = FilterChips()
    qtbot.addWidget(chips)
    return chips


def test_shows_labels(qtbot: QtBot) -> None:
    chips = _chips(qtbot)
    chips.set_chips([Chip("age", "age ≤ 21"), Chip("pa", "pa ≥ 180")])
    assert chips.labels() == ["age ≤ 21", "pa ≥ 180"]
    chips.set_chips([])
    assert chips.labels() == []


def test_click_remove_emits_key(qtbot: QtBot) -> None:
    chips = _chips(qtbot)
    chips.set_chips([Chip("age", "age ≤ 21"), Chip("pa", "pa ≥ 180")])
    with qtbot.waitSignal(chips.chip_removed) as blocker:
        chips.remove_button("pa").click()
    assert blocker.args == ["pa"]


def test_advanced_chip(qtbot: QtBot) -> None:
    chips = _chips(qtbot)
    chips.set_chips([], advanced="age<22 or ca>150")
    assert chips.labels() == ["Advanced filter"]
    assert chips.remove_button("advanced").toolTip().endswith("age<22 or ca>150")
    with qtbot.waitSignal(chips.advanced_removed):
        chips.remove_button("advanced").click()
