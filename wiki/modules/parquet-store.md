---
title: Modulo adapters.parquet_store
updated: 2026-11-03
sources:
  - src/fmxray/adapters/parquet_store/store.py
  - tests/adapters/test_parquet_store.py
source_commit: 2025c37
confidence: high
---

# Modulo adapters.parquet_store

## Purpose
`ParquetSnapshotStore(root)`: implementa `SnapshotStore`, un file `root/<career_id>/<snapshot_id>.parquet` (zstd) per snapshot.

## Invariants
- Scrittura atomica: `*.parquet.tmp` → `os.replace`; il `.tmp` viene sempre rimosso.
- `read` applica lo schema del catalogo; file assente → `FileNotFoundError`; `delete` di un file assente non fa nulla.

## Verification
`uv run pytest tests/adapters/test_parquet_store.py`
