import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from fmxray.adapters.sqlite_catalog import SqliteCatalogStore
from fmxray.domain.fields import Provenance
from tests.factories import make_meta


def test_career_is_created_once(tmp_path: Path) -> None:
    with SqliteCatalogStore(tmp_path / "catalog.db") as catalog:
        first = catalog.get_or_create_career("Roma")
        assert catalog.get_or_create_career("Roma") == first
        assert catalog.find_career("Roma") == first
        assert catalog.find_career("Lazio") is None


def test_add_and_find_by_sha256(tmp_path: Path) -> None:
    with SqliteCatalogStore(tmp_path / "catalog.db") as catalog:
        career = catalog.get_or_create_career("Roma")
        meta = make_meta(
            career_id=career,
            game_date=None,
            provenance={"ca": Provenance.UNCONFIRMED, "release_fee_min": Provenance.DERIVED},
            warnings=("unverified build",),
        )
        catalog.add_snapshot(meta)
        assert catalog.find_by_sha256(career, meta.source_sha256) == meta
        assert catalog.find_by_sha256(career, "f" * 64) is None


def test_same_sha_in_two_careers_is_allowed(tmp_path: Path) -> None:
    with SqliteCatalogStore(tmp_path / "catalog.db") as catalog:
        roma = catalog.get_or_create_career("Roma")
        other = catalog.get_or_create_career("Roma bis")
        catalog.add_snapshot(make_meta(snapshot_id="a", career_id=roma))
        catalog.add_snapshot(make_meta(snapshot_id="b", career_id=other))
        assert len(catalog.list_snapshots()) == 2


def test_duplicate_sha_in_same_career_raises(tmp_path: Path) -> None:
    with SqliteCatalogStore(tmp_path / "catalog.db") as catalog:
        roma = catalog.get_or_create_career("Roma")
        catalog.add_snapshot(make_meta(snapshot_id="a", career_id=roma))
        with pytest.raises(sqlite3.IntegrityError):
            catalog.add_snapshot(make_meta(snapshot_id="b", career_id=roma))


def test_latest_snapshot_orders_by_game_date(tmp_path: Path) -> None:
    with SqliteCatalogStore(tmp_path / "catalog.db") as catalog:
        roma = catalog.get_or_create_career("Roma")
        late = make_meta(
            snapshot_id="late", career_id=roma, source_sha256="1" * 64,
            game_date=date(2027, 1, 1), imported_at=datetime(2026, 11, 1, tzinfo=UTC),
        )  # fmt: skip
        early = make_meta(
            snapshot_id="early", career_id=roma, source_sha256="2" * 64,
            game_date=date(2026, 9, 12), imported_at=datetime(2026, 11, 2, tzinfo=UTC),
        )  # fmt: skip
        catalog.add_snapshot(late)
        catalog.add_snapshot(early)
        assert [m.snapshot_id for m in catalog.list_snapshots(roma)] == ["early", "late"]
        latest = catalog.latest_snapshot(roma)
        assert latest is not None and latest.snapshot_id == "late"


def test_data_survives_reopen(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    with SqliteCatalogStore(db) as catalog:
        meta = make_meta(career_id=catalog.get_or_create_career("Roma"))
        catalog.add_snapshot(meta)
    with SqliteCatalogStore(db) as catalog:
        assert catalog.list_snapshots() == [meta]


def test_user_version_is_1(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    SqliteCatalogStore(db).close()
    with sqlite3.connect(db) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
