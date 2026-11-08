from pathlib import Path

from PySide6.QtCore import QSettings

from fmxray.ui.settings import UiSettings
from fmxray.ui.theme import Density


def _store(tmp_path: Path) -> QSettings:
    return QSettings(str(tmp_path / "ui.ini"), QSettings.Format.IniFormat)


def test_defaults(tmp_path: Path) -> None:
    settings = UiSettings(_store(tmp_path))
    assert settings.density is Density.MEDIUM
    assert settings.sidebar_open is False


def test_roundtrip(tmp_path: Path) -> None:
    settings = UiSettings(_store(tmp_path))
    settings.density = Density.COMPACT
    settings.sidebar_open = True
    again = UiSettings(_store(tmp_path))
    assert again.density is Density.COMPACT
    assert again.sidebar_open is True


def test_bad_values_fall_back(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.setValue("density", "huge")
    store.setValue("sidebar_open", "maybe")
    settings = UiSettings(store)
    assert settings.density is Density.MEDIUM
    assert settings.sidebar_open is False
