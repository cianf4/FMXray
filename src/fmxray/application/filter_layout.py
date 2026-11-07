"""Which fields the filter dialog shows, where, and with which kind of control."""

from dataclasses import dataclass
from enum import StrEnum

import polars as pl

from fmxray.domain.fields import PLAYER_CATALOG, FieldGroup, Unit
from fmxray.domain.search.derived import TEXT_FIELDS
from fmxray.domain.search.parser import SEARCH_SCHEMA


@dataclass(frozen=True)
class FilterBlock:
    title: str
    fields: tuple[str, ...]


@dataclass(frozen=True)
class FilterTab:
    title: str
    blocks: tuple[FilterBlock, ...]


class ControlKind(StrEnum):
    RANGE = "range"  # numbers and dates: min-max
    TEXT = "text"  # contains, ignoring case and accents
    CHOICE = "choice"  # one or more values from a list
    FLAG = "flag"  # yes / no / don't care
    POSITION = "position"  # the pitch


_SCALAR_CHOICES = frozenset({"nation_id"})
QUICK_FIELDS: tuple[str, ...] = ("age", "ca", "pa")


def _names(group: FieldGroup, raw: bool | None = None) -> tuple[str, ...]:
    names = (spec.name for spec in PLAYER_CATALOG.in_group(group))
    return tuple(n for n in names if raw is None or n.endswith("_raw") == raw)


def _block(group: FieldGroup, raw: bool | None = None, extra: tuple[str, ...] = ()) -> FilterBlock:
    title = group.value.capitalize() + (" (1-100)" if raw else "")
    return FilterBlock(title, _names(group, raw) + extra)


_ATTRIBUTE_GROUPS = (
    FieldGroup.TECHNICAL, FieldGroup.MENTAL, FieldGroup.PHYSICAL, FieldGroup.GOALKEEPING,
)  # fmt: skip

FILTER_TABS: tuple[FilterTab, ...] = (
    FilterTab("General", (
        _block(FieldGroup.IDENTITY), _block(FieldGroup.ABILITY), _block(FieldGroup.NATIONALITY),
        _block(FieldGroup.CLUB, extra=("free_agent",)), _block(FieldGroup.LOAN),
        _block(FieldGroup.REPUTATION), _block(FieldGroup.CONDITION),
    )),
    FilterTab("Positions", (_block(FieldGroup.POSITIONS), _block(FieldGroup.FEET))),
    FilterTab("Attributes", (
        *(_block(g, raw=False) for g in _ATTRIBUTE_GROUPS),
        *(_block(g, raw=True) for g in _ATTRIBUTE_GROUPS),
    )),
    FilterTab("Hidden & personality", (
        _block(FieldGroup.HIDDEN, raw=False), _block(FieldGroup.PERSONALITY),
        _block(FieldGroup.HIDDEN, raw=True),
    )),
    FilterTab("Contract & value", (
        _block(FieldGroup.VALUE), _block(FieldGroup.CONTRACT, extra=("contract_left",)),
    )),
    FilterTab("Traits", (_block(FieldGroup.TRAITS),)),
)  # fmt: skip


def control_kind(field: str) -> ControlKind:
    dtype = SEARCH_SCHEMA[field]
    if field.startswith("pos_"):
        return ControlKind.POSITION
    if isinstance(dtype, pl.Boolean):
        return ControlKind.FLAG
    if field in TEXT_FIELDS:
        return ControlKind.TEXT
    if isinstance(dtype, pl.List) or field in _SCALAR_CHOICES:
        return ControlKind.CHOICE
    return ControlKind.RANGE


def slider_bounds(field: str) -> tuple[int, int] | None:
    """Fixed bounds for sliders; None means spin boxes bounded by the snapshot's values."""
    if field in ("ca", "pa"):
        return (1, 200)
    if field not in PLAYER_CATALOG.names():
        return None
    unit = PLAYER_CATALOG.get(field).unit
    if unit is Unit.DISPLAY_1_20:
        return (1, 20)
    if unit is Unit.RAW_1_100:
        return (1, 100)
    return None
