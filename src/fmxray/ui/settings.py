"""Interface preferences remembered between runs."""

from PySide6.QtCore import QSettings

from fmxray.ui.theme import Density


class UiSettings:
    def __init__(self, store: QSettings) -> None:
        self._store = store

    @property
    def density(self) -> Density:
        try:
            return Density(str(self._store.value("density", Density.MEDIUM.value)))
        except ValueError:
            return Density.MEDIUM

    @density.setter
    def density(self, value: Density) -> None:
        self._store.setValue("density", value.value)
        self._store.sync()

    @property
    def sidebar_open(self) -> bool:
        # .ini files give strings back: only an explicit "true" opens the sidebar.
        return str(self._store.value("sidebar_open", "false")).lower() == "true"

    @sidebar_open.setter
    def sidebar_open(self, value: bool) -> None:
        self._store.setValue("sidebar_open", "true" if value else "false")
        self._store.sync()
