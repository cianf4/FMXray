"""Versioned SQLite schema. MIGRATIONS[i] brings the database to version i + 1."""

import sqlite3

MIGRATIONS: tuple[str, ...] = (
    """
    CREATE TABLE careers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL
    );
    CREATE TABLE snapshots (
        id TEXT PRIMARY KEY,
        career_id INTEGER NOT NULL REFERENCES careers(id),
        game TEXT NOT NULL,
        build TEXT NOT NULL,
        known_build INTEGER NOT NULL,
        db_version TEXT NOT NULL,
        game_date TEXT,
        imported_at TEXT NOT NULL,
        source_sha256 TEXT NOT NULL,
        source_kind TEXT NOT NULL,
        reader_version TEXT NOT NULL,
        row_count INTEGER NOT NULL,
        provenance_json TEXT NOT NULL,
        warnings_json TEXT NOT NULL,
        UNIQUE (career_id, source_sha256)
    );
    """,
    """
    CREATE TABLE saved_searches (
        name TEXT PRIMARY KEY,
        query_text TEXT NOT NULL,
        spec_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """,
)


def migrate(conn: sqlite3.Connection) -> None:
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for version, script in enumerate(MIGRATIONS[current:], start=current + 1):
        conn.executescript(f"BEGIN; {script} PRAGMA user_version = {version}; COMMIT;")
