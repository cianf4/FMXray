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

- Status: in progress
- Goal: far approvare la spec madre e partire con SP1
- Last completed step: spec madre approvata, D7 → FM27, spec SP1 scritta (2026-11-03)
- Current branch: `unknown` (la cartella non è un repo git)
- Last commit: `unknown`
- Worktree: unknown

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | Revisione del piano SP1 da parte dell'utente | `docs/superpowers/plans/2026-11-03-sp1-fondamenta.md` | l'utente approva | Not verified - documento | |
| 2 | Esecuzione di SP1 con `superpowers:executing-plans` inline, Task 1–9 | piano SP1 | criteri di successo della spec SP1 | `uv run pytest` | l'utente lancia `uv sync` e i commit |
| 3 | Verifiche V1–V4 su un save reale | `wiki/reference/fmsave.md`, `wiki/project/requirements.md` | risposte registrate in `reference/fmsave.md` | `uvx fmsave info <save>.fm` (la lancia l'utente) | serve il save dall'utente |

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
