from pathlib import Path

from pytestqt.qtbot import QtBot

from fmxray.application.session import BrowseSession
from fmxray.bootstrap import build_app
from fmxray.ui.main_window import MainWindow
from fmxray.ui.theme import stylesheet


def test_main_window_opens(qtbot: QtBot, tmp_path: Path) -> None:
    app = build_app(tmp_path / "data")
    window = MainWindow(app, BrowseSession(app))
    qtbot.addWidget(window)
    window.setStyleSheet(stylesheet())
    window.show()
    assert window.windowTitle() == "FM X-Ray"
