"""Snapshot store: one zstd Parquet file per snapshot, written atomically."""

import os
from pathlib import Path

import polars as pl

from fmxray.domain.fields import PLAYER_CATALOG
from fmxray.domain.snapshot import Snapshot


class ParquetSnapshotStore:
    def __init__(self, root: Path) -> None:
        self._root = root

    def _path(self, career_id: int, snapshot_id: str) -> Path:
        return self._root / str(career_id) / f"{snapshot_id}.parquet"

    def write(self, snapshot: Snapshot) -> None:
        final = self._path(snapshot.meta.career_id, snapshot.meta.snapshot_id)
        final.parent.mkdir(parents=True, exist_ok=True)
        tmp = final.with_name(final.name + ".tmp")
        try:
            snapshot.frame.write_parquet(tmp, compression="zstd")
            os.replace(tmp, final)
        finally:
            tmp.unlink(missing_ok=True)

    def read(self, career_id: int, snapshot_id: str) -> pl.DataFrame:
        path = self._path(career_id, snapshot_id)
        if not path.exists():
            raise FileNotFoundError(path)
        return pl.read_parquet(path, schema=PLAYER_CATALOG.polars_schema())

    def delete(self, career_id: int, snapshot_id: str) -> None:
        self._path(career_id, snapshot_id).unlink(missing_ok=True)
