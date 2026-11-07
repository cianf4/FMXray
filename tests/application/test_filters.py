from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from fmxray.application.filters import (
    EMPTY,
    FilterState,
    Mode,
    Range,
    active_count,
    from_spec,
    to_spec,
)
from fmxray.domain.search.compile import to_expr
from fmxray.domain.search.derived import prepare_frame
from fmxray.domain.search.parser import parse
from fmxray.domain.search.printer import to_text
from fmxray.domain.search.spec import MatchAll, Value
from tests.factories import make_player_frame


def test_empty_state_matches_all() -> None:
    assert to_spec(EMPTY) == MatchAll()
    assert from_spec(MatchAll()) == EMPTY
    assert active_count(EMPTY) == 0


def test_quick_filters() -> None:
    state = FilterState(
        ranges={"age": Range(15, 21), "pa": Range(180, None)},
        positions={"dc": 18, "dm": 15},
    )
    assert to_spec(state) == parse("age>=15 age<=21 pa>=180 (pos_dc>=18 or pos_dm>=15)")
    assert active_count(state) == 3


def test_positions_all_mode() -> None:
    state = FilterState(positions={"dc": 18, "dm": 15}, positions_mode=Mode.ALL)
    assert to_spec(state) == parse("pos_dc>=18 pos_dm>=15")
    assert from_spec(to_spec(state)) == state


def test_traits_any_and_all() -> None:
    traits = frozenset({"dictates_tempo", "moves_into_channels"})
    any_state = FilterState(choices={"traits": traits})
    assert to_spec(any_state) == parse("trait:dictates_tempo or trait:moves_into_channels")
    all_state = FilterState(choices={"traits": traits}, choice_modes={"traits": Mode.ALL})
    assert to_spec(all_state) == parse("trait:dictates_tempo trait:moves_into_channels")
    assert from_spec(to_spec(all_state)) == all_state


def test_name_or_club() -> None:
    state = FilterState(name_or_club="Çelik")
    assert to_spec(state) == parse('name:"celik" or club_name:"celik"')
    assert from_spec(to_spec(state)) == FilterState(name_or_club="celik")


def test_lt_normalised() -> None:
    state = from_spec(parse("age<22 ca>150 pa=180"))
    assert state is not None
    assert state.ranges == {"age": Range(None, 21), "ca": Range(151, None), "pa": Range(180, 180)}


def test_not_representable() -> None:
    for query in ("age<22 or ca>150", "not club:roma", "transfer_value:none", 'club_name="Roma"'):
        assert from_spec(parse(query)) is None


_FOLDED = st.text(alphabet="abcdefgh ", min_size=1, max_size=6).filter(lambda t: t.strip() == t)


@st.composite
def _states(draw: st.DrawFn) -> FilterState:
    ranges: dict[str, Range] = {}
    bounds: tuple[tuple[str, st.SearchStrategy[Value]], ...] = (
        ("age", st.integers(14, 45)),
        ("transfer_value", st.integers(0, 10**8)),
        ("contract_end", st.dates(date(2026, 1, 1), date(2035, 1, 1))),
    )
    for field, values in bounds:
        low, high = draw(st.one_of(st.none(), values)), draw(st.one_of(st.none(), values))
        if low is not None or high is not None:
            ranges[field] = Range(low, high)
    positions = draw(
        st.dictionaries(st.sampled_from(["gk", "dc", "dm", "amc", "stc"]), st.integers(1, 20))
    )
    traits = draw(st.frozensets(st.sampled_from(["dictates_tempo", "x_y", "z"]), max_size=3))
    choices = {"traits": traits} if traits else {}
    modes = {"traits": Mode.ALL} if len(traits) > 1 and draw(st.booleans()) else {}  # missing = ANY
    flags = draw(st.dictionaries(st.sampled_from(["free_agent", "on_loan"]), st.booleans()))
    texts = draw(st.dictionaries(st.sampled_from(["club_name", "contract_squad_status"]), _FOLDED))
    return FilterState(
        ranges=ranges,
        positions=positions,
        positions_mode=draw(st.sampled_from(list(Mode))) if len(positions) > 1 else Mode.ANY,
        choices=choices,
        choice_modes=modes,
        flags=flags,
        texts=texts,
        name_or_club=draw(st.one_of(st.just(""), _FOLDED)),
    )


@given(_states())
def test_roundtrip(state: FilterState) -> None:
    assert from_spec(to_spec(state)) == state
    assert from_spec(parse(to_text(to_spec(state)))) == state


_FRAME = prepare_frame(make_player_frame(30), date(2026, 9, 12))


@given(_states())
def test_state_and_text_select_same_players(state: FilterState) -> None:
    spec = to_spec(state)
    expected = _FRAME.filter(to_expr(spec, _FRAME.schema))["uid"].to_list()
    via_text = parse(to_text(spec))
    assert _FRAME.filter(to_expr(via_text, _FRAME.schema))["uid"].to_list() == expected


def test_state_edits() -> None:
    from fmxray.application.filters import (
        with_choices,
        with_flag,
        with_positions,
        with_range,
        with_text,
        without_fields,
    )

    state = with_range(EMPTY, "age", Range(15, 21))
    state = with_text(state, "club_name", " roma ")
    state = with_flag(state, "free_agent", True)
    state = with_choices(state, "traits", frozenset({"a", "b"}), Mode.ALL)
    state = with_positions(state, {"dc": 18}, Mode.ALL)
    assert state == FilterState(
        ranges={"age": Range(15, 21)},
        positions={"dc": 18},
        choices={"traits": frozenset({"a", "b"})},
        choice_modes={"traits": Mode.ALL},
        flags={"free_agent": True},
        texts={"club_name": "roma"},
    )
    assert with_range(state, "age", Range()).ranges == {}
    cleared = without_fields(state, frozenset({"traits", "pos_dc", "free_agent"}))
    assert cleared == FilterState(ranges={"age": Range(15, 21)}, texts={"club_name": "roma"})
