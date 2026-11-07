"""Starts the Qt application."""

from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from fmxray.application.app import App
from fmxray.application.session import BrowseSession
from fmxray.ui.main_window import MainWindow
from fmxray.ui.theme import stylesheet


def run_gui(app: App, argv: Sequence[str]) -> int:
    qt_app = QApplication(list(argv))
    qt_app.setApplicationName("FM X-Ray")
    qt_app.setStyleSheet(stylesheet())
    window = MainWindow(app, BrowseSession(app))
    window.show()
    return qt_app.exec()
