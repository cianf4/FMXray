---
title: Modello dati
updated: 2026-11-03
sources:
  - src/fmxray/domain/fields.py
  - src/fmxray/adapters/sqlite_catalog/schema.py
  - src/fmxray/adapters/parquet_store/store.py
source_commit: 2025c37
confidence: high
---

# Modello dati

- **Snapshot giocatori:** Parquet zstd in `<data-dir>/snapshots/<career_id>/<snapshot_id>.parquet`, colonne = `PLAYER_CATALOG` (vedi [domain](../modules/domain.md)). Sul save FM27 dell'utente: 126.427 righe, 16 MB.
- **Catalogo:** SQLite `<data-dir>/catalog.db`, tabelle `careers` e `snapshots` (metadati, provenienze in JSON, warning in JSON), `user_version = 1`.
- **ID:** `snapshot_id` = UUIDv7 (ordinabile nel tempo); `uid` vale dentro un save; `unique_id` tra carriere (può essere `None`).
- **Soldi:** unità interna del save, nessuna conversione (V4 aperta).
