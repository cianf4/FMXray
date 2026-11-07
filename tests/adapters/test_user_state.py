import sqlite3
from pathlib import Path

from fmxray.adapters.sqlite_catalog import (
    SqliteCareerSourceStore,
    SqliteCatalogStore,
    SqliteColumnViewStore,
)
from fmxray.adapters.sqlite_catalog.schema import MIGRATIONS
from fmxray.application.column_views import ColumnView


def test_view_save_list_delete(tmp_path: Path) -> None:
    with SqliteColumnViewStore(tmp_path / "catalog.db") as store:
        store.save(ColumnView("mine", ("name", "pa")))
        store.save(ColumnView("b", ("name",)))
        assert [v.name for v in store.list()] == ["b", "mine"]
        assert store.delete("mine") is True
        assert store.delete("mine") is False


def test_view_overwrite(tmp_path: Path) -> None:
    with SqliteColumnViewStore(tmp_path / "catalog.db") as store:
        store.save(ColumnView("mine", ("name", "pa")))
        store.save(ColumnView("mine", ("name", "ca")))
        assert store.list() == [ColumnView("mine", ("name", "ca"))]


def test_career_source_set_get(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    with SqliteCatalogStore(db) as catalog:
        career = catalog.get_or_create_career("Roma")
    with SqliteCareerSourceStore(db) as sources:
        assert sources.get(career) is None
        sources.set(career, tmp_path / "games")
        sources.set(career, tmp_path / "cloud" / "games")
        assert sources.get(career) == tmp_path / "cloud" / "games"


def test_v2_database_is_migrated(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    conn = sqlite3.connect(db)
    for version, script in enumerate(MIGRATIONS[:2], start=1):
        conn.executescript(f"BEGIN; {script} PRAGMA user_version = {version}; COMMIT;")
    conn.execute("INSERT INTO saved_searches VALUES ('kept', 'age<22', '{}', '2026-11-06')")
    conn.commit()
    conn.close()
    SqliteColumnViewStore(db).close()
    with sqlite3.connect(db) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
        assert conn.execute("SELECT name FROM saved_searches").fetchall() == [("kept",)]
    conn.close()
