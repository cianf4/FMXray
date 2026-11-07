from fmxray.ui.theme import TOKENS, attribute_band, stylesheet


def test_attribute_bands() -> None:
    assert [attribute_band(v) for v in (1, 5, 6, 15, 16, 20)] == [
        "band_1", "band_1", "band_2", "band_3", "band_4", "band_4",
    ]  # fmt: skip
    assert attribute_band(None) is None


def test_stylesheet_uses_tokens() -> None:
    assert TOKENS["background"] in stylesheet()
    changed = {**TOKENS, "background": "#123456"}
    assert "#123456" in stylesheet(changed)
    assert TOKENS["background"] not in stylesheet(changed)
