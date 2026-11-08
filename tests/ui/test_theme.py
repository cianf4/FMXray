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


def test_row_heights() -> None:
    from fmxray.ui.theme import Density, row_height

    assert row_height(Density.COMPACT) < row_height(Density.MEDIUM)
    assert (row_height(Density.MEDIUM), row_height(Density.COMPACT)) == (26, 20)


def test_new_tokens_present() -> None:
    for key in ("font_text", "font_numbers", "row_height_medium", "row_height_compact",
                "chip_background", "chip_text", "primary", "primary_text"):  # fmt: skip
        assert key in TOKENS, key
    assert TOKENS["primary"] == "#4a8ad6"
