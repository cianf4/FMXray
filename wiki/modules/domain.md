---
title: Modulo domain
updated: 2026-11-03
sources:
  - src/fmxray/domain/fields.py
  - src/fmxray/domain/snapshot.py
  - src/fmxray/domain/errors.py
  - tests/domain/test_fields.py
  - tests/domain/test_snapshot.py
source_commit: 2025c37
confidence: high
---

# Modulo domain

## Purpose
Modello puro di FM X-Ray: il catalogo delle colonne giocatore e lo snapshot. Non importa nessun altro pacchetto del progetto (contratto import-linter 1).

## Key files
| File | Contenuto |
| --- | --- |
| `src/fmxray/domain/fields.py` | `Provenance`, `FieldGroup`, `Unit`, `FieldSpec`, `FieldCatalog`, `PLAYER_CATALOG`, costanti `ATTRIBUTES` (52), `HIDDEN_ATTRIBUTES`, `PERSONALITY`, `POSITIONS`, `RELEASE_CLAUSES` |
| `src/fmxray/domain/snapshot.py` | `SnapshotMeta`, `Snapshot`, `validate_frame` |
| `src/fmxray/domain/errors.py` | `SchemaMismatchError` |

## Invariants
- Ogni attributo esiste in due colonne: `<nome>` (1–20) e `<nome>_raw` (1–100).
- I soldi (`transfer_value`, `contract_wage`, clausole) sono nell'unità interna del save.
- Uno `Snapshot` si costruisce solo se il DataFrame ha esattamente nomi, ordine e tipi di `PLAYER_CATALOG` e `meta.row_count == frame.height`.
- La provenienza non sta nel catalogo: viaggia in `SnapshotMeta.provenance`.

## How to change this safely
Aggiungere una colonna = `FieldSpec` in `_build_player_catalog()` + mappatura in `adapters/fmsave_source/mapping.py` (il test `test_every_catalog_column_is_mapped` fallisce finché manca) + valore in `tests/factories.py` se il tipo è nuovo. Gli snapshot già salvati con lo schema vecchio non si rileggono: serve una migrazione (non ancora prevista).

## Verification
`uv run pytest tests/domain`
