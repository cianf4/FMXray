"""Catalog of careers and snapshots, stored in SQLite."""

import json
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path
from types import TracebackType
from typing import Self

from fmxray.adapters.sqlite_catalog.schema import migrate
from fmxray.domain.fields import Provenance
from fmxray.domain.snapshot import SnapshotMeta

_COLUMNS = (
    "id, career_id, game, build, known_build, db_version, game_date, imported_at, "
    "source_sha256, source_kind, reader_version, row_count, provenance_json, warnings_json"
)
# Snapshots without a game date sort last.
_ORDER = "ORDER BY game_date IS NULL, game_date, imported_at"


class SqliteCatalogStore:
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

    def get_or_create_career(self, name: str) -> int:
        with self._conn:
            self._conn.execute(
                "INSERT OR IGNORE INTO careers (name, created_at) VALUES (?, ?)",
                (name, datetime.now(UTC).isoformat()),
            )
        career_id = self.find_career(name)
        assert career_id is not None
        return career_id

    def list_careers(self) -> list[str]:
        return [row[0] for row in self._conn.execute("SELECT name FROM careers ORDER BY name")]

    def find_career(self, name: str) -> int | None:
        row = self._conn.execute("SELECT id FROM careers WHERE name = ?", (name,)).fetchone()
        return None if row is None else int(row[0])

    def find_by_sha256(self, career_id: int, sha256: str) -> SnapshotMeta | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM snapshots WHERE career_id = ? AND source_sha256 = ?",
            (career_id, sha256),
        ).fetchone()
        return None if row is None else _to_meta(row)

    def add_snapshot(self, meta: SnapshotMeta) -> None:
        with self._conn:
            self._conn.execute(
                f"INSERT INTO snapshots ({_COLUMNS}) VALUES ({', '.join('?' * 14)})",
                (
                    meta.snapshot_id,
                    meta.career_id,
                    meta.game,
                    meta.build,
                    int(meta.known_build),
                    meta.db_version,
                    None if meta.game_date is None else meta.game_date.isoformat(),
                    meta.imported_at.isoformat(),
                    meta.source_sha256,
                    meta.source_kind,
                    meta.reader_version,
                    meta.row_count,
                    json.dumps({k: str(v) for k, v in meta.provenance.items()}),
                    json.dumps(list(meta.warnings)),
                ),
            )

    def list_snapshots(self, career_id: int | None = None) -> list[SnapshotMeta]:
        if career_id is None:
            rows = self._conn.execute(f"SELECT {_COLUMNS} FROM snapshots {_ORDER}")
        else:
            rows = self._conn.execute(
                f"SELECT {_COLUMNS} FROM snapshots WHERE career_id = ? {_ORDER}", (career_id,)
            )
        return [_to_meta(row) for row in rows.fetchall()]

    def latest_snapshot(self, career_id: int) -> SnapshotMeta | None:
        found = self.list_snapshots(career_id)
        return found[-1] if found else None


def _to_meta(row: tuple[object, ...]) -> SnapshotMeta:
    (sid, career, game, build, known, db_version, game_date, imported,
     sha, kind, reader, rows, provenance, warnings) = row  # fmt: skip
    return SnapshotMeta(
        snapshot_id=str(sid),
        career_id=int(str(career)),
        game=str(game),
        build=str(build),
        known_build=bool(known),
        db_version=str(db_version),
        game_date=None if game_date is None else date.fromisoformat(str(game_date)),
        imported_at=datetime.fromisoformat(str(imported)),
        source_sha256=str(sha),
        source_kind=str(kind),
        reader_version=str(reader),
        row_count=int(str(rows)),
        provenance={k: Provenance(v) for k, v in json.loads(str(provenance)).items()},
        warnings=tuple(json.loads(str(warnings))),
    )
