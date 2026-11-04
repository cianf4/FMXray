---
title: Work Tracker
updated: 2026-11-04
sources:
  - wiki/agent/activity.md
  - wiki/agent/handoff.md
  - brainstorming 2026-10-31
source_commit: unknown
confidence: medium
---

# Work Tracker

## Active Work

| Priority | Work item | Status | Owner | Evidence | Next verification |
| --- | --- | --- | --- | --- | --- |
| P0 | SP2 motore di ricerca: commit, CI, PR | in progress | utente (commit/push) + agent (PR) | branch `sp2-ricerca` | CI verde su Linux e Windows |

## Planned Work

| Priority | Work item | Why it matters | Start files | Done when |
| --- | --- | --- | --- | --- |
| P1 | SP3 interfaccia della Fase 1 | tabella e scheda giocatore | spec madre §8 | spec e piano approvati |

## Recently Completed

| Date | Work item | Verification | Evidence |
| --- | --- | --- | --- |
| 2026-11-04 | SP2 Task 1–8: albero dei filtri, parser, campi calcolati, SearchPlayers, CSV, ricerche salvate (SQLite v2), comandi `search`/`searches` | `uv run pytest` → 117 passed (save reale incluso); ruff, mypy, lint-imports puliti | [search](../modules/search.md) |
| 2026-11-03 | SP1 unito in `main` (PR #1) | CI verde Linux + Windows, 56 test | merge `95075b9` |
| 2026-11-03 | SP1 Task 1–8: scheletro, catalogo campi, snapshot, ImportSave, Parquet, SQLite, adattatore fmsave, CLI | `uv run pytest` → 55 passed | commit `568c2d7..2025c37` |
| 2026-11-03 | Spec madre, spec e piano SP1 | approvati dall'utente | `docs/superpowers/` |
| 2026-10-31 | Ricerca di contesto online (fmsave, tool esistenti, FM-Arena, FM27) | Not verified - ricerca documentale | [fmsave](../reference/fmsave.md), [prior art](../reference/prior-art.md) |
| 2026-10-31 | Inizializzazione della wiki | file presenti in `wiki/` | [log](../log.md) |

## Blocked / Waiting

| Work item | Blocker | Needed from | Next check |
| --- | --- | --- | --- |
| V1, V4 | rimandate dall'utente (2026-11-03): confronto con il gioco e con un tool esterno dopo l'uscita ufficiale di FM27 | utente | dopo il 2026-11-10 |
| V5, V7 | nuovo `Roma.fm` dopo una sessione; spostate in SP4 (storico e newgen) | utente | inizio SP4 |
