from datetime import date

import pytest

from fmxray.domain.search.errors import SpecFormatError
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
    fields_in,
    from_json,
    to_json,
)


def test_json_roundtrip() -> None:
    spec = Or(
        (
            And(
                (Comparison("age", Op.LT, 22), Comparison("contract_end", Op.LE, date(2027, 6, 30)))
            ),
            Not(TextContains("club_name", "roma")),
            IsNone("transfer_value"),
            ListContains("traits", "dictates_tempo"),
            Comparison("free_agent", Op.EQ, True),
            Comparison("pa", Op.GE, 180.5),
            MatchAll(),
        )
    )
    assert from_json(to_json(spec)) == spec


def test_unknown_version_raises() -> None:
    with pytest.raises(SpecFormatError):
        from_json({"version": 99, "root": {"type": "match_all"}})


def test_malformed_json_raises() -> None:
    with pytest.raises(SpecFormatError):
        from_json({"version": 1, "root": {"type": "nope"}})
    with pytest.raises(SpecFormatError):
        from_json({"version": 1})


def test_fields_in() -> None:
    spec = And((Comparison("age", Op.LT, 22), Not(TextContains("club_name", "roma"))))
    assert fields_in(spec) == {"age", "club_name"}
