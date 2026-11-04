"""Finding and loading a career's snapshots, shared by the use cases."""

import polars as pl

from fmxray.application.errors import CareerNotFoundError, FmxrayError
from fmxray.application.ports import CatalogStore, SnapshotStore
from fmxray.domain.snapshot import SnapshotMeta


def find_snapshot(
    catalog: CatalogStore, career_name: str, snapshot_id: str | None = None
) -> SnapshotMeta:
    """The given snapshot of a career, or its latest one when `snapshot_id` is None."""
    career_id = catalog.find_career(career_name)
    if career_id is None:
        raise CareerNotFoundError(f"no career named {career_name!r}")
    if snapshot_id is None:
        meta = catalog.latest_snapshot(career_id)
    else:
        found = (m for m in catalog.list_snapshots(career_id) if m.snapshot_id == snapshot_id)
        meta = next(found, None)
    if meta is None:
        raise FmxrayError(f"no snapshot found for career {career_name!r}")
    return meta


def load_snapshot(
    store: SnapshotStore,
    catalog: CatalogStore,
    career_name: str,
    snapshot_id: str | None = None,
) -> tuple[SnapshotMeta, pl.DataFrame]:
    meta = find_snapshot(catalog, career_name, snapshot_id)
    return meta, store.read(meta.career_id, meta.snapshot_id)


def previous_snapshot(
    catalog: CatalogStore, career_id: int, snapshot_id: str
) -> SnapshotMeta | None:
    """The snapshot imported just before `snapshot_id` in the same career."""
    snapshots = catalog.list_snapshots(career_id)
    ids = [m.snapshot_id for m in snapshots]
    index = ids.index(snapshot_id) if snapshot_id in ids else 0
    return snapshots[index - 1] if index > 0 else None
