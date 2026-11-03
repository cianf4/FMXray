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
- Goal: chiudere SP1 (verifiche V1, V4, V5, V7) e partire con SP2
- Last completed step: Task 1–8 del piano SP1 committati (`568c2d7..2025c37`), suite 55 test verde; import reale di `Roma.fm` fatto
- Current branch: `sp1-fondamenta`
- Last commit: `2025c37`
- Worktree: dirty solo per la wiki (Task 9)

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | V1/V4: raccogliere il confronto nel gioco dell'utente e registrare l'esito (senza valori dei giocatori) in `wiki/reference/fmsave.md` | `local/v1-check.md`, `wiki/reference/fmsave.md` | esito registrato; fattore monetario stimato | Not verified - confronto manuale nel gioco | i valori restano in `local/` |
| 2 | V5/V7: importare il nuovo `Roma.fm` dalla cartella cloud dopo una sessione di gioco e confrontare `uid`/`unique_id` | `local/saves/fm27/`, `src/fmxray/adapters/fmsave_source/` | esito in `wiki/reference/fmsave.md` | `uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma` | serve un nuovo save dall'utente |
| 3 | Revisione finale del branch SP1, merge in `main` (lo fa l'utente) | `docs/superpowers/plans/2026-11-03-sp1-fondamenta.md` | CI verde su Linux e Windows | `uv run pytest` | |
| 4 | SP2: spec del motore di ricerca | spec madre §7, §12 | spec approvata | Not verified - documento | |

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
