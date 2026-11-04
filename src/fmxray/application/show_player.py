"""Use case: find a player in a snapshot and return all their fields."""

from dataclasses import dataclass

import polars as pl

from fmxray.application.errors import FmxrayError
from fmxray.application.ports import CatalogStore, SnapshotStore
from fmxray.application.snapshots import load_snapshot
from fmxray.domain.snapshot import SnapshotMeta
from fmxray.domain.text import fold


@dataclass(frozen=True)
class PlayerMatch:
    uid: int
    name: str
    club_name: str | None
    age: int | None


class ShowPlayer:
    def __init__(self, store: SnapshotStore, catalog: CatalogStore) -> None:
        self._store = store
        self._catalog = catalog

    def find(
        self, career_name: str, query: str, snapshot_id: str | None = None
    ) -> list[PlayerMatch]:
        _, frame = load_snapshot(self._store, self._catalog, career_name, snapshot_id)
        needle = fold(query)
        names, full_names = frame["name"].to_list(), frame["full_name"].to_list()
        hits = [
            i
            for i, (name, full) in enumerate(zip(names, full_names, strict=True))
            if name is not None and (needle in fold(name) or needle in fold(full or ""))
        ]
        rows = frame[hits].select("uid", "name", "club_name", "age").iter_rows()
        return [PlayerMatch(uid, name, club, age) for uid, name, club, age in rows]

    def details(
        self, career_name: str, uid: int, snapshot_id: str | None = None
    ) -> tuple[SnapshotMeta, dict[str, object]]:
        meta, frame = load_snapshot(self._store, self._catalog, career_name, snapshot_id)
        rows = frame.filter(pl.col("uid") == uid).to_dicts()
        if not rows:
            raise FmxrayError(f"no player with uid {uid} in snapshot {meta.snapshot_id}")
        return meta, rows[0]
