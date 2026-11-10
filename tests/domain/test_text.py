from fmxray.domain.text import fold


def test_fold_strips_accents_and_case() -> None:
    assert fold("Ünal Çelik") == "unal celik"
    assert fold("A.S. Roma") == "a.s. roma"


def test_humanize() -> None:
    from fmxray.domain.text import humanize

    cases = {
        "long_shots": "Long Shots", "off_the_ball": "Off the Ball",
        "command_of_area": "Command of Area", "one_on_ones": "One on Ones",
        "regular_starter": "Regular Starter", "dives_into_tackles": "Dives into Tackles",
        "runs_with_ball_down_left": "Runs with Ball Down Left", "age": "Age",
    }  # fmt: skip
    assert {name: humanize(name) for name in cases} == cases
