import polars as pl
import pytest

from fmxray.domain.search.compile import to_expr
from fmxray.domain.search.errors import UnknownFieldError
from fmxray.domain.search.spec import (
    And,
    Comparison,
    IsNone,
    ListContains,
    MatchAll,
    Not,
    Op,
    Or,
    TextContains,
)

FRAME = pl.DataFrame(
    {
        "uid": [1, 2, 3, 4],
        "age": [19, 25, 21, 30],
        "pa": [185, 190, 150, 170],
        "club_name": ["A.S. Roma", "Lazio", None, "Roma Wolves"],
        "club_name__folded": ["a.s. roma", "lazio", None, "roma wolves"],
        "transfer_value": [5_000_000, None, 2_000_000, 500_000],
        "traits": [["dictates_tempo"], [], None, ["crosses_early"]],
    }
)


def _uids(spec: object) -> list[int]:
    return FRAME.filter(to_expr(spec, FRAME.schema))["uid"].to_list()  # type: ignore[arg-type]


def test_comparisons() -> None:
    assert _uids(And((Comparison("age", Op.LT, 22), Comparison("pa", Op.GE, 180)))) == [1]


def test_missing_value_excluded_by_comparison() -> None:
    assert _uids(Comparison("transfer_value", Op.GT, 1_000_000)) == [1, 3]


def test_not_includes_missing_values() -> None:
    assert _uids(Not(TextContains("club_name", "roma"))) == [2, 3]


def test_or_and_not() -> None:
    spec = Or(
        (
            Comparison("age", Op.GE, 30),
            And((Comparison("pa", Op.GT, 180), Not(Comparison("age", Op.EQ, 19)))),
        )
    )
    assert _uids(spec) == [2, 4]


def test_list_contains() -> None:
    assert _uids(ListContains("traits", "dictates_tempo")) == [1]


def test_is_none() -> None:
    assert _uids(IsNone("transfer_value")) == [2]
    assert _uids(MatchAll()) == [1, 2, 3, 4]


def test_unknown_field_suggests() -> None:
    schema = pl.Schema({"finishing": pl.Int16()})
    with pytest.raises(UnknownFieldError) as info:
        to_expr(Comparison("finishng", Op.GT, 15), schema)
    assert "finishing" in info.value.suggestions
