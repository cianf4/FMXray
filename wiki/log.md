---
title: Log della wiki
updated: 2026-10-31
sources:
  - wiki/index.md
source_commit: unknown
confidence: high
---

# Log della wiki

## [2026-10-31] init | bootstrapped wiki
- Scope: wiki di FM X-Ray durante il brainstorming, prima di qualsiasi codice
- Wiki root: wiki/
- Pages created: 34
- Modules: nessuno (placeholder `modules/README.md`)
- Project/project-docs pages populated: status, work-tracker, roadmap, risks, requirements, decisions, project-brief, use-cases, audience, faq; ipotesi in value-proposition ed evidence
- Agent continuity: context, handoff, activity, work tracker
- Portable overview: overview-fm-x-ray.md
- Extra: reference/fmsave.md, reference/prior-art.md (ricerche del 2026-10-31)
- Proposed for retirement: none
- Follow-up: run /wiki-lint to verify coverage

## [2026-11-03] sync | spec madre
- Decisioni D12–D20 aggiunte; handoff e stato aggiornati alla spec madre `docs/superpowers/specs/2026-11-03-fm-x-ray-design.md`
- [2026-11-03] sync | reference/fmsave.md: verifiche su Roma.fm (FM27, fmsave 0.9.3)
- [2026-11-03] sync | D7 → FM27 obiettivo principale; spec SP1 scritta

## [2026-11-03] ingest | SP1 Fondamenta
- Moduli: domain, application, fmsave-source, parquet-store, sqlite-catalog, cli
- Engineering popolate: architecture, data-model, development, testing, change-map
- Verifiche: V2, V3, V6 registrate; V1, V4, V5, V7 in attesa

## [2026-11-04] sync | chiusura SP1
- PR #1 unita in `main` (merge `95075b9`); D16 aggiornata a Python 3.14; stato, work tracker e handoff puntano a SP2

## [2026-11-04] ingest | SP2 Motore di ricerca
- Nuova pagina: modules/search.md (grammatica, semantica, invarianti)
- Aggiornate: modules/README, application, cli, sqlite-catalog; engineering/change-map; project/status, work-tracker; agent/handoff, activity; index

## [2026-11-06] sync | 7 pages updated
- Changed files: PR #2 e #3 unite in `main` (nessun file sorgente nuovo)
- Pages updated: project/status, project/work-tracker, agent/handoff, agent/context, engineering/development, overview-fm-x-ray, agent/activity
- Follow-ups: `CLAUDE.md` alla radice con le regole di lavoro; brainstorming SP3

## [2026-11-06] ingest | SP3 Interfaccia
- Nuova pagina: modules/ui.md
- Aggiornate: modules/README, application, sqlite-catalog, search; engineering/architecture, testing, development, change-map; project/decisions (D23–D25), status, work-tracker; agent/handoff, activity; index
