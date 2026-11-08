from pathlib import Path

from pytestqt.qtbot import QtBot

from fmxray.ui.icons import ICONS, icon
from fmxray.ui.theme import load_fonts


def test_every_icon_exists(qtbot: QtBot) -> None:
    for name in ICONS:
        assert not icon(name).isNull(), name


def test_fonts_load(qtbot: QtBot) -> None:
    assert load_fonts() == ("Figtree", "JetBrains Mono")


def test_missing_font_falls_back(qtbot: QtBot, tmp_path: Path) -> None:
    text, numbers = load_fonts(tmp_path)
    assert text and numbers  # system families, no exception
