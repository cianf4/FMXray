"""In-memory fakes of the application ports."""

from datetime import date
from pathlib import Path

import polars as pl

from fmxray.application.column_views import ColumnView
from fmxray.application.errors import SavedSearchExistsError
from fmxray.application.ports import SavedSearch, SaveReading
from fmxray.domain.fields import PLAYER_CATALOG, Provenance
from fmxray.domain.snapshot import Snapshot, SnapshotMeta
from tests.factories import make_player_frame


def make_reading(rows: int = 3, game: str = "FM27") -> SaveReading:
    return SaveReading(
        game=game,
        build="27.0.0+2493426",
        known_build=False,
        db_version="27.0.0+0",
        game_date=date(2026, 9, 12),
        reader_version="0.9.3",
        warnings=("unverified build",),
        provenance={name: Provenance.UNCONFIRMED for name in PLAYER_CATALOG.names()},
        frame=make_player_frame(rows),
    )


class FakeSaveSource:
    def __init__(self, reading: SaveReading | Exception) -> None:
        self.reading = reading
        self.paths: list[Path] = []

    def read(self, path: Path) -> SaveReading:
        self.paths.append(path)
        assert path.exists(), "the source must be given an existing copy"
        if isinstance(self.reading, Exception):
            raise self.reading
        return self.reading


class InMemorySnapshotStore:
    def __init__(self) -> None:
        self.frames: dict[tuple[int, str], pl.DataFrame] = {}

    def write(self, snapshot: Snapshot) -> None:
        self.frames[(snapshot.meta.career_id, snapshot.meta.snapshot_id)] = snapshot.frame

    def read(self, career_id: int, snapshot_id: str) -> pl.DataFrame:
        return self.frames[(career_id, snapshot_id)]

    def delete(self, career_id: int, snapshot_id: str) -> None:
        self.frames.pop((career_id, snapshot_id), None)


class InMemoryCatalogStore:
    def __init__(self, fail_on_add: bool = False) -> None:
        self.fail_on_add = fail_on_add
        self.careers: dict[str, int] = {}
        self.snapshots: list[SnapshotMeta] = []

    def get_or_create_career(self, name: str) -> int:
        return self.careers.setdefault(name, len(self.careers) + 1)

    def list_careers(self) -> list[str]:
        return sorted(self.careers)

    def find_career(self, name: str) -> int | None:
        return self.careers.get(name)

    def find_by_sha256(self, career_id: int, sha256: str) -> SnapshotMeta | None:
        return next(
            (m for m in self.snapshots if m.career_id == career_id and m.source_sha256 == sha256),
            None,
        )

    def add_snapshot(self, meta: SnapshotMeta) -> None:
        if self.fail_on_add:
            raise RuntimeError("catalog unavailable")
        self.snapshots.append(meta)

    def list_snapshots(self, career_id: int | None = None) -> list[SnapshotMeta]:
        return [m for m in self.snapshots if career_id is None or m.career_id == career_id]

    def latest_snapshot(self, career_id: int) -> SnapshotMeta | None:
        found = self.list_snapshots(career_id)
        return found[-1] if found else None


class InMemorySavedSearchStore:
    def __init__(self) -> None:
        self.searches: dict[str, SavedSearch] = {}

    def save(self, search: SavedSearch, replace: bool = False) -> None:
        if search.name in self.searches and not replace:
            raise SavedSearchExistsError(search.name)
        self.searches[search.name] = search

    def get(self, name: str) -> SavedSearch | None:
        return self.searches.get(name)

    def list(self) -> list[SavedSearch]:
        return [self.searches[name] for name in sorted(self.searches)]

    def delete(self, name: str) -> bool:
        return self.searches.pop(name, None) is not None


class InMemoryColumnViewStore:
    def __init__(self) -> None:
        self.views: dict[str, ColumnView] = {}

    def save(self, view: ColumnView) -> None:
        self.views[view.name] = view

    def list(self) -> list[ColumnView]:
        return [self.views[name] for name in sorted(self.views)]

    def delete(self, name: str) -> bool:
        return self.views.pop(name, None) is not None


class InMemoryCareerSourceStore:
    def __init__(self) -> None:
        self.paths: dict[int, Path] = {}

    def set(self, career_id: int, path: Path) -> None:
        self.paths[career_id] = path

    def get(self, career_id: int) -> Path | None:
        return self.paths.get(career_id)
