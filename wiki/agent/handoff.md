---
title: Agent Handoff
updated: 2026-11-03
sources:
  - wiki/agent/activity.md
  - wiki/project/work-tracker.md
  - wiki/project/decisions.md
source_commit: unknown
confidence: medium
---

# Agent Handoff

## Current Work State

- Status: in progress (SP1 quasi chiuso)
- Goal: merge di SP1 e partire con SP2 (V1/V4 rimandate dall'utente all'uscita di FM27; V5/V7 in SP4)
- Last completed step: Task 1–8 del piano SP1 committati (`568c2d7..2025c37`), suite 55 test verde; import reale di `Roma.fm` fatto
- Current branch: `sp1-fondamenta`
- Last commit: `2025c37`
- Worktree: dirty solo per la wiki (Task 9)

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | Merge di SP1 in `main` dopo CI verde, merge in `main` (lo fa l'utente) | `docs/superpowers/plans/2026-11-03-sp1-fondamenta.md` | CI verde su Linux e Windows | `uv run pytest` | |
| 2 | SP2: spec del motore di ricerca | spec madre §7, §12 | spec approvata | Not verified - documento | |

## Blockers

| Blocker | Type | Needed from | Current workaround |
| --- | --- | --- | --- |
| Nessun save reale disponibile | external | utente | proseguire con brainstorming e spec |

## Known Risks

| Risk | Impact | Mitigation | Evidence |
| --- | --- | --- | --- |
| fmsave cambia API spesso | alto | versione bloccata + adattatore | K1 in [rischi](../project/risks.md) |

## Commands Already Run

| Command | Directory | Result | Evidence / notes |
| --- | --- | --- | --- |
| `ls -la` | `/home/cianf/Progetti/FMXray` | pass | cartella vuota prima della wiki |

## Do Not Redo

- Ricerca online su fmsave, tool esistenti, FM-Arena, FM27: è in [fmsave](../reference/fmsave.md) e [prior art](../reference/prior-art.md).
- Decisione fmsave contro parser proprio: presa (D2–D4).

## Evidence Trail

- [Activity log](activity.md)
- [Work tracker](../project/work-tracker.md)
- [Project status](../project/status.md)
- [Decisions](../project/decisions.md)
