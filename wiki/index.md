---
title: Indice della wiki
updated: 2026-10-31
sources:
  - wiki/SCHEMA.md
source_commit: unknown
confidence: high
---

# Indice della wiki

## Overview

| Pagina | Contenuto |
| --- | --- |
| [Overview](overview.md) | cos'è FM X-Ray e dove guardare |
| [Scheda di progetto](overview-fm-x-ray.md) | scheda portabile + Personal Wiki Export |
| [Schema](SCHEMA.md) | convenzioni di questa wiki |
| [Log](log.md) | changelog delle operazioni sulla wiki |
| [Glossario](glossary.md) | CA, PA, hidden, newgen, ID, BepInEx, … |

## Engineering

| Pagina | Stato |
| --- | --- |
| [Architettura](engineering/architecture.md) | strati e contratti di import |
| [Modello dati](engineering/data-model.md) | snapshot e catalogo |
| [Sviluppo](engineering/development.md) | comandi |
| [Testing](engineering/testing.md) | livelli di test e CI |
| [Operations](engineering/operations.md) | stub |
| [Troubleshooting](engineering/troubleshooting.md) | problemi documentati da fmsave |
| [Mappa delle modifiche](engineering/change-map.md) | dove intervenire |

## Modules

| Pagina | Stato |
| --- | --- |
| [Moduli](modules/README.md) | indice |
| [domain](modules/domain.md) | catalogo campi, snapshot |
| [search](modules/search.md) | filtri, barra a testo, ricerche salvate |
| [application](modules/application.md) | porte, ImportSave, ShowPlayer, SearchPlayers |
| [fmsave-source](modules/fmsave-source.md) | unico punto che legge fmsave |
| [parquet-store](modules/parquet-store.md) | snapshot su Parquet |
| [sqlite-catalog](modules/sqlite-catalog.md) | catalogo su SQLite |
| [cli](modules/cli.md) | comandi e composition root |

## Project

| Pagina | Contenuto |
| --- | --- |
| [Stato](project/status.md) | dove siamo |
| [Work tracker](project/work-tracker.md) | lavoro attivo, pianificato, completato, bloccato |
| [Roadmap](project/roadmap.md) | Fasi 1–3 |
| [Milestone](project/milestones.md) | date esterne (FM27) |
| [Rischi](project/risks.md) | K1–K11 |
| [Requisiti](project/requirements.md) | R1–R11, V1–V4, N1–N6 |
| [Decisioni](project/decisions.md) | D1–D11 e temi aperti |

## Project Docs

| Pagina | Stato |
| --- | --- |
| [Project brief](project-docs/project-brief.md) | popolata |
| [Casi d'uso](project-docs/use-cases.md) | popolata |
| [Pubblico](project-docs/audience.md) | popolata |
| [Proposta di valore](project-docs/value-proposition.md) | ipotesi |
| [Evidenze](project-docs/evidence.md) | lacune e ipotesi |
| [Impatto](project-docs/impact.md) | stub |
| [Materiale per demo](project-docs/demo-materials.md) | stub |
| [FAQ](project-docs/faq.md) | popolata |

## Agent

| Pagina | Contenuto |
| --- | --- |
| [Context](agent/context.md) | onboarding rapido per agenti |
| [Handoff](agent/handoff.md) | testimone per la prossima sessione |
| [Activity](agent/activity.md) | log append-only |

## Reference

| Pagina | Contenuto |
| --- | --- |
| [fmsave](reference/fmsave.md) | cosa legge fmsave 0.9.0, limiti, politica dei contributi |
| [Prior art](reference/prior-art.md) | FMSuperScout, Genie Scout, FM-Arena, FM26-Analyst, fm26rte |
