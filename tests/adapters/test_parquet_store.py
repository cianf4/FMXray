from pathlib import Path

import polars as pl
import pytest

from fmxray.adapters.parquet_store import ParquetSnapshotStore
from fmxray.domain.snapshot import Snapshot
from tests.factories import make_meta, make_player_frame


def _snapshot() -> Snapshot:
    frame = make_player_frame(3, traits=[["dictates_tempo"], [], ["crosses_early"]])
    return Snapshot(make_meta(row_count=3), frame)


def test_roundtrip_preserves_frame(tmp_path: Path) -> None:
    store = ParquetSnapshotStore(tmp_path)
    snapshot = _snapshot()
    store.write(snapshot)
    assert store.read(1, "snap-1").equals(snapshot.frame)


def test_no_tmp_file_left_after_write(tmp_path: Path) -> None:
    ParquetSnapshotStore(tmp_path).write(_snapshot())
    assert sorted(p.name for p in (tmp_path / "1").iterdir()) == ["snap-1.parquet"]


def test_failed_write_leaves_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args: object, **kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(pl.DataFrame, "write_parquet", boom)
    with pytest.raises(OSError):
        ParquetSnapshotStore(tmp_path).write(_snapshot())
    assert list((tmp_path / "1").iterdir()) == []


def test_delete_missing_is_noop(tmp_path: Path) -> None:
    ParquetSnapshotStore(tmp_path).delete(1, "missing")


def test_read_missing_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ParquetSnapshotStore(tmp_path).read(1, "missing")
