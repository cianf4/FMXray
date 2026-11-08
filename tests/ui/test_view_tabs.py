from pytestqt.qtbot import QtBot

from fmxray.application.column_views import BUILTIN_VIEWS, ColumnView
from fmxray.ui.view_tabs import ViewTabs

_MINE = ColumnView("My scouting", ("name", "pa", "determination"))


def _tabs(qtbot: QtBot) -> ViewTabs:
    tabs = ViewTabs()
    qtbot.addWidget(tabs)
    tabs.set_views([*BUILTIN_VIEWS, _MINE])
    return tabs


def test_builtin_then_user_then_plus(qtbot: QtBot) -> None:
    tabs = _tabs(qtbot)
    titles = [tabs.tabText(i) for i in range(tabs.count())]
    assert titles == [*(v.name for v in BUILTIN_VIEWS), "My scouting", "+"]
    assert tabs.current_view() == BUILTIN_VIEWS[0]


def test_choosing_emits_view(qtbot: QtBot) -> None:
    tabs = _tabs(qtbot)
    with qtbot.waitSignal(tabs.view_chosen) as blocker:
        tabs.setCurrentIndex(len(BUILTIN_VIEWS))
    assert blocker.args == [_MINE]


def test_plus_requests_save_and_keeps_current(qtbot: QtBot) -> None:
    tabs = _tabs(qtbot)
    tabs.setCurrentIndex(2)
    with qtbot.waitSignal(tabs.save_requested):
        tabs.setCurrentIndex(tabs.count() - 1)
    assert tabs.currentIndex() == 2


def test_unknown_columns_dropped(qtbot: QtBot) -> None:
    tabs = ViewTabs()
    qtbot.addWidget(tabs)
    tabs.set_views([ColumnView("Old", ("name", "gone_field", "pa"))])
    assert tabs.current_view() == ColumnView("Old", ("name", "pa"))


def test_custom_tab(qtbot: QtBot) -> None:
    tabs = _tabs(qtbot)
    custom = ColumnView("Custom", ("name", "ca"))
    tabs.show_custom(custom)
    tabs.show_custom(ColumnView("Custom", ("name", "ca", "pa")))
    titles = [tabs.tabText(i) for i in range(tabs.count())]
    assert titles[-2:] == ["Custom", "+"] and titles.count("Custom") == 1
    assert tabs.current_view() == ColumnView("Custom", ("name", "ca", "pa"))
