from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from fmxray.ui.saved_sidebar import SIDEBAR_CLOSED_PX, SIDEBAR_OPEN_PX, SavedEntry, SavedSidebar

_ENTRIES = [
    SavedEntry("wonderkids", "age<22 pa>180", 3),
    SavedEntry("free agents", "free_agent=true", 1),
]


def _sidebar(qtbot: QtBot) -> SavedSidebar:
    host = QWidget()
    host.resize(600, 500)
    qtbot.addWidget(host)
    sidebar = SavedSidebar(host, host)
    sidebar.set_entries(_ENTRIES)
    return sidebar


def test_entries_with_new_counts(qtbot: QtBot) -> None:
    sidebar = _sidebar(qtbot)
    texts = [sidebar.list.item(i).text() for i in range(sidebar.list.count())]
    assert texts[0].startswith("wonderkids") and "+3" in texts[0]


def test_badge_visible_when_closed(qtbot: QtBot) -> None:
    sidebar = _sidebar(qtbot)
    sidebar.set_open(False, animate=False)
    assert sidebar.badge_text() == "+4"
    assert sidebar.badge.isVisibleTo(sidebar)
    assert sidebar.panel.isHidden()
    sidebar.set_entries([SavedEntry("quiet", "age<30", 0)])
    assert sidebar.badge_text() == ""


def test_toggle_without_animation(qtbot: QtBot) -> None:
    sidebar = _sidebar(qtbot)
    with qtbot.waitSignal(sidebar.toggled) as blocker:
        sidebar.set_open(True, animate=False)
    assert blocker.args == [True] and sidebar.is_open()
    assert sidebar.panel.width() == SIDEBAR_OPEN_PX
    sidebar.set_open(False, animate=False)
    assert sidebar.panel.isHidden()


def test_sidebar_strip_keeps_width(qtbot: QtBot) -> None:
    sidebar = _sidebar(qtbot)
    sidebar.set_open(True, animate=False)
    assert sidebar.width() == SIDEBAR_CLOSED_PX
    assert not sidebar.panel.isHidden() and sidebar.panel.width() == SIDEBAR_OPEN_PX
    assert sidebar.panel.parent() is sidebar.parent()  # floats over its neighbours


def test_panel_follows_resize(qtbot: QtBot) -> None:
    sidebar = _sidebar(qtbot)
    host = sidebar.parentWidget()
    assert host is not None
    host.show()  # a hidden widget gets its resize event only when shown
    qtbot.waitExposed(host)
    sidebar.set_open(True, animate=False)
    host.resize(600, 300)
    assert sidebar.panel.height() == 300


def test_choosing_emits_name(qtbot: QtBot) -> None:
    sidebar = _sidebar(qtbot)
    sidebar.set_open(True, animate=False)
    with qtbot.waitSignal(sidebar.search_chosen) as blocker:
        sidebar.list.setCurrentRow(1)
    assert blocker.args == ["free agents"]
