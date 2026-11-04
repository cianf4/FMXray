from datetime import date

import polars as pl
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from fmxray.domain.search.compile import to_expr
from fmxray.domain.search.derived import prepare_frame
from fmxray.domain.search.errors import QueryParseError, UnknownFieldError
from fmxray.domain.search.parser import SortKey, parse, parse_sort
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
    from_json,
    to_json,
)
from tests.factories import make_player_frame


def test_space_is_and() -> None:
    assert parse("age<22 pa>180") == And(
        (Comparison("age", Op.LT, 22), Comparison("pa", Op.GT, 180))
    )


def test_spaces_around_operator() -> None:
    assert parse("age < 22") == Comparison("age", Op.LT, 22)


def test_precedence_and_parentheses() -> None:
    assert parse("ca>=140 (pos:stc or pos:amc) not club:roma") == And(
        (
            Comparison("ca", Op.GE, 140),
            Or((Comparison("pos_stc", Op.GE, 15), Comparison("pos_amc", Op.GE, 15))),
            Not(TextContains("club_name", "roma")),
        )
    )
    assert parse("age<22 OR ca>150 AND pa>180") == Or(
        (
            Comparison("age", Op.LT, 22),
            And((Comparison("ca", Op.GT, 150), Comparison("pa", Op.GT, 180))),
        )
    )


def test_position_thresholds() -> None:
    assert parse("pos:dc") == Comparison("pos_dc", Op.GE, 15)
    assert parse("natural:DC") == Comparison("pos_dc", Op.GE, 18)
    with pytest.raises(UnknownFieldError):
        parse("pos:xx")


def test_aliases() -> None:
    assert parse("acc>15 inj<8") == And(
        (Comparison("acceleration", Op.GT, 15), Comparison("injury_proneness", Op.LT, 8))
    )


def test_quoted_and_accented_text() -> None:
    assert parse('club:"A.S. Roma"') == TextContains("club_name", "a.s. roma")
    assert parse('name:"Ünal Çelik"') == TextContains("name", "unal celik")


def test_none_and_trait() -> None:
    assert parse("transfer_value:none trait:Dictates_Tempo") == And(
        (IsNone("transfer_value"), ListContains("traits", "dictates_tempo"))
    )
    assert parse("natural_positions:amc") == ListContains("natural_positions", "AMC")


def test_dates_and_booleans() -> None:
    assert parse("contract_end<2027-06-30 free_agent=true") == And(
        (
            Comparison("contract_end", Op.LT, date(2027, 6, 30)),
            Comparison("free_agent", Op.EQ, True),
        )
    )


def test_empty_query_matches_all() -> None:
    assert parse("") == MatchAll()
    assert parse("   ") == MatchAll()


def test_unknown_field_suggests() -> None:
    with pytest.raises(UnknownFieldError) as error:
        parse("finishng>15")
    assert "finishing" in error.value.suggestions


def test_syntax_error_reports_position() -> None:
    with pytest.raises(QueryParseError) as missing_value:
        parse("age<")
    assert missing_value.value.position == 4
    with pytest.raises(QueryParseError) as missing_paren:
        parse("(age<22")
    assert missing_paren.value.position == 7


def test_numeric_operator_on_text_field_rejected() -> None:
    with pytest.raises(QueryParseError):
        parse("club_name>3")
    with pytest.raises(QueryParseError):
        parse("age<abc")


def test_parse_sort() -> None:
    assert parse_sort("ca:desc,pa") == (SortKey("ca", True), SortKey("pa", False))
    with pytest.raises(UnknownFieldError):
        parse_sort("finishng")


_TERMS = st.sampled_from(["age<22", "ca>=110", "pa>150", "pos:dc", "club:club_name-1", "age=5"])


def _queries() -> st.SearchStrategy[str]:
    return st.recursive(
        _TERMS,
        lambda inner: st.one_of(
            st.builds(lambda a, b: f"{a} {b}", inner, inner),
            st.builds(lambda a, b: f"({a} or {b})", inner, inner),
            st.builds(lambda a: f"not {a}", inner),
        ),
        max_leaves=6,
    )


_FRAME = prepare_frame(make_player_frame(30), date(2026, 9, 12))


@settings(max_examples=60)
@given(_queries())
def test_text_and_json_agree(query: str) -> None:
    spec = parse(query)
    via_json = from_json(to_json(spec))
    expected = _FRAME.filter(to_expr(spec, _FRAME.schema))["uid"].to_list()
    assert _FRAME.filter(to_expr(via_json, _FRAME.schema))["uid"].to_list() == expected


def test_frame_filters_with_parsed_query() -> None:
    frame = prepare_frame(
        make_player_frame(3, club_name=["A.S. Roma", None, "Lazio"]), date(2026, 9, 12)
    )
    expr = to_expr(parse("not club:roma"), frame.schema)
    assert frame.filter(expr)["uid"].to_list() == [1001, 1002]
    assert isinstance(frame.schema["uid"], pl.Int64)
