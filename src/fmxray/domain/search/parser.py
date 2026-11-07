"""Text search bar: tokenizer and recursive-descent parser producing a filter tree.

Grammar (keywords are case-insensitive):
    query    := or_expr? EOF
    or_expr  := and_expr ("or" and_expr)*
    and_expr := unary ("and"? unary)*
    unary    := "not" unary | "(" or_expr ")" | term
    term     := NAME OP VALUE | NAME ":" VALUE
"""

import re
from dataclasses import dataclass
from datetime import date

import polars as pl

from fmxray.domain.fields import PLAYER_CATALOG, POSITIONS
from fmxray.domain.search.aliases import resolve_field
from fmxray.domain.search.derived import DERIVED_FIELDS, TEXT_FIELDS
from fmxray.domain.search.errors import QueryParseError
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
    Value,
)
from fmxray.domain.text import fold

SEARCH_SCHEMA = pl.Schema({**PLAYER_CATALOG.polars_schema(), **DERIVED_FIELDS})

POSITION_THRESHOLD = 15  # pos:X — the player can play there
NATURAL_THRESHOLD = 18  # natural:X — the player is natural there
_POSITION_FIELDS = tuple(f"pos_{code}" for code in POSITIONS)
_POSITION_LISTS = frozenset({"natural_positions", "accomplished_positions"})

_TOKEN = re.compile(
    r"\s*(?:(?P<paren>[()])|(?P<op><=|>=|!=|<|>|=)|(?P<colon>:)"
    r'|"(?P<string>[^"]*)"|(?P<word>[^\s()<>=!:"]+))'
)


@dataclass(frozen=True)
class _Token:
    kind: str  # "(", ")", "op", "colon", "string", "word", "eof"
    text: str
    pos: int


def _tokenize(text: str) -> list[_Token]:
    tokens: list[_Token] = []
    index = 0
    while text[index:].strip():
        match = _TOKEN.match(text, index)
        start = len(text) - len(text[index:].lstrip())
        if match is None or match.lastgroup is None:
            raise QueryParseError(f"unexpected character {text[start]!r}", start)
        kind = match.lastgroup
        value = match.group(kind)
        pos = match.start(kind) - (kind == "string")  # point at the opening quote
        tokens.append(_Token(value if kind == "paren" else kind, value, pos))
        index = match.end()
    tokens.append(_Token("eof", "", len(text)))
    return tokens


@dataclass(frozen=True)
class SortKey:
    field: str
    descending: bool


DEFAULT_SORT: tuple[SortKey, ...] = (SortKey("ca", True),)


def _combine(kind: type[And] | type[Or], children: list[Spec]) -> Spec:
    return children[0] if len(children) == 1 else kind(tuple(children))


def _typed_value(field: str, dtype: pl.DataType, token: _Token) -> Value:
    text = token.text
    if isinstance(dtype, pl.String):
        return text
    if isinstance(dtype, pl.Boolean):
        if text.lower() in ("true", "false"):
            return text.lower() == "true"
        raise QueryParseError(f"expected true or false for {field!r}", token.pos)
    if isinstance(dtype, pl.Date):
        try:
            return date.fromisoformat(text)
        except ValueError:
            raise QueryParseError(
                f"expected a date like 2027-06-30 for {field!r}", token.pos
            ) from None
    if dtype.is_numeric():
        try:
            return int(text)
        except ValueError:
            pass
        try:
            return float(text)
        except ValueError:
            raise QueryParseError(f"expected a number for {field!r}", token.pos) from None
    raise QueryParseError(f"{field!r} cannot be compared; use {field}:value", token.pos)


