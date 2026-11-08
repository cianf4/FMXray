from PySide6.QtGui import QColor

from fmxray.ui.table_delegate import pill_colors
from fmxray.ui.theme import TOKENS


def test_pill_colors() -> None:
    low, high = pill_colors(3), pill_colors(18)
    assert low is not None and low[1] == QColor(TOKENS["band_1"])
    assert high is not None and high[1] == QColor(TOKENS["band_4"])
    assert high[0].alpha() < 255
    for value in (None, "x", 0, 21, True):
        assert pill_colors(value) is None, value
