"""Starts the Qt application."""

from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from fmxray.application.app import App
from fmxray.application.session import BrowseSession
from fmxray.ui.main_window import MainWindow
from fmxray.ui.theme import load_fonts, stylesheet


def run_gui(app: App, argv: Sequence[str]) -> int:
    qt_app = QApplication(list(argv))
    qt_app.setApplicationName("FM X-Ray")
    load_fonts()  # before the style sheet, so it can name the bundled faces
    qt_app.setStyleSheet(stylesheet())
    window = MainWindow(app, BrowseSession(app))
    window.show()
    return qt_app.exec()
