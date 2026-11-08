---
title: Agent Handoff
updated: 2026-11-07
sources:
  - wiki/agent/activity.md
  - wiki/project/work-tracker.md
  - wiki/project/decisions.md
source_commit: unknown
confidence: medium
---

# Agent Handoff

## Current Work State

- Status: SP3b sul branch `feat/sp3b-design` (già su origin, PR non ancora aperta); rifinitura visiva del 2026-11-08 implementata e non committata
- Goal: prova dell'utente (`uv run fmxray-gui`), commit, push, PR
- Last completed step: Task 7 del [piano di rifinitura](../../docs/superpowers/plans/2026-11-08-sp3b-rifinitura-visiva.md)
- Current branch: `feat/sp3b-design`
- Worktree: dirty (rifinitura: `src`, `tests`, `wiki`, spec e piano del 2026-11-08, Inter al posto di Figtree in `src/fmxray/ui/fonts/`)

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | Prova dell'utente, commit e PR di SP3b | [ui](../modules/ui.md), `local/pr-sp3b.md` | PR aperta, CI verde | `gh pr checks` | la scheda è QML: se su un PC non si vede, guardare l'errore mostrato nella scheda |
| 2 | SP4 storico e newgen: brainstorming | spec madre §9, §12 | spec SP4 approvata | Not verified - documento | V5/V7 servono un nuovo `Roma.fm` |

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
| `uv run pytest` | repo | 209 passed | save reale incluso (2026-11-06) |
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
