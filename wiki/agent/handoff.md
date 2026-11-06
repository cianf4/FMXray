---
title: Agent Handoff
updated: 2026-11-06
sources:
  - wiki/agent/activity.md
  - wiki/project/work-tracker.md
  - wiki/project/decisions.md
source_commit: unknown
confidence: medium
---

# Agent Handoff

## Current Work State

- Status: SP2 chiuso (PR #2 e #3 unite); SP3 in brainstorming
- Goal: SP3 (interfaccia della Fase 1): brainstorming → spec → piano
- Last completed step: fix CSV (PR #3, merge `9bfc8a1`); wiki allineata e `CLAUDE.md` aggiunto sul branch `docs/handoff-portatile`
- Current branch: `docs/handoff-portatile` (da unire in `main`)
- Last commit: `9bfc8a1`
- Worktree: dirty solo per wiki e `CLAUDE.md`

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | Riprendere il brainstorming di SP3 con `superpowers:brainstorming` | spec madre §8 e §12, [decisioni](../project/decisions.md) D10, D11, D21 | spec SP3 approvata e committata | Not verified - documento | prima domanda già fatta: cosa fa e guarda l'utente sul secondo schermo; mockup con il visual companion |
| 2 | Piano di SP3 con `superpowers:writing-plans` | spec SP3 | piano approvato | Not verified - documento | aggiungere PySide6 e pytest-qt (installazione la lancia l'utente) |

## Blockers

| Blocker | Type | Needed from | Current workaround |
| --- | --- | --- | --- |
| Nuovo `Roma.fm` per V5/V7 | external | utente | i "nuovi risultati" usano `uid` finché V5 non dice altro |

## Known Risks

| Risk | Impact | Mitigation | Evidence |
| --- | --- | --- | --- |
| fmsave cambia API spesso | alto | versione bloccata + adattatore | K1 in [rischi](../project/risks.md) |
| `uid` non stabile tra save | medio | confronto in un solo punto (`RunSavedSearch`) | V5 in [requisiti](../project/requirements.md) |

## Commands Already Run

| Command | Directory | Result | Evidence / notes |
| --- | --- | --- | --- |
| `uv run pytest` | repo | 118 passed | save reale incluso (2026-11-04) |
| `uv run fmxray search "finishng>15" --career Roma` | repo | exit 1, suggerisce `finishing` | criterio 3 della spec SP2 |

## Do Not Redo

- Ricerca online su fmsave, tool esistenti, FM-Arena, FM27: è in [fmsave](../reference/fmsave.md) e [prior art](../reference/prior-art.md).
- Decisione fmsave contro parser proprio: presa (D2–D4).
- Design del motore di ricerca: [spec SP2](../../docs/superpowers/specs/2026-11-04-sp2-ricerca-design.md) e [modulo search](../modules/search.md).

## Evidence Trail

- [Activity log](activity.md)
- [Work tracker](../project/work-tracker.md)
- [Project status](../project/status.md)
- [Decisions](../project/decisions.md)
