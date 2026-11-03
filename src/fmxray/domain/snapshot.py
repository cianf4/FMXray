"""A snapshot: one read of a save, immutable once built."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime

import polars as pl

from fmxray.domain.errors import SchemaMismatchError
from fmxray.domain.fields import PLAYER_CATALOG, FieldCatalog, Provenance


@dataclass(frozen=True)
class SnapshotMeta:
    snapshot_id: str
    career_id: int
    game: str
    build: str
    known_build: bool
    db_version: str
    game_date: date | None
    imported_at: datetime
    source_sha256: str
    source_kind: str
    reader_version: str
    row_count: int
    provenance: Mapping[str, Provenance]
    warnings: tuple[str, ...]


def validate_frame(frame: pl.DataFrame, catalog: FieldCatalog) -> None:
    expected = catalog.polars_schema()
    actual = frame.schema
    if list(actual.items()) == list(expected.items()):
        return
    missing = [name for name in expected if name not in actual]
    extra = [name for name in actual if name not in expected]
    wrong = [
        f"{name} ({actual[name]} != {dtype})"
        for name, dtype in expected.items()
        if name in actual and actual[name] != dtype
    ]
    problems = [
        f"missing: {', '.join(missing)}" if missing else "",
        f"extra: {', '.join(extra)}" if extra else "",
        f"wrong type: {', '.join(wrong)}" if wrong else "",
    ]
    detail = "; ".join(p for p in problems if p) or "column order differs"
    raise SchemaMismatchError(f"frame does not match catalog: {detail}")


@dataclass(frozen=True)
class Snapshot:
    meta: SnapshotMeta
    frame: pl.DataFrame

    def __post_init__(self) -> None:
        validate_frame(self.frame, PLAYER_CATALOG)
        if self.meta.row_count != self.frame.height:
            raise ValueError(f"row_count {self.meta.row_count} != frame height {self.frame.height}")
