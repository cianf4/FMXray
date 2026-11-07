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

- Status: SP3 implementato sul branch `feat/sp3-interfaccia`, non ancora committato (tranne spec e piano, `40320d5`)
- Goal: prova a mano dell'utente, commit, push, CI, PR di SP3
- Last completed step: Task 10 del [piano SP3](../../docs/superpowers/plans/2026-11-06-sp3-interfaccia.md) (test GUI sul save reale, wiki)
- Current branch: `feat/sp3-interfaccia`
- Last commit: `40320d5` (spec e piano di SP3)
- Worktree: dirty (tutto SP3: `src`, `tests`, `wiki`, `pyproject.toml`, `uv.lock`, CI)

## Baton For Next Coding Agent

| Order | Task | Start files | Done when | Verification command | Notes / blockers |
| --- | --- | --- | --- | --- | --- |
| 1 | L'utente prova `uv run fmxray-gui` (filtri, popup, ruoli, scheda, ricerche salvate, viste, export, "Watch folder…" con un salvataggio di FM) | [ui](../modules/ui.md) | l'utente conferma o segnala problemi | `uv run fmxray-gui` | le correzioni con TDD prima dei commit |
| 2 | Commit raggruppati, push, PR con `gh pr create` | `local/pr-sp3.md` | CI verde su Linux e Windows | `gh pr checks` | i test Qt in CI Linux usano `libegl1 libxkbcommon0 libgl1` |
| 3 | SP3b design grafico: brainstorming | `src/fmxray/ui/theme.py`, spec madre §12 | spec SP3b approvata | Not verified - documento | tre proposte: Claude, impeccable, taste-skill |

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
