"""Ports: what the application needs from the outside world."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Protocol

import polars as pl

from fmxray.domain.fields import Provenance
from fmxray.domain.snapshot import Snapshot, SnapshotMeta


@dataclass(frozen=True)
class SaveReading:
    game: str
    build: str
    known_build: bool
    db_version: str
    game_date: date | None
    reader_version: str
    warnings: tuple[str, ...]
    provenance: Mapping[str, Provenance]
    frame: pl.DataFrame


class SaveSource(Protocol):
    def read(self, path: Path) -> SaveReading: ...


class SnapshotStore(Protocol):
    def write(self, snapshot: Snapshot) -> None: ...

    def read(self, career_id: int, snapshot_id: str) -> pl.DataFrame: ...

    def delete(self, career_id: int, snapshot_id: str) -> None: ...


class CatalogStore(Protocol):
    def get_or_create_career(self, name: str) -> int: ...

    def find_career(self, name: str) -> int | None: ...

    def find_by_sha256(self, career_id: int, sha256: str) -> SnapshotMeta | None: ...

    def add_snapshot(self, meta: SnapshotMeta) -> None: ...

    def list_snapshots(self, career_id: int | None = None) -> list[SnapshotMeta]: ...

    def latest_snapshot(self, career_id: int) -> SnapshotMeta | None: ...
