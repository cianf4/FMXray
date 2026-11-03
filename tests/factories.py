"""Synthetic test data that always matches the player catalog."""

from datetime import UTC, date, datetime
from typing import Any

import polars as pl

from fmxray.domain.fields import PLAYER_CATALOG, Provenance
from fmxray.domain.snapshot import SnapshotMeta

NAMES = ("Ünal Çelik", "Paulo Dybala", "Mile Svilar")


def _value(dtype: pl.DataType, name: str, row: int) -> object:
    if name == "name" or name == "full_name":
        return NAMES[row % len(NAMES)] + ("" if row < len(NAMES) else f" {row}")
    if name in ("uid", "unique_id"):
        return 1000 + row
    if name in ("ca", "pa"):
        return 100 + row % 100
    if isinstance(dtype, pl.List):
        return []
    if dtype == pl.Boolean():
        return False
    if dtype == pl.Date():
        return date(2000, 1, 1)
    if dtype == pl.String():
        return f"{name}-{row}"
    return 1 + row % 20


def make_player_frame(n: int = 3, **overrides: list[Any]) -> pl.DataFrame:
    schema = PLAYER_CATALOG.polars_schema()
    data = {
        name: overrides.get(name, [_value(dtype, name, row) for row in range(n)])
        for name, dtype in schema.items()
    }
    return pl.DataFrame(data, schema=schema)


def make_meta(**overrides: Any) -> SnapshotMeta:
    values: dict[str, Any] = {
        "snapshot_id": "snap-1",
        "career_id": 1,
        "game": "FM27",
        "build": "27.0.0+2493426",
        "known_build": False,
        "db_version": "27.0.0+0",
        "game_date": date(2026, 9, 12),
        "imported_at": datetime(2026, 11, 3, 12, 0, tzinfo=UTC),
        "source_sha256": "0" * 64,
        "source_kind": "fmsave",
        "reader_version": "0.9.3",
        "row_count": 3,
        "provenance": {name: Provenance.UNCONFIRMED for name in PLAYER_CATALOG.names()},
        "warnings": (),
    }
    values.update(overrides)
    return SnapshotMeta(**values)
