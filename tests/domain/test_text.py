from fmxray.domain.text import fold


def test_fold_strips_accents_and_case() -> None:
    assert fold("Ünal Çelik") == "unal celik"
    assert fold("A.S. Roma") == "a.s. roma"
