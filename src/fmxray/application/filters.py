"""State of the filter controls, convertible to and from a filter tree."""

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import date
from enum import StrEnum

import polars as pl

from fmxray.application.filter_layout import FILTER_TABS, ControlKind, control_kind
from fmxray.domain.search.parser import SEARCH_SCHEMA
from fmxray.domain.search.spec import (
    And,
    Comparison,
    ListContains,
    MatchAll,
    Op,
    Or,
    Spec,
    TextContains,
    Value,
)
from fmxray.domain.text import fold

_LAYOUT_ORDER = tuple(f for tab in FILTER_TABS for block in tab.blocks for f in block.fields)


class Mode(StrEnum):
    ANY = "any"
    ALL = "all"


@dataclass(frozen=True)
class Range:
    low: Value | None = None  # inclusive
    high: Value | None = None  # inclusive


@dataclass(frozen=True)
class FilterState:
    ranges: Mapping[str, Range] = field(default_factory=dict)
    positions: Mapping[str, int] = field(default_factory=dict)  # "dc" -> minimum rating
    positions_mode: Mode = Mode.ANY
    choices: Mapping[str, frozenset[Value]] = field(default_factory=dict)
    choice_modes: Mapping[str, Mode] = field(default_factory=dict)  # missing = ANY
    flags: Mapping[str, bool] = field(default_factory=dict)
    texts: Mapping[str, str] = field(default_factory=dict)
    name_or_club: str = ""


EMPTY = FilterState()


def active_count(state: FilterState) -> int:
    return (
        len(state.ranges) + bool(state.positions) + len(state.choices) + len(state.flags)
        + len(state.texts) + bool(state.name_or_club)
    )  # fmt: skip


def _combine(kind: type[And] | type[Or], children: list[Spec]) -> list[Spec]:
    """ANY wraps the group in one `Or`; ALL leaves its terms as top-level `And` terms."""
    if kind is Or and len(children) > 1:
        return [Or(tuple(children))]
    return children


def _field_terms(state: FilterState, name: str) -> list[Spec]:
    if name in state.ranges:
        r = state.ranges[name]
        terms: list[Spec] = []
        if r.low is not None:
            terms.append(Comparison(name, Op.GE, r.low))
        if r.high is not None:
            terms.append(Comparison(name, Op.LE, r.high))
        return terms
    if name in state.choices:
        values = sorted(state.choices[name], key=str)
        if isinstance(SEARCH_SCHEMA[name], pl.List):
            mode = state.choice_modes.get(name, Mode.ANY)
            kind = Or if mode is Mode.ANY else And
            return _combine(kind, [ListContains(name, v) for v in values])
        return _combine(Or, [Comparison(name, Op.EQ, v) for v in values])
    if name in state.flags:
        return [Comparison(name, Op.EQ, state.flags[name])]
    if name in state.texts:
        return [TextContains(name, fold(state.texts[name]))]
    code = name.removeprefix("pos_")
    if name.startswith("pos_") and code in state.positions:
        return [Comparison(name, Op.GE, state.positions[code])]
    return []


def to_spec(state: FilterState) -> Spec:
    terms: list[Spec] = []
    if state.name_or_club:
        text = fold(state.name_or_club)
        terms.append(Or((TextContains("name", text), TextContains("club_name", text))))
    positions = [t for n in _LAYOUT_ORDER if n.startswith("pos_") for t in _field_terms(state, n)]
    placed = False
    for name in _LAYOUT_ORDER:
        if not name.startswith("pos_"):
            terms.extend(_field_terms(state, name))
        elif not placed:  # the whole position group goes where the Positions tab is
            terms.extend(_combine(Or if state.positions_mode is Mode.ANY else And, positions))
            placed = True
    if not terms:
        return MatchAll()
    return terms[0] if len(terms) == 1 else And(tuple(terms))


