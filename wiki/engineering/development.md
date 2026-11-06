---
title: Sviluppo
updated: 2026-11-06
sources:
  - pyproject.toml
  - .python-version
  - uv.lock
source_commit: 2025c37
confidence: high
---

# Sviluppo

| Cosa | Comando (dalla radice del repo) |
| --- | --- |
| Installare / aggiornare l'ambiente (lo lancia l'utente) | `uv sync` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check` |
| Formattazione | `uv run ruff format` (controllo: `uv run ruff format --check`) |
| Tipi | `uv run mypy src tests` |
| Regole di import | `uv run lint-imports` |
| Usare il tool | `uv run fmxray --help` |

- Python 3.14 (`.python-version`), dipendenze bloccate in `uv.lock`; fmsave è fissato a `==0.9.3`.
- Branch per le PR con prefisso di tipo: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `ci/` (es. `fix/csv-formule`); SP1 e SP2 usavano `sp1-fondamenta`, `sp2-ricerca`. Commit e push li fa l'utente.
- Gli stessi comandi valgono su Windows (PowerShell) e Linux; la CI li esegue su entrambi.
