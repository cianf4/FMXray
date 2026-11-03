---
title: Modulo adapters.sqlite_catalog
updated: 2026-11-03
sources:
  - src/fmxray/adapters/sqlite_catalog/catalog.py
  - src/fmxray/adapters/sqlite_catalog/schema.py
  - tests/adapters/test_sqlite_catalog.py
source_commit: 2025c37
confidence: high
---

# Modulo adapters.sqlite_catalog

## Purpose
`SqliteCatalogStore(db_path)`: implementa `CatalogStore` (carriere e metadati degli snapshot).

## Invariants
- Schema versionato con `PRAGMA user_version`; `MIGRATIONS[i]` porta alla versione `i + 1` (oggi 1: tabelle `careers`, `snapshots`).
- `UNIQUE (career_id, source_sha256)`: lo stesso save in due carriere è permesso, due volte nella stessa no.
- Ordine degli snapshot: `game_date` (NULL per ultimi), poi `imported_at`.

## How to change this safely
Una modifica allo schema = nuova stringa in coda a `MIGRATIONS`, mai modificare quelle esistenti.

## Verification
`uv run pytest tests/adapters/test_sqlite_catalog.py`
