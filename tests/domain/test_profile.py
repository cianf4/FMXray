from fmxray.domain.fields import ATTRIBUTES
from fmxray.domain.profile import (
    GOALKEEPER_AREAS,
    OUTFIELD_AREAS,
    profile,
)


def _all(value: int) -> dict[str, object]:
    return dict.fromkeys(ATTRIBUTES, value)


def test_every_area_attribute_exists() -> None:
    for _, names in (*OUTFIELD_AREAS, *GOALKEEPER_AREAS):
        for name in names:
            assert name in ATTRIBUTES, name


def test_outfield_profile() -> None:
    areas = profile({**_all(10), "finishing": 20})
    assert [a.name for a in areas] == [
        "Attack", "Technique", "Creativity", "Defence", "Physical", "Mental",
    ]  # fmt: skip
    assert [a.value for a in areas] == [12.5, 10.0, 10.0, 10.0, 10.0, 10.0]


def test_missing_attributes_skipped() -> None:
    values: dict[str, object] = {**dict.fromkeys(ATTRIBUTES), "finishing": 16, "heading": 12}
    assert profile(values)[0].value == 14.0


def test_no_attributes_gives_none() -> None:
    areas = profile({})
    assert len(areas) == 6
    assert all(a.value is None for a in areas)


def test_goalkeeper_uses_own_areas() -> None:
    areas = profile({**_all(10), "natural_positions": ["GK", "DC"]})
    assert [a.name for a in areas] == [
        "Shot stopping", "Aerial", "Sweeping", "Distribution", "Physical", "Mental",
    ]  # fmt: skip


def test_no_positions_is_outfield() -> None:
    assert profile({"natural_positions": None})[0].name == "Attack"
