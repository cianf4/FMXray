"""Turns a filter tree back into search-bar text: `parse(to_text(spec)) == spec`."""

from datetime import date

from fmxray.domain.search.spec import (
    And,
    Comparison,
    IsNone,
    ListContains,
    MatchAll,
    Not,
    Or,
    Spec,
    TextContains,
    Value,
)


def _value(value: Value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        if '"' in value:
            raise ValueError(f"text values cannot contain quotes: {value!r}")
        return f'"{value}"'
    return repr(value)


def _grouped(spec: Spec) -> str:
    text = to_text(spec)
    return f"({text})" if isinstance(spec, And | Or) else text


def to_text(spec: Spec) -> str:
    match spec:
        case MatchAll():
            return ""
        case Comparison(field=f, op=op, value=v):
            return f"{f}{op}{_value(v)}"
        case IsNone(field=f):
            return f"{f}:none"
        case ListContains(field=f, value=v):
            return f"{f}:{_value(v)}"
        case And(children=c):
            return " ".join(f"({to_text(x)})" if isinstance(x, Or) else to_text(x) for x in c)
        case Or(children=c):
            return " or ".join(to_text(x) for x in c)
        case Not(child=child):
            return f"not {_grouped(child)}"
        case TextContains(field=f, text=t):
            return f"{f}:{_value(t)}"
