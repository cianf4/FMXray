---
title: Agent Handoff
updated: 2026-11-04
sources:
  - wiki/agent/activity.md
  - wiki/project/work-tracker.md
  - wiki/project/decisions.md
source_commit: unknown
confidence: medium
---

# Agent Handoff

## Current Work State

- Status: SP2 implementato, non ancora committato
- Goal: commit, push, CI verde, PR di SP2
- Last completed step: Task 8 del [piano SP2](../../docs/superpowers/plans/2026-11-04-sp2-ricerca.md) e revisione finale inline
- Current branch: `sp2-ricerca`
- Last commit: `af7688a` (spec e piano di SP2)
- Worktree: dirty (tutto SP2: `src`, `tests`, `wiki`)

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | Commit e push di SP2 (li lancia l'utente) | — | branch `sp2-ricerca` su GitHub | `git log --oneline -3` | niente attribuzioni a Claude |
| 2 | PR di SP2 con `gh pr create` | `local/pr-sp2.md` | CI verde, PR aperta | `gh pr checks` | |
| 3 | SP3: brainstorming dell'interfaccia | spec madre §8 | spec SP3 approvata | Not verified - documento | prima skill: `superpowers:brainstorming` |

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
| `uv run pytest` | repo | 117 passed | save reale incluso |
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
