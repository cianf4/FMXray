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

- Status: SP1 chiuso; SP2 non iniziato
- Goal: SP2 (motore di ricerca): brainstorming → spec → piano
- Last completed step: PR #1 unita in `main` (merge `95075b9`), CI verde
- Current branch: `main` (dopo `git switch main`)
- Last commit: `95075b9`
- Worktree: dirty solo per la wiki (chiusura SP1)

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | SP2: brainstorming e spec del motore di ricerca (filtri Specification → Polars, ricerche salvate, barra a testo, CSV) | spec madre §7, §12; `src/fmxray/application/` | spec SP2 approvata | Not verified - documento | prima skill: `superpowers:brainstorming` |

## Blockers

| Blocker | Type | Needed from | Current workaround |
| --- | --- | --- | --- |
| Nuovo `Roma.fm` per V5/V7 | external | utente | non blocca SP2 |

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
