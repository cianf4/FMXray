---
title: Architettura
updated: 2026-11-06
sources:
  - pyproject.toml
  - src/fmxray/bootstrap.py
  - wiki/project/decisions.md
source_commit: 2025c37
confidence: high
---

# Architettura

Esagonale (porte e adattatori), un processo Python. Regole di import verificate da `uv run lint-imports` (7 contratti in `pyproject.toml`).

```mermaid
flowchart LR
  cli[cli] --> app[application]
  ui[ui PySide6] --> app
  boot --> ui
  boot[bootstrap] --> cli
  boot --> fs[adapters.fmsave_source]
  boot --> pq[adapters.parquet_store]
  boot --> sq[adapters.sqlite_catalog]
  app --> dom[domain]
  fs -.implementa SaveSource.-> app
  pq -.implementa SnapshotStore.-> app
  sq -.implementa CatalogStore.-> app
  fs --> fmsave[(fmsave)]
```

| Contratto | Regola |
| --- | --- |
| 1 | `domain` non importa altri pacchetti del progetto |
| 2 | `application` importa solo `domain` |
| 3 | `cli` e `ui` non importano adattatori né `bootstrap` |
| 3b | `domain` e `application` non importano PySide6 |
| 3c | `cli` e `ui` sono indipendenti |
| 4 | solo `adapters.fmsave_source` importa `fmsave` |
| 5 | gli adattatori sono indipendenti tra loro |

UI PySide6 (SP3) e lettura dalla RAM (SP9) si aggiungeranno come nuovi strati/adattatori senza toccare `domain` e `application` (D10, D11, D6). Moduli: [indice](../modules/README.md).
