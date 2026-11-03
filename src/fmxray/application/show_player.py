"""Use case: find a player in a snapshot and return all their fields."""

import unicodedata
from dataclasses import dataclass

import polars as pl

from fmxray.application.errors import CareerNotFoundError, FmxrayError
from fmxray.application.ports import CatalogStore, SnapshotStore
from fmxray.domain.snapshot import SnapshotMeta


@dataclass(frozen=True)
class PlayerMatch:
    uid: int
    name: str
    club_name: str | None
    age: int | None


def _fold(text: str) -> str:
    """Lowercase and strip accents, so "unal celik" matches "Ünal Çelik"."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


class ShowPlayer:
    def __init__(self, store: SnapshotStore, catalog: CatalogStore) -> None:
        self._store = store
        self._catalog = catalog

    def _snapshot(self, career_name: str, snapshot_id: str | None) -> SnapshotMeta:
        career_id = self._catalog.find_career(career_name)
        if career_id is None:
            raise CareerNotFoundError(f"no career named {career_name!r}")
        if snapshot_id is None:
            meta = self._catalog.latest_snapshot(career_id)
        else:
            meta = next(
                (
                    m
                    for m in self._catalog.list_snapshots(career_id)
                    if m.snapshot_id == snapshot_id
                ),
                None,
            )
        if meta is None:
            raise FmxrayError(f"no snapshot found for career {career_name!r}")
        return meta

    def _frame(self, meta: SnapshotMeta) -> pl.DataFrame:
        return self._store.read(meta.career_id, meta.snapshot_id)

    def find(
        self, career_name: str, query: str, snapshot_id: str | None = None
    ) -> list[PlayerMatch]:
        frame = self._frame(self._snapshot(career_name, snapshot_id))
        needle = _fold(query)
        names, full_names = frame["name"].to_list(), frame["full_name"].to_list()
        hits = [
            i
            for i, (name, full) in enumerate(zip(names, full_names, strict=True))
            if name is not None and (needle in _fold(name) or needle in _fold(full or ""))
        ]
        rows = frame[hits].select("uid", "name", "club_name", "age").iter_rows()
        return [PlayerMatch(uid, name, club, age) for uid, name, club, age in rows]

    def details(
        self, career_name: str, uid: int, snapshot_id: str | None = None
    ) -> tuple[SnapshotMeta, dict[str, object]]:
        meta = self._snapshot(career_name, snapshot_id)
        rows = self._frame(meta).filter(pl.col("uid") == uid).to_dicts()
        if not rows:
            raise FmxrayError(f"no player with uid {uid} in snapshot {meta.snapshot_id}")
        return meta, rows[0]
