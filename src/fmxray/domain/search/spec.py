"""Filter tree (Composite/Specification) and its versioned JSON form."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any

from fmxray.domain.search.errors import SpecFormatError

SPEC_VERSION = 1


class Op(StrEnum):
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    EQ = "="
    NE = "!="


type Value = int | float | str | bool | date


@dataclass(frozen=True)
class MatchAll:
    pass


@dataclass(frozen=True)
class Comparison:
    field: str
    op: Op
    value: Value


@dataclass(frozen=True)
class IsNone:
    field: str


@dataclass(frozen=True)
class TextContains:
    field: str
    text: str


@dataclass(frozen=True)
class ListContains:
    field: str
    value: str


@dataclass(frozen=True)
class And:
    children: tuple[Spec, ...]


@dataclass(frozen=True)
class Or:
    children: tuple[Spec, ...]


@dataclass(frozen=True)
class Not:
    child: Spec


type Spec = MatchAll | Comparison | IsNone | TextContains | ListContains | And | Or | Not


def fields_in(spec: Spec) -> frozenset[str]:
    match spec:
        case MatchAll():
            return frozenset()
        case Comparison(field=f) | IsNone(field=f) | TextContains(field=f) | ListContains(field=f):
            return frozenset({f})
        case And(children=c) | Or(children=c):
            return frozenset().union(*(fields_in(child) for child in c))
        case Not(child=child):
            return fields_in(child)


def _value_to_json(value: Value) -> object:
    return {"date": value.isoformat()} if isinstance(value, date) else value


def _value_from_json(raw: object) -> Value:
    if isinstance(raw, dict):
        return date.fromisoformat(str(raw["date"]))
    if isinstance(raw, (bool, int, float, str)):
        return raw
    raise SpecFormatError(f"invalid value: {raw!r}")


def _node_to_json(spec: Spec) -> dict[str, object]:
    match spec:
        case MatchAll():
            return {"type": "match_all"}
        case Comparison(field=f, op=op, value=v):
            return {"type": "comparison", "field": f, "op": str(op), "value": _value_to_json(v)}
        case IsNone(field=f):
            return {"type": "is_none", "field": f}
        case TextContains(field=f, text=t):
            return {"type": "text_contains", "field": f, "text": t}
        case ListContains(field=f, value=v):
            return {"type": "list_contains", "field": f, "value": v}
        case And(children=c):
            return {"type": "and", "children": [_node_to_json(x) for x in c]}
        case Or(children=c):
            return {"type": "or", "children": [_node_to_json(x) for x in c]}
        case Not(child=child):
            return {"type": "not", "child": _node_to_json(child)}


def _node_from_json(raw: Any) -> Spec:
    kind = raw["type"]
    if kind == "match_all":
        return MatchAll()
    if kind == "comparison":
        return Comparison(str(raw["field"]), Op(raw["op"]), _value_from_json(raw["value"]))
    if kind == "is_none":
        return IsNone(str(raw["field"]))
    if kind == "text_contains":
        return TextContains(str(raw["field"]), str(raw["text"]))
    if kind == "list_contains":
        return ListContains(str(raw["field"]), str(raw["value"]))
    if kind == "and":
        return And(tuple(_node_from_json(x) for x in raw["children"]))
    if kind == "or":
        return Or(tuple(_node_from_json(x) for x in raw["children"]))
    if kind == "not":
        return Not(_node_from_json(raw["child"]))
    raise SpecFormatError(f"unknown node type: {kind!r}")


def to_json(spec: Spec) -> dict[str, object]:
    return {"version": SPEC_VERSION, "root": _node_to_json(spec)}


def from_json(data: Mapping[str, object]) -> Spec:
    if data.get("version") != SPEC_VERSION:
        raise SpecFormatError(f"unsupported filter version: {data.get('version')!r}")
    try:
        return _node_from_json(data["root"])
    except SpecFormatError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise SpecFormatError(f"malformed filter: {error}") from error
