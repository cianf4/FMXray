from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st

from fmxray.domain.search.parser import parse
from fmxray.domain.search.printer import to_text
from fmxray.domain.search.spec import (
    And,
    Comparison,
    IsNone,
    ListContains,
    MatchAll,
    Not,
    Op,
    Or,
    Spec,
    TextContains,
    from_json,
    to_json,
)


def test_examples() -> None:
    for query in (
        "age<22 pa>180 (pos:dc or pos:dm) not club:roma",
        'name:"unal celik" contract_end<2027-06-30 free_agent=true',
        "transfer_value:none trait:dictates_tempo natural_positions:amc",
        "not (age<20 or age>30)",
    ):
        spec = parse(query)
        assert parse(to_text(spec)) == spec


def test_match_all_is_empty() -> None:
    assert to_text(MatchAll()) == ""


def test_quotes_rejected() -> None:
    with pytest.raises(ValueError):
        to_text(TextContains("name", 'a"b'))


def test_list_of_ints() -> None:
    spec = parse("second_nation_ids:7")
    assert spec == ListContains("second_nation_ids", 7)
    assert from_json(to_json(spec)) == spec


_SAFE_TEXT = st.text(alphabet="abcdefghij .-'", min_size=1, max_size=8)
_LEAVES: st.SearchStrategy[Spec] = st.one_of(
    st.builds(lambda o, v: Comparison("age", o, v), st.sampled_from(list(Op)), st.integers(-5, 60)),
    st.builds(lambda v: Comparison("height_cm", Op.GE, v), st.integers(150, 210)),
    st.builds(
        lambda o, d: Comparison("contract_end", o, d),
        st.sampled_from(list(Op)),
        st.dates(date(2000, 1, 1), date(2040, 1, 1)),
    ),
    st.builds(lambda b: Comparison("free_agent", Op.EQ, b), st.booleans()),
    st.builds(lambda t: Comparison("club_name", Op.EQ, t), _SAFE_TEXT),
    st.builds(lambda t: TextContains("name", t), _SAFE_TEXT),
    st.builds(lambda t: ListContains("traits", t), st.sampled_from(["dictates_tempo", "x_y"])),
    st.builds(lambda c: ListContains("natural_positions", c), st.sampled_from(["DC", "AMC"])),
    st.builds(lambda n: ListContains("second_nation_ids", n), st.integers(0, 300)),
    st.sampled_from([IsNone("transfer_value"), IsNone("club_name")]),
)


def _normalised(children: list[Spec], kind: type[And] | type[Or]) -> Spec:
    flat: list[Spec] = []
    for child in children:
        flat.extend(child.children if isinstance(child, kind) else (child,))
    return kind(tuple(flat))


_TREES = st.recursive(
    _LEAVES,
    lambda inner: st.one_of(
        st.builds(lambda c: _normalised(c, And), st.lists(inner, min_size=2, max_size=3)),
        st.builds(lambda c: _normalised(c, Or), st.lists(inner, min_size=2, max_size=3)),
        st.builds(Not, inner),
    ),
    max_leaves=8,
)


@given(_TREES)
def test_roundtrip(spec: Spec) -> None:
    assert parse(to_text(spec)) == spec
