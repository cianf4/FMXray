"""User preferences kept in the catalog file: column views and career save folders."""

import json
import sqlite3
from pathlib import Path
from types import TracebackType
from typing import Self

from fmxray.adapters.sqlite_catalog.schema import migrate
from fmxray.application.column_views import ColumnView


class _Connection:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")
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


class SqliteColumnViewStore(_Connection):
    def save(self, view: ColumnView) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO column_views VALUES (?, ?)",
                (view.name, json.dumps(list(view.columns))),
            )

    def list(self) -> list[ColumnView]:
        rows = self._conn.execute("SELECT name, columns_json FROM column_views ORDER BY name")
        return [ColumnView(name, tuple(json.loads(columns))) for name, columns in rows]

    def delete(self, name: str) -> bool:
        with self._conn:
            cursor = self._conn.execute("DELETE FROM column_views WHERE name = ?", (name,))
        return cursor.rowcount > 0


class SqliteCareerSourceStore(_Connection):
    def set(self, career_id: int, path: Path) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO career_sources VALUES (?, ?)", (career_id, str(path))
            )

    def get(self, career_id: int) -> Path | None:
        row = self._conn.execute(
            "SELECT path FROM career_sources WHERE career_id = ?", (career_id,)
        ).fetchone()
        return None if row is None else Path(row[0])
