"""Column views as tabs above the table, like FM's own views; "+" saves the current one."""

from collections.abc import Sequence

from PySide6.QtCore import QSignalBlocker, Signal
from PySide6.QtWidgets import QTabBar, QWidget

from fmxray.application.column_views import ColumnView
from fmxray.domain.search.parser import SEARCH_SCHEMA

CUSTOM_NAME = "Custom"
_PLUS = "+"


def _known(view: ColumnView) -> ColumnView:
    """Drops columns the catalog no longer has (a view saved by an older version)."""
    return ColumnView(view.name, tuple(c for c in view.columns if c in SEARCH_SCHEMA))


class ViewTabs(QTabBar):
    view_chosen = Signal(object)  # ColumnView
    save_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)
        self._views: list[ColumnView] = []
        self._last = 0
        self.currentChanged.connect(self._changed)

    def set_views(self, views: Sequence[ColumnView]) -> None:
        current = self.current_view().name if self._views else None
        with QSignalBlocker(self):
            while self.count():
                self.removeTab(0)
            self._views = [_known(v) for v in views]
            for view in self._views:
                self.addTab(self.tr(view.name))
            plus = self.addTab(_PLUS)
            self.setTabToolTip(plus, self.tr("Save the current columns as a view"))
            names = [v.name for v in self._views]
            self._last = names.index(current) if current in names else 0
            self.setCurrentIndex(self._last)

    def current_view(self) -> ColumnView:
        return self._views[self._last]

    def show_custom(self, view: ColumnView) -> None:
        names = [v.name for v in self._views]
        with QSignalBlocker(self):
            if CUSTOM_NAME in names:
                index = names.index(CUSTOM_NAME)
                self._views[index] = _known(view)
            else:
                index = len(self._views)
                self._views.append(_known(view))
                self.insertTab(index, self.tr(CUSTOM_NAME))
            self._last = index
            self.setCurrentIndex(index)

    def _changed(self, index: int) -> None:
        if index == len(self._views):  # the "+" tab
            with QSignalBlocker(self):
                self.setCurrentIndex(self._last)
            self.save_requested.emit()
            return
        if 0 <= index < len(self._views):
            self._last = index
            self.view_chosen.emit(self._views[index])