class _Builder:
    """Collects terms into a FilterState; any term it cannot place makes it unrepresentable."""

    def __init__(self) -> None:
        self.ranges: dict[str, Range] = {}
        self.positions: dict[str, int] = {}
        self.choices: dict[str, set[Value]] = {}
        self.list_terms: dict[str, int] = {}  # top-level ListContains per field (ALL mode)
        self.flags: dict[str, bool] = {}
        self.texts: dict[str, str] = {}
        self.name_or_club = ""
        self.top_positions = 0

    def comparison(self, term: Comparison) -> bool:
        name, op, value = term.field, term.op, term.value
        kind = control_kind(name)
        if kind is ControlKind.POSITION:
            if op is not Op.GE or not isinstance(value, int) or isinstance(value, bool):
                return False
            self.positions[name.removeprefix("pos_")] = value
            self.top_positions += 1
            return True
        if kind is ControlKind.FLAG:
            if op is not Op.EQ or not isinstance(value, bool) or name in self.flags:
                return False
            self.flags[name] = value
            return True
        if kind is ControlKind.CHOICE:
            if op is not Op.EQ or name in self.choices:
                return False
            self.choices[name] = {value}
            return True
        if kind is not ControlKind.RANGE:
            return False
        return self._bound(name, op, value)

    def _bound(self, name: str, op: Op, value: Value) -> bool:
        if isinstance(value, int) and not isinstance(value, bool):
            if op is Op.LT:
                op, value = Op.LE, value - 1
            elif op is Op.GT:
                op, value = Op.GE, value + 1
        if not isinstance(value, int | float | date) or isinstance(value, bool):
            return False
        current = self.ranges.get(name, Range())
        if op is Op.EQ and current == Range():
            self.ranges[name] = Range(value, value)
        elif op is Op.GE and current.low is None:
            self.ranges[name] = Range(value, current.high)
        elif op is Op.LE and current.high is None:
            self.ranges[name] = Range(current.low, value)
        else:
            return False
        return True

    def group(self, term: Or) -> bool:
        c = term.children
        match c:
            case (TextContains("name", a), TextContains("club_name", b)) if a == b:
                if self.name_or_club:
                    return False
                self.name_or_club = a
                return True
        if all(isinstance(x, Comparison) and control_kind(x.field) is ControlKind.POSITION
               and x.op is Op.GE for x in c):  # fmt: skip
            if self.positions:
                return False
            for x in c:
                assert isinstance(x, Comparison)
                if not self.comparison(x):
                    return False
            self.top_positions = 0  # an Or group is ANY mode
            return True
        name = c[0].field if isinstance(c[0], ListContains | Comparison) else ""
        if not name or name in self.choices or control_kind(name) is not ControlKind.CHOICE:
            return False
        is_list = isinstance(SEARCH_SCHEMA[name], pl.List)
        values: set[Value] = set()
        for x in c:
            match x:
                case ListContains(field=f, value=v) if f == name and is_list:
                    values.add(v)
                case Comparison(field=f, op=Op.EQ, value=v) if f == name and not is_list:
                    values.add(v)
                case _:
                    return False
        self.choices[name] = values
        return True

    def term(self, term: Spec) -> bool:
        match term:
            case Comparison():
                return self.comparison(term)
            case ListContains(field=name, value=value):
                if control_kind(name) is not ControlKind.CHOICE:
                    return False
                self.choices.setdefault(name, set()).add(value)
                self.list_terms[name] = self.list_terms.get(name, 0) + 1
                return True
            case TextContains(field=name, text=text):
                if name in self.texts:
                    return False
                self.texts[name] = text
                return True
            case Or():
                return self.group(term)
            case _:
                return False

    def state(self) -> FilterState:
        modes = {name: Mode.ALL for name, count in self.list_terms.items() if count > 1}
        return FilterState(
            ranges=self.ranges,
            positions=self.positions,
            positions_mode=Mode.ALL if self.top_positions > 1 else Mode.ANY,
            choices={name: frozenset(values) for name, values in self.choices.items()},
            choice_modes=modes,
            flags=self.flags,
            texts=self.texts,
            name_or_club=self.name_or_club,
        )


def from_spec(spec: Spec) -> FilterState | None:
    """The controls' state for `spec`, or None when the controls cannot show it."""
    if isinstance(spec, MatchAll):
        return EMPTY
    builder = _Builder()
    terms = spec.children if isinstance(spec, And) else (spec,)
    if not all(builder.term(t) for t in terms):
        return None
    return builder.state()


# Small edits used by the filter widgets; each returns a new state.


def with_range(state: FilterState, name: str, value: Range) -> FilterState:
    ranges = dict(state.ranges)
    if value == Range():
        ranges.pop(name, None)
    else:
        ranges[name] = value
    return replace(state, ranges=ranges)


def with_text(state: FilterState, name: str, text: str) -> FilterState:
    texts = dict(state.texts)
    if text.strip():
        texts[name] = text.strip()
    else:
        texts.pop(name, None)
    return replace(state, texts=texts)


def with_flag(state: FilterState, name: str, value: bool | None) -> FilterState:
    flags = dict(state.flags)
    if value is None:
        flags.pop(name, None)
    else:
        flags[name] = value
    return replace(state, flags=flags)


def with_choices(
    state: FilterState, name: str, values: frozenset[Value], mode: Mode = Mode.ANY
) -> FilterState:
    choices, modes = dict(state.choices), dict(state.choice_modes)
    modes.pop(name, None)
    if values:
        choices[name] = values
        if mode is Mode.ALL and len(values) > 1:
            modes[name] = mode
    else:
        choices.pop(name, None)
    return replace(state, choices=choices, choice_modes=modes)


def with_positions(state: FilterState, positions: Mapping[str, int], mode: Mode) -> FilterState:
    return replace(
        state, positions=dict(positions), positions_mode=mode if len(positions) > 1 else Mode.ANY
    )


def without_fields(state: FilterState, names: frozenset[str]) -> FilterState:
    """Clears every filter on `names` (a `pos_*` name clears the positions)."""
    keep = {k: v for k, v in state.ranges.items() if k not in names}
    positions = {} if any(n.startswith("pos_") for n in names) else state.positions
    return FilterState(
        ranges=keep,
        positions=positions,
        positions_mode=state.positions_mode if positions else Mode.ANY,
        choices={k: v for k, v in state.choices.items() if k not in names},
        choice_modes={k: v for k, v in state.choice_modes.items() if k not in names},
        flags={k: v for k, v in state.flags.items() if k not in names},
        texts={k: v for k, v in state.texts.items() if k not in names},
        name_or_club=state.name_or_club,
    )
