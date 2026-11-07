import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fmxray.adapters.sqlite_catalog import SqliteCatalogStore, SqliteSavedSearchStore
from fmxray.adapters.sqlite_catalog.schema import MIGRATIONS
from fmxray.application.errors import SavedSearchExistsError
from fmxray.application.ports import SavedSearch
from fmxray.domain.search.errors import SpecFormatError
from fmxray.domain.search.parser import parse

_CREATED = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)


def _search(name: str = "wonderkids", query: str = "age<22 pa>180") -> SavedSearch:
    return SavedSearch(name, query, parse(query), _CREATED)


def test_save_get_roundtrip(tmp_path: Path) -> None:
    with SqliteSavedSearchStore(tmp_path / "catalog.db") as store:
        store.save(_search())
        assert store.get("wonderkids") == _search()
        assert store.get("missing") is None


def test_duplicate_without_replace_raises(tmp_path: Path) -> None:
    with SqliteSavedSearchStore(tmp_path / "catalog.db") as store:
        store.save(_search())
        with pytest.raises(SavedSearchExistsError):
            store.save(_search(query="age<20"))


def test_replace_overwrites(tmp_path: Path) -> None:
    with SqliteSavedSearchStore(tmp_path / "catalog.db") as store:
        store.save(_search())
        store.save(_search(query="age<20"), replace=True)
        found = store.get("wonderkids")
        assert found is not None and found.query_text == "age<20"


def test_list_sorted_by_name(tmp_path: Path) -> None:
    with SqliteSavedSearchStore(tmp_path / "catalog.db") as store:
        store.save(_search("b"))
        store.save(_search("a"))
        assert [s.name for s in store.list()] == ["a", "b"]


def test_delete_returns_whether_found(tmp_path: Path) -> None:
    with SqliteSavedSearchStore(tmp_path / "catalog.db") as store:
        store.save(_search())
        assert store.delete("wonderkids") is True
        assert store.delete("wonderkids") is False


def test_corrupted_spec_json_raises_spec_format_error(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    SqliteSavedSearchStore(db).close()
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO saved_searches VALUES ('broken', 'age<22', ?, ?)",
            ('{"version": 99}', _CREATED.isoformat()),
        )
    conn.close()
    with SqliteSavedSearchStore(db) as store, pytest.raises(SpecFormatError, match="broken"):
        store.get("broken")


def test_v1_database_is_migrated(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    conn = sqlite3.connect(db)
    conn.executescript(f"BEGIN; {MIGRATIONS[0]} PRAGMA user_version = 1; COMMIT;")
    conn.execute("INSERT INTO careers (name, created_at) VALUES ('Roma', '2026-11-03')")
    conn.commit()
    conn.close()
    SqliteSavedSearchStore(db).close()
    with sqlite3.connect(db) as conn:
        assert conn.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
    conn.close()
    with SqliteCatalogStore(db) as catalog:
        assert catalog.find_career("Roma") is not None
