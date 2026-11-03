"""How fmsave's flat player columns map onto the FM X-Ray player catalog."""

from collections.abc import Mapping, Sequence
from typing import Any

import polars as pl

from fmxray.domain.fields import (
    ATTRIBUTES,
    PERSONALITY,
    PLAYER_CATALOG,
    POSITIONS,
    RELEASE_CLAUSES,
)

_PLAIN = (
    "uid", "unique_id", "name", "full_name", "birth_date", "age", "height_cm", "nation_id",
    "second_nation_ids", "club_uid", "club_name", "club_reputation", "reputation_current",
    "reputation_home", "reputation_world", "left_foot", "right_foot", "natural_positions",
    "accomplished_positions", "transfer_value", "transfer_value_state", "contract_wage",
    "contract_start", "contract_end", "contract_squad_status", "on_loan",
    "loan_parent_club_uid", "loan_parent_club_name", "loan_end", "traits",
)  # fmt: skip

# Our column -> fmsave flat column (as produced by `Table.to_columns()`).
COLUMN_MAP: Mapping[str, str] = {
    **{name: name for name in _PLAIN},
    "ca": "ability_current",
    "pa": "ability_potential",
    "left_foot_raw": "raw_left_foot",
    "right_foot_raw": "raw_right_foot",
    "condition_raw": "raw_condition",
    "match_sharpness_raw": "raw_match_sharpness",
    **{a: f"attributes_{a}" for a in ATTRIBUTES},
    **{f"{a}_raw": f"raw_attributes_{a}" for a in ATTRIBUTES},
    **{p: f"personality_{p}" for p in PERSONALITY},
    **{f"pos_{code}": f"positions_{code}" for code in POSITIONS},
}

_NESTED_PREFIXES = (
    "raw_attributes", "attributes", "ability", "personality", "positions", "reputation",
    "contract",
)  # fmt: skip


def _field_path(flat: str) -> str:
    """fmsave flat column -> dotted path understood by `fmsave.field_status`."""
    for prefix in _NESTED_PREFIXES:
        if flat.startswith(prefix + "_"):
            return f"{prefix}.{flat.removeprefix(prefix + '_')}"
    return flat


# Our column -> path for `fmsave.field_status(fmsave.Player, path)`.
FIELD_PATHS: Mapping[str, str] = {ours: _field_path(flat) for ours, flat in COLUMN_MAP.items()}


def _release_fee(clauses: Sequence[Mapping[str, Any]] | None, kind: str) -> object:
    for clause in clauses or ():
        if clause.get("kind") == kind:
            return clause.get("value")
    return None


def to_frame(columns: Mapping[str, Sequence[object]]) -> pl.DataFrame:
    """Select, rename and type fmsave's flat columns into a catalog-shaped DataFrame."""
    schema = PLAYER_CATALOG.polars_schema()
    clauses: Sequence[Any] = columns["contract_clauses"]
    data: dict[str, list[object]] = {}
    for name, dtype in schema.items():
        if name in RELEASE_CLAUSES:
            data[name] = [_release_fee(c, RELEASE_CLAUSES[name]) for c in clauses]
        elif isinstance(dtype, pl.List):
            data[name] = [None if v is None else list(v) for v in columns[COLUMN_MAP[name]]]  # type: ignore[call-overload]
        else:
            data[name] = list(columns[COLUMN_MAP[name]])
    return pl.DataFrame(data, schema=schema)
