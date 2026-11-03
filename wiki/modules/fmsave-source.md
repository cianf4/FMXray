---
title: Modulo adapters.fmsave_source
updated: 2026-11-03
sources:
  - src/fmxray/adapters/fmsave_source/source.py
  - src/fmxray/adapters/fmsave_source/mapping.py
  - tests/adapters/test_fmsave_source.py
  - tests/adapters/fake_fmsave.py
  - tests/integration/test_real_save.py
source_commit: 2025c37
confidence: high
---

# Modulo adapters.fmsave_source

## Purpose
L'**unico** modulo che importa `fmsave` (contratto import-linter 4). Implementa `SaveSource`.

## Key files
| File | Contenuto |
| --- | --- |
| `source.py` | `FmsaveSaveSource(module=None)`: `fmsave.open` → `save.info` + `save.players().to_columns()`; raccoglie i warning; traduce le eccezioni |
| `mapping.py` | `COLUMN_MAP` (nostra colonna → colonna piatta fmsave), `FIELD_PATHS` (→ path di `field_status`), `to_frame()` |

## Invariants
- Usa `Table.to_columns()`, non l'extra `polars` di fmsave: il DataFrame lo costruiamo noi con lo schema del catalogo.
- Provenienza: clausole rescissorie `derived`; su FM27 tutto il resto `unconfirmed`; su FM26 `fmsave.field_status`.
- Errori: `UnsupportedGameError` → `UnsupportedSaveError`; `CorruptSaveError`, `NotAFmSaveError`, `ReaderCheckError` → `UnreadableSaveError`.
- La colonna di una clausola contiene il `value` della prima clausola con quel `kind`, altrimenti `None`.

## How to change this safely
Aggiornare fmsave: leggere il changelog, cambiare la versione esatta in `pyproject.toml`, `uv sync`, poi `uv run pytest` **con** il save reale presente. `test_field_paths_are_registered_in_fmsave` rileva path rinominati.

## Verification
`uv run pytest tests/adapters/test_fmsave_source.py tests/integration`

## Open risks
fmsave cambia spesso (K1); la build FM27 dell'utente non è registrata in fmsave 0.9.3.
