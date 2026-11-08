"""Icons: Phosphor (MIT) through QtAwesome, coloured from the theme tokens."""

from collections.abc import Mapping

import qtawesome as qta
from PySide6.QtGui import QIcon

from fmxray.ui.theme import TOKENS

# Our name -> Phosphor name (checked against qtawesome 1.4.2).
ICONS: Mapping[str, str] = {
    "filters": "funnel",
    "copy": "copy",
    "saved": "star",
    "text_bar": "terminal-window",
    "density": "rows",
    "close": "x",
    "add": "plus",
    "import": "download-simple",
    "watch": "eye",
    "positions": "sliders-horizontal",
}


def icon(name: str, color_token: str = "text") -> QIcon:
    result: QIcon = qta.icon("ph." + ICONS[name], color=TOKENS[color_token])
    return result
