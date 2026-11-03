---
title: Work Tracker
updated: 2026-10-31
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
| P0 | SP1 Fondamenta: verifiche finali e merge | in progress | agent + utente | [handoff](../agent/handoff.md) | `uv run pytest` |

## Planned Work

| Priority | Work item | Why it matters | Start files | Done when |
| --- | --- | --- | --- | --- |
| P1 | SP2 motore di ricerca | filtri su CA/PA/hidden (Fase 1) | spec madre §7 | spec e piano approvati |

## Recently Completed

| Date | Work item | Verification | Evidence |
| --- | --- | --- | --- |
| 2026-11-03 | SP1 Task 1–8: scheletro, catalogo campi, snapshot, ImportSave, Parquet, SQLite, adattatore fmsave, CLI | `uv run pytest` → 55 passed | commit `568c2d7..2025c37` |
| 2026-11-03 | Spec madre, spec e piano SP1 | approvati dall'utente | `docs/superpowers/` |
| 2026-10-31 | Ricerca di contesto online (fmsave, tool esistenti, FM-Arena, FM27) | Not verified - ricerca documentale | [fmsave](../reference/fmsave.md), [prior art](../reference/prior-art.md) |
| 2026-10-31 | Inizializzazione della wiki | file presenti in `wiki/` | [log](../log.md) |

## Blocked / Waiting

| Work item | Blocker | Needed from | Next check |
| --- | --- | --- | --- |
| V1, V4 | confronto dei valori nel gioco | utente | prossima sessione |
| V5, V7 | nuovo `Roma.fm` dopo una sessione | utente | prossima sessione |
