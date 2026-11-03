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
- Last completed step: spec madre scritta (2026-11-03), decisioni D1–D20
- Current branch: `unknown` (la cartella non è un repo git)
- Last commit: `unknown`
- Worktree: unknown

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | Revisione della spec madre da parte dell'utente | `docs/superpowers/specs/2026-11-03-fm-x-ray-design.md` | l'utente approva (o le modifiche sono applicate) | Not verified - documento | lingua UI (inglese) e repo (pubblico, MIT) decisi: D21, D22 |
| 2 | Spec di SP1 (Fondamenta) → `superpowers:writing-plans` | spec madre §12 | spec e piano SP1 approvati | Not verified - documento | |
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