class _Parser:
    def __init__(self, text: str) -> None:
        self._tokens = _tokenize(text)
        self._index = 0

    def _peek(self) -> _Token:
        return self._tokens[self._index]

    def _advance(self) -> _Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _at_keyword(self, keyword: str) -> bool:
        token = self._peek()
        return token.kind == "word" and token.text.lower() == keyword

    def query(self) -> Spec:
        if self._peek().kind == "eof":
            return MatchAll()
        spec = self._or()
        token = self._peek()
        if token.kind != "eof":
            raise QueryParseError(f"unexpected {token.text!r}", token.pos)
        return spec

    def _or(self) -> Spec:
        children = [self._and()]
        while self._at_keyword("or"):
            self._advance()
            children.append(self._and())
        return _combine(Or, children)

    def _and(self) -> Spec:
        children = [self._unary()]
        while True:
            if self._at_keyword("and"):
                self._advance()
            elif not (self._peek().kind in ("(", "word") and not self._at_keyword("or")):
                break
            children.append(self._unary())
        return _combine(And, children)

    def _unary(self) -> Spec:
        if self._at_keyword("not"):
            self._advance()
            return Not(self._unary())
        if self._peek().kind == "(":
            self._advance()
            spec = self._or()
            token = self._peek()
            if token.kind != ")":
                raise QueryParseError("expected ')'", token.pos)
            self._advance()
            return spec
        return self._term()

    def _value(self) -> _Token:
        token = self._peek()
        if token.kind not in ("string", "word"):
            raise QueryParseError("expected a value", token.pos)
        return self._advance()

    def _term(self) -> Spec:
        name = self._peek()
        if name.kind != "word":
            raise QueryParseError("expected a field name", name.pos)
        self._advance()
        token = self._peek()
        if token.kind == "op":
            self._advance()
            return self._comparison(name, token, self._value())
        if token.kind == "colon":
            self._advance()
            return self._colon(name, self._value())
        raise QueryParseError(f"expected an operator or ':' after {name.text!r}", token.pos)

    def _comparison(self, name: _Token, op_token: _Token, value: _Token) -> Spec:
        field = resolve_field(name.text, SEARCH_SCHEMA, name.pos)
        dtype = SEARCH_SCHEMA[field]
        op = Op(op_token.text)
        ordering = op not in (Op.EQ, Op.NE)
        if isinstance(dtype, pl.List) or (isinstance(dtype, pl.String) and ordering):
            raise QueryParseError(
                f"{op_token.text!r} does not apply to {field!r}; use {field}:value", op_token.pos
            )
        return Comparison(field, op, _typed_value(field, dtype, value))

    def _colon(self, name: _Token, value: _Token) -> Spec:
        key, raw = name.text.lower(), value.text
        if key in ("pos", "natural"):
            field = resolve_field(f"pos_{raw.lower()}", _POSITION_FIELDS, value.pos)
            threshold = POSITION_THRESHOLD if key == "pos" else NATURAL_THRESHOLD
            return Comparison(field, Op.GE, threshold)
        if key == "trait":
            return ListContains("traits", raw.lower())
        field = resolve_field(name.text, SEARCH_SCHEMA, name.pos)
        if value.kind == "word" and raw.lower() == "none":
            return IsNone(field)
        if field in TEXT_FIELDS:
            return TextContains(field, fold(raw))
        dtype = SEARCH_SCHEMA[field]
        if isinstance(dtype, pl.List):
            if dtype.inner.is_integer():
                return ListContains(field, _typed_value(field, pl.Int64(), value))
            if not isinstance(dtype.inner, pl.String):
                raise QueryParseError(f"{field!r} cannot be searched by text", value.pos)
            return ListContains(field, raw.upper() if field in _POSITION_LISTS else raw.lower())
        return Comparison(field, Op.EQ, _typed_value(field, dtype, value))


def parse(text: str) -> Spec:
    return _Parser(text).query()


def parse_sort(text: str) -> tuple[SortKey, ...]:
    """Parse `"ca:desc,pa"`; empty text gives the default sort."""
    keys: list[SortKey] = []
    for part in (p.strip() for p in text.split(",")):
        if not part:
            continue
        name, _, direction = part.partition(":")
        if direction.lower() not in ("", "asc", "desc"):
            raise QueryParseError(f"unknown sort direction {direction!r}", text.find(part))
        field = resolve_field(name.strip(), SEARCH_SCHEMA, text.find(part))
        keys.append(SortKey(field, direction.lower() == "desc"))
    return tuple(keys) or DEFAULT_SORT
