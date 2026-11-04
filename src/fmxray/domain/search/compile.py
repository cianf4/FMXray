"""Compiles a filter tree into a Polars expression."""

import difflib

import polars as pl

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
    Spec,
    TextContains,
)

FOLDED_SUFFIX = "__folded"


def _column(name: str, schema: pl.Schema) -> pl.Expr:
    if name not in schema:
        suggestions = difflib.get_close_matches(name, schema.names(), n=3)
        raise UnknownFieldError(name, tuple(suggestions))
    return pl.col(name)


def _compare(column: pl.Expr, op: Op, value: object) -> pl.Expr:
    match op:
        case Op.LT:
            return column < value
        case Op.LE:
            return column <= value
        case Op.GT:
            return column > value
        case Op.GE:
            return column >= value
        case Op.EQ:
            return column == value
        case Op.NE:
            return column != value


def to_expr(spec: Spec, schema: pl.Schema) -> pl.Expr:
    # Leaves never yield null: a missing value fails the test, so `Not` of it passes.
    match spec:
        case MatchAll():
            return pl.lit(True)
        case Comparison(field=f, op=op, value=v):
            return _compare(_column(f, schema), op, v).fill_null(False)
        case IsNone(field=f):
            return _column(f, schema).is_null()
        case TextContains(field=f, text=t):
            _column(f, schema)
            folded = _column(f + FOLDED_SUFFIX, schema)
            return folded.str.contains(t, literal=True).fill_null(False)
        case ListContains(field=f, value=v):
            return _column(f, schema).list.contains(v).fill_null(False)
        case And(children=c):
            return pl.all_horizontal(*(to_expr(child, schema) for child in c))
        case Or(children=c):
            return pl.any_horizontal(*(to_expr(child, schema) for child in c))
        case Not(child=child):
            return ~to_expr(child, schema)
