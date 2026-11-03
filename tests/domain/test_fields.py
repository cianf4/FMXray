import pytest

from fmxray.domain.fields import (
    ATTRIBUTES,
    HIDDEN_ATTRIBUTES,
    PERSONALITY,
    PLAYER_CATALOG,
    RELEASE_CLAUSES,
    FieldGroup,
    Unit,
)


def test_names_are_unique() -> None:
    names = PLAYER_CATALOG.names()
    assert len(set(names)) == len(names)


def test_every_attribute_in_both_scales() -> None:
    assert len(ATTRIBUTES) == 52
    for attribute in ATTRIBUTES:
        assert PLAYER_CATALOG.get(attribute).unit is Unit.DISPLAY_1_20
        assert PLAYER_CATALOG.get(f"{attribute}_raw").unit is Unit.RAW_1_100


def test_thirteen_hidden_values() -> None:
    hidden = {spec.name for spec in PLAYER_CATALOG.in_group(FieldGroup.HIDDEN)}
    assert hidden == {*HIDDEN_ATTRIBUTES, *(f"{a}_raw" for a in HIDDEN_ATTRIBUTES)}
    personality = {spec.name for spec in PLAYER_CATALOG.in_group(FieldGroup.PERSONALITY)}
    assert personality == set(PERSONALITY)
    assert len(HIDDEN_ATTRIBUTES) + len(PERSONALITY) == 13


def test_money_fields_are_internal_units() -> None:
    for name in ("transfer_value", "contract_wage", *RELEASE_CLAUSES):
        assert PLAYER_CATALOG.get(name).unit is Unit.MONEY_INTERNAL


def test_polars_schema_matches_fields() -> None:
    assert list(PLAYER_CATALOG.polars_schema().names()) == list(PLAYER_CATALOG.names())


def test_get_unknown_field_raises() -> None:
    with pytest.raises(KeyError):
        PLAYER_CATALOG.get("nope")
