"""Saved searches, stored in the same SQLite file as the catalog."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Self

from fmxray.adapters.sqlite_catalog.schema import migrate
from fmxray.application.errors import SavedSearchExistsError
from fmxray.application.ports import SavedSearch
from fmxray.domain.search.errors import SpecFormatError
from fmxray.domain.search.spec import from_json, to_json


class SqliteSavedSearchStore:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        migrate(self._conn)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def save(self, search: SavedSearch, replace: bool = False) -> None:
        verb = "INSERT OR REPLACE" if replace else "INSERT"
        row = (
            search.name, search.query_text, json.dumps(to_json(search.spec)),
            search.created_at.isoformat(),
        )  # fmt: skip
        try:
            with self._conn:
                self._conn.execute(f"{verb} INTO saved_searches VALUES (?, ?, ?, ?)", row)
        except sqlite3.IntegrityError:
            raise SavedSearchExistsError(
                f"a saved search named {search.name!r} already exists (use --replace)"
            ) from None

    def get(self, name: str) -> SavedSearch | None:
        row = self._conn.execute("SELECT * FROM saved_searches WHERE name = ?", (name,)).fetchone()
        return None if row is None else _to_search(row)

    def list(self) -> list[SavedSearch]:
        rows = self._conn.execute("SELECT * FROM saved_searches ORDER BY name").fetchall()
        return [_to_search(row) for row in rows]

    def delete(self, name: str) -> bool:
        with self._conn:
            cursor = self._conn.execute("DELETE FROM saved_searches WHERE name = ?", (name,))
        return cursor.rowcount > 0


def _to_search(row: tuple[str, str, str, str]) -> SavedSearch:
    name, query_text, spec_json, created_at = row
    try:
        spec = from_json(json.loads(spec_json))
    except (SpecFormatError, json.JSONDecodeError, AttributeError) as error:
        raise SpecFormatError(f"saved search {name!r} cannot be read: {error}") from error
    return SavedSearch(name, query_text, spec, datetime.fromisoformat(created_at))
