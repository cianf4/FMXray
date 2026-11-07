"""Ports: what the application needs from the outside world."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Protocol

import polars as pl

from fmxray.application.column_views import ColumnView
from fmxray.domain.fields import Provenance
from fmxray.domain.search.spec import Spec
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

    def list_careers(self) -> list[str]: ...  # names, sorted

    def find_by_sha256(self, career_id: int, sha256: str) -> SnapshotMeta | None: ...

    def add_snapshot(self, meta: SnapshotMeta) -> None: ...

    def list_snapshots(self, career_id: int | None = None) -> list[SnapshotMeta]: ...

    def latest_snapshot(self, career_id: int) -> SnapshotMeta | None: ...


@dataclass(frozen=True)
class SavedSearch:
    name: str
    query_text: str  # what the user typed, for display
    spec: Spec  # what runs: stays valid if the text syntax changes
    created_at: datetime


class SavedSearchStore(Protocol):
    def save(self, search: SavedSearch, replace: bool = False) -> None: ...

    def get(self, name: str) -> SavedSearch | None: ...

    def list(self) -> list[SavedSearch]: ...

    def delete(self, name: str) -> bool: ...


class ColumnViewStore(Protocol):
    def save(self, view: ColumnView) -> None: ...  # overwrites a view with the same name

    def list(self) -> list[ColumnView]: ...

    def delete(self, name: str) -> bool: ...


class CareerSourceStore(Protocol):
    """The save folder (or file) each career follows."""

    def set(self, career_id: int, path: Path) -> None: ...

    def get(self, career_id: int) -> Path | None: ...
