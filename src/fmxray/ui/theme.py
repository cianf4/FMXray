"""Design tokens and the Qt style sheet built from them.

Every colour, font and spacing of the interface comes from TOKENS, so a new look
(SP3b) replaces this mapping, not the widgets.
"""

from collections.abc import Mapping
from string import Template

TOKENS: Mapping[str, str] = {
    "background": "#1e1f22",
    "surface": "#2b2d31",
    "text": "#e6e6e6",
    "text_muted": "#b0b0b0",
    "border": "#44464d",
    "selection": "#34404f",
    "accent": "#7aa2f7",
    "unconfirmed": "#e0b060",
    "estimate": "#f07070",
    "error": "#f07070",
    "new": "#7fd17f",
    "band_1": "#c0504d",  # attributes 1-5
    "band_2": "#e0a040",  # 6-10
    "band_3": "#d8d8d8",  # 11-15
    "band_4": "#7fd17f",  # 16-20
    "font_family": "sans-serif",
    "font_size": "10pt",
    "spacing": "6px",
    "radius": "4px",
}

_BANDS = ((5, "band_1"), (10, "band_2"), (15, "band_3"), (20, "band_4"))

_QSS = Template("""
QWidget { background: $background; color: $text; font-family: $font_family;
          font-size: $font_size; }
QTableView, QListWidget, QTabWidget::pane, QGroupBox { background: $surface;
          border: 1px solid $border; border-radius: $radius; }
QTableView { selection-background-color: $selection; gridline-color: $border; }
QHeaderView::section { background: $surface; color: $text_muted; padding: $spacing;
          border: none; border-bottom: 1px solid $border; }
QPushButton, QLineEdit, QSpinBox, QDateEdit, QComboBox { background: $surface;
          border: 1px solid $border; border-radius: $radius; padding: 3px $spacing; }
QPushButton:hover { border-color: $accent; }
QLineEdit[error="true"] { border-color: $error; }
QLabel[role="muted"] { color: $text_muted; }
QLabel[role="error"] { color: $error; }
QTabBar::tab { background: $surface; color: $text_muted; padding: 4px 10px; }
QTabBar::tab:selected { background: $selection; color: $text; }
""")


def stylesheet(tokens: Mapping[str, str] = TOKENS) -> str:
    return _QSS.substitute(tokens)


def attribute_band(value: int | None) -> str | None:
    """Token name for an attribute on the 1-20 scale."""
    if value is None:
        return None
    return next((band for top, band in _BANDS if value <= top), "band_4")
