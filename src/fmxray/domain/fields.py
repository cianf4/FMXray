"""Catalog of the player columns FM X-Ray stores in a snapshot.

The catalog is the single source of truth for column names, Polars types,
UI groups and units. Provenance is *not* stored here: it depends on the save
(game build, reader version) and travels with each snapshot.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

import polars as pl


class Provenance(StrEnum):
    VERIFIED = "verified"
    UNCONFIRMED = "unconfirmed"
    DERIVED = "derived"
    ESTIMATE = "estimate"


class FieldGroup(StrEnum):
    IDENTITY = "identity"
    NATIONALITY = "nationality"
    CLUB = "club"
    ABILITY = "ability"
    REPUTATION = "reputation"
    TECHNICAL = "technical"
    MENTAL = "mental"
    PHYSICAL = "physical"
    GOALKEEPING = "goalkeeping"
    HIDDEN = "hidden"
    PERSONALITY = "personality"
    FEET = "feet"
    POSITIONS = "positions"
    CONDITION = "condition"
    VALUE = "value"
    CONTRACT = "contract"
    LOAN = "loan"
    TRAITS = "traits"


class Unit(StrEnum):
    NONE = "none"
    RAW_1_100 = "raw_1_100"
    DISPLAY_1_20 = "display_1_20"
    MONEY_INTERNAL = "money_internal"
    CM = "cm"
    DATE = "date"
    RAW_0_10000 = "raw_0_10000"


@dataclass(frozen=True)
class FieldSpec:
    name: str
    dtype: pl.DataType
    group: FieldGroup
    unit: Unit = Unit.NONE


# The 52 attributes, in fmsave's `Attributes` order.
ATTRIBUTES: tuple[str, ...] = (
    "crossing", "dribbling", "finishing", "heading", "long_shots", "marking",
    "off_the_ball", "passing", "penalty_taking", "tackling", "vision", "handling",
    "aerial_reach", "command_of_area", "communication", "kicking", "throwing",
    "anticipation", "decisions", "one_on_ones", "positioning", "reflexes",
    "first_touch", "technique", "flair", "corners", "teamwork", "work_rate",
    "long_throws", "eccentricity", "rushing_out", "punching", "acceleration",
    "free_kick_taking", "strength", "stamina", "pace", "jumping_reach", "leadership",
    "dirtiness", "balance", "bravery", "consistency", "aggression", "agility",
    "important_matches", "injury_proneness", "versatility", "natural_fitness",
    "determination", "composure", "concentration",
)  # fmt: skip

HIDDEN_ATTRIBUTES: tuple[str, ...] = (
    "dirtiness", "consistency", "important_matches", "injury_proneness", "versatility",
)  # fmt: skip

PERSONALITY: tuple[str, ...] = (
    "adaptability", "ambition", "loyalty", "pressure",
    "professionalism", "sportsmanship", "temperament", "controversy",
)  # fmt: skip

POSITIONS: tuple[str, ...] = (
    "gk", "sw", "dl", "dc", "dr", "dm", "ml", "mc", "mr",
    "aml", "amc", "amr", "stc", "wbl", "wbr",
)  # fmt: skip

# Our column -> fmsave clause `kind`.
RELEASE_CLAUSES: Mapping[str, str] = {
    "release_fee_min": "minimum_fee_release",
    "release_fee_domestic": "minimum_fee_release_domestic",
    "release_fee_foreign": "minimum_fee_release_foreign",
    "release_fee_domestic_higher": "minimum_fee_release_domestic_higher_division",
    "relegation_release_fee": "relegation_release",
    "non_promotion_release_fee": "non_promotion_release",
}

_TECHNICAL = frozenset({
    "corners", "crossing", "dribbling", "finishing", "first_touch", "free_kick_taking",
    "heading", "long_shots", "long_throws", "marking", "passing", "penalty_taking",
    "tackling", "technique",
})  # fmt: skip
_MENTAL = frozenset({
    "aggression", "anticipation", "bravery", "composure", "concentration", "decisions",
    "determination", "flair", "leadership", "off_the_ball", "positioning", "teamwork",
    "vision", "work_rate",
})  # fmt: skip
_PHYSICAL = frozenset({
    "acceleration", "agility", "balance", "jumping_reach", "natural_fitness", "pace",
    "stamina", "strength",
})  # fmt: skip
_GOALKEEPING = frozenset({
    "aerial_reach", "command_of_area", "communication", "eccentricity", "handling",
    "kicking", "one_on_ones", "punching", "reflexes", "rushing_out", "throwing",
})  # fmt: skip


def _attribute_group(name: str) -> FieldGroup:
    if name in HIDDEN_ATTRIBUTES:
        return FieldGroup.HIDDEN
    if name in _TECHNICAL:
        return FieldGroup.TECHNICAL
    if name in _MENTAL:
        return FieldGroup.MENTAL
    if name in _PHYSICAL:
        return FieldGroup.PHYSICAL
    if name in _GOALKEEPING:
        return FieldGroup.GOALKEEPING
    raise ValueError(f"attribute without a group: {name}")


class FieldCatalog:
    def __init__(self, fields: tuple[FieldSpec, ...]) -> None:
        self.fields = fields
        self._by_name = {spec.name: spec for spec in fields}
        if len(self._by_name) != len(fields):
            raise ValueError("duplicate field names in catalog")

    def names(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.fields)

    def get(self, name: str) -> FieldSpec:
        return self._by_name[name]

    def in_group(self, group: FieldGroup) -> tuple[FieldSpec, ...]:
        return tuple(spec for spec in self.fields if spec.group is group)

    def polars_schema(self) -> pl.Schema:
        return pl.Schema({spec.name: spec.dtype for spec in self.fields})


def _build_player_catalog() -> FieldCatalog:
    g, u = FieldGroup, Unit
    i64, i16, text, flag, day = pl.Int64(), pl.Int16(), pl.String(), pl.Boolean(), pl.Date()
    texts, ints = pl.List(pl.String()), pl.List(pl.Int64())
    fields: list[FieldSpec] = [
        FieldSpec("uid", i64, g.IDENTITY),
        FieldSpec("unique_id", i64, g.IDENTITY),
        FieldSpec("name", text, g.IDENTITY),
        FieldSpec("full_name", text, g.IDENTITY),
        FieldSpec("birth_date", day, g.IDENTITY, u.DATE),
        FieldSpec("age", i16, g.IDENTITY),
        FieldSpec("height_cm", i16, g.IDENTITY, u.CM),
        FieldSpec("nation_id", i64, g.NATIONALITY),
        FieldSpec("second_nation_ids", ints, g.NATIONALITY),
        FieldSpec("club_uid", i64, g.CLUB),
        FieldSpec("club_name", text, g.CLUB),
        FieldSpec("club_reputation", i64, g.CLUB),
        FieldSpec("ca", i16, g.ABILITY),
        FieldSpec("pa", i16, g.ABILITY),
        FieldSpec("reputation_current", i64, g.REPUTATION),
        FieldSpec("reputation_home", i64, g.REPUTATION),
        FieldSpec("reputation_world", i64, g.REPUTATION),
    ]
    for attribute in ATTRIBUTES:
        group = _attribute_group(attribute)
        fields.append(FieldSpec(attribute, i16, group, u.DISPLAY_1_20))
        fields.append(FieldSpec(f"{attribute}_raw", i16, group, u.RAW_1_100))
    fields += [FieldSpec(trait, i16, g.PERSONALITY, u.DISPLAY_1_20) for trait in PERSONALITY]
    fields += [
        FieldSpec("left_foot", i16, g.FEET, u.DISPLAY_1_20),
        FieldSpec("right_foot", i16, g.FEET, u.DISPLAY_1_20),
        FieldSpec("left_foot_raw", i16, g.FEET, u.RAW_1_100),
        FieldSpec("right_foot_raw", i16, g.FEET, u.RAW_1_100),
        FieldSpec("natural_positions", texts, g.POSITIONS),
        FieldSpec("accomplished_positions", texts, g.POSITIONS),
    ]
    fields += [FieldSpec(f"pos_{code}", i16, g.POSITIONS, u.DISPLAY_1_20) for code in POSITIONS]
    fields += [
        FieldSpec("condition_raw", i16, g.CONDITION, u.RAW_0_10000),
        FieldSpec("match_sharpness_raw", i16, g.CONDITION, u.RAW_0_10000),
        FieldSpec("transfer_value", i64, g.VALUE, u.MONEY_INTERNAL),
        FieldSpec("transfer_value_state", text, g.VALUE),
        FieldSpec("contract_wage", i64, g.CONTRACT, u.MONEY_INTERNAL),
        FieldSpec("contract_start", day, g.CONTRACT, u.DATE),
        FieldSpec("contract_end", day, g.CONTRACT, u.DATE),
        FieldSpec("contract_squad_status", text, g.CONTRACT),
    ]
    fields += [FieldSpec(name, i64, g.CONTRACT, u.MONEY_INTERNAL) for name in RELEASE_CLAUSES]
    fields += [
        FieldSpec("on_loan", flag, g.LOAN),
        FieldSpec("loan_parent_club_uid", i64, g.LOAN),
        FieldSpec("loan_parent_club_name", text, g.LOAN),
        FieldSpec("loan_end", day, g.LOAN, u.DATE),
        FieldSpec("traits", texts, g.TRAITS),
    ]
    return FieldCatalog(tuple(fields))


PLAYER_CATALOG: FieldCatalog = _build_player_catalog()
