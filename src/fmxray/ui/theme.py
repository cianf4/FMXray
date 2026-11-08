"""Design tokens and the Qt style sheet built from them.

Every colour, font and spacing of the interface comes from TOKENS, so a new look
(SP3b) replaces this mapping, not the widgets.
"""

from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path
from string import Template

from PySide6.QtGui import QFontDatabase

TOKENS: Mapping[str, str] = {
    # Proposal A "Pitch-side" with C's blue accent, chosen by the user on 2026-11-07.
    "background": "#15181d",
    "surface": "#1d2128",
    "raised": "#252a33",
    "text": "#e8eaee",
    "text_muted": "#9aa3b2",
    "border": "#323843",
    "selection": "#23384a",
    "accent": "#4a8ad6",
    "primary": "#4a8ad6",
    "primary_text": "#ffffff",
    "chip_background": "#233040",
    "chip_text": "#cfe3ff",
    "unconfirmed": "#d9a441",
    "estimate": "#f07070",
    "error": "#f07070",
    "new": "#4a8ad6",
    "band_1": "#d0605a",  # attributes 1-5
    "band_2": "#e3a04b",  # 6-10
    "band_3": "#d9dde4",  # 11-15
    "band_4": "#5ccf8f",  # 16-20
    "font_text": "Figtree",
    "font_numbers": "JetBrains Mono",
    "font_size": "10pt",
    "spacing": "6px",
    "radius": "6px",
    "row_height_medium": "26",
    "row_height_compact": "20",
}

_BANDS = ((5, "band_1"), (10, "band_2"), (15, "band_3"), (20, "band_4"))

_QSS = Template("""
QWidget { background: $background; color: $text; font-family: "$font_text"; font-size: $font_size;
          selection-background-color: $selection; selection-color: $text; }
QWidget#careerBar { background: $surface; border-bottom: 1px solid $border; }
QWidget#savedSidebar { background: $surface; border-right: 1px solid $border; }
QWidget#playerCard, QDialog { background: $surface; }
QToolTip { background: $raised; color: $text; border: 1px solid $border; padding: 4px 8px; }
QMenu { background: $raised; border: 1px solid $border; padding: 4px; }
QMenu::item { padding: 5px 18px; border-radius: $radius; }
QMenu::item:selected { background: $selection; }

QPushButton, QToolButton { background: $raised; color: $text; border: 1px solid $border;
          border-radius: $radius; padding: 5px 12px; }
QPushButton:pressed, QToolButton:pressed, QToolButton:checked { background: $selection;
          border-color: $accent; }
QPushButton:disabled, QToolButton:disabled { color: $text_muted; }
QPushButton[role="primary"] { background: $primary; color: $primary_text; border-color: $primary;
          font-weight: 600; padding: 5px 14px; }
QToolButton[role="chip"] { background: $chip_background; color: $chip_text; border: none;
          border-radius: 12px; padding: 3px 10px; }

QLineEdit, QSpinBox, QDateEdit, QComboBox { background: $surface; color: $text;
          border: 1px solid $border; border-radius: $radius; padding: 4px 8px; }
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border-color: $accent; }
QLineEdit[error="true"] { border-color: $error; }
QComboBox QAbstractItemView { background: $raised; border: 1px solid $border; }

QLabel, QCheckBox, QRadioButton { background: transparent; }
QLabel[role="muted"] { color: $text_muted; }
QLabel[role="figure"] { font-family: "$font_numbers"; font-size: 20pt; font-weight: 600; }
QLabel[role="error"] { color: $error; }
QLabel[role="title"] { font-size: 13pt; font-weight: 600; }
QLabel[role="number"] { font-family: "$font_numbers"; }
QLabel[role="badge"] { background: $new; color: $primary_text; border-radius: 9px;
          padding: 0 6px; font-family: "$font_numbers"; font-weight: 600; }

QTabBar::tab { background: transparent; color: $text_muted; padding: 6px 12px;
          border: none; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: $text; border-bottom-color: $accent; }
QTabBar::tab:hover { color: $text; }
QTabWidget::pane { border: none; border-top: 1px solid $border; }

QTableView { background: $background; border: none; gridline-color: $border; }
QTableView::item { border-bottom: 1px solid $surface; padding: 0 8px; }
QTableView::item:selected { background: $selection; color: $text; }
QHeaderView::section { background: $surface; color: $text_muted; padding: 6px 8px; border: none;
          border-bottom: 1px solid $border; }

QListWidget { background: transparent; border: none; }
QListWidget::item { padding: 6px 8px; border-radius: $radius; }
QListWidget::item:selected { background: $selection; color: $text; }
QGroupBox { border: none; margin-top: 18px; color: $text_muted; }
QGroupBox::title { subcontrol-origin: margin; left: 0; padding: 0; color: $text_muted; }

QScrollBar:vertical { background: $background; width: 10px; margin: 0; }
QScrollBar:horizontal { background: $background; height: 10px; margin: 0; }
QScrollBar::handle { background: $raised; border-radius: 5px; min-height: 24px; min-width: 24px; }
QScrollBar::handle:hover { background: $border; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
""")


def stylesheet(tokens: Mapping[str, str] = TOKENS) -> str:
    return _QSS.substitute(tokens)


def attribute_band(value: int | None) -> str | None:
    """Token name for an attribute on the 1-20 scale."""
    if value is None:
        return None
    return next((band for top, band in _BANDS if value <= top), "band_4")


ANIMATION_MS = 150
FONTS_DIR = Path(__file__).parent / "fonts"
_FONT_FILES = ("Figtree-Variable.ttf", "JetBrainsMono-Variable.ttf")


class Density(StrEnum):
    MEDIUM = "medium"
    COMPACT = "compact"


def row_height(density: Density, tokens: Mapping[str, str] = TOKENS) -> int:
    return int(tokens[f"row_height_{density.value}"])


def load_fonts(folder: Path = FONTS_DIR) -> tuple[str, str]:
    """Registers the bundled faces; a missing file falls back to the system face."""
    fallback = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
    families: list[str] = []
    for name in _FONT_FILES:
        font_id = QFontDatabase.addApplicationFont(str(folder / name))
        found = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
        families.append(found[0] if found else fallback)
    return families[0], families[1]
