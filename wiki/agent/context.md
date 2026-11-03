---
title: Agent Context
updated: 2026-11-03
sources:
  - wiki/index.md
  - wiki/project/decisions.md
  - wiki/project/requirements.md
  - wiki/reference/fmsave.md
source_commit: 2025c37
confidence: medium
---

# Agent Context

## Project Snapshot

- Project: FM X-Ray
- Purpose: scouting tool personale e in sola lettura per FM27 (FM26 nei limiti di fmsave) che legge i save e mostra tutto il database giocatori, compresi CA, PA e hidden. Fonte: [project brief](../project-docs/project-brief.md)
- Current status: SP1 (Fondamenta) implementato sul branch `sp1-fondamenta` ([stato](../project/status.md))
- Primary languages/frameworks: Python 3.14, fmsave 0.9.3, Polars 2.x, SQLite; UI PySide6 da SP3
- Main runtime/deploy target: app desktop locale, Windows e Linux

## Architecture At A Glance

| Area | Purpose | Start here |
| --- | --- | --- |
| Fonte dati (fmsave) | lettura del save, dietro un unico adattatore | [architettura](../engineering/architecture.md), [fmsave](../reference/fmsave.md) |
| Fonte dati RAM (Fase 3) | seconda fonte dello stesso modello | [decisioni](../project/decisions.md) D6 |
| Moduli | domain, application, adapters, cli | [moduli](../modules/README.md) |

## Non-Negotiable Technical Rules

- Sola lettura, nessuna rete, nessun dato di SI/SEGA nel repo, nelle issue o nella wiki - Source: D1 in [decisioni](../project/decisions.md)
- Solo l'adattatore importa fmsave; versione di fmsave bloccata - Source: D2, D3
- Processo superpowers inline (niente subagent): brainstorming → spec → piano → `executing-plans` + TDD - Source: D8
- Documentazione in italiano, codice in inglese - Source: D8
- Niente `git commit`/`push` né `pip`/`uv` install automatici: stampare il comando per l'utente - Source: CLAUDE.md dell'utente
- Niente API indovinate: verificare sulla documentazione - Source: CLAUDE.md dell'utente

## Core Commands

| Task | Command | Working directory | Evidence |
| --- | --- | --- | --- |
| Setup | `uv sync` (la lancia l'utente) | `.` | `pyproject.toml` |
| Test | `uv run pytest` | `.` | `pyproject.toml` |
| Lint | `uv run ruff check && uv run ruff format --check && uv run mypy src tests && uv run lint-imports` | `.` | `.github/workflows/ci.yml` |
| Build | Not verified - nessun eseguibile prima di SP8 | `.` | spec madre §11 |
| Importare un save | `uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma` | `.` | `src/fmxray/cli/commands.py` |
| Ispezione rapida di un save | `uv run fmsave info "local/saves/fm27/Roma.fm"` | `.` | [README fmsave](https://github.com/rhiever/fmsave) |

## Read First

1. [Master index](../index.md)
2. [Decisioni](../project/decisions.md)
3. [Requisiti](../project/requirements.md)
4. [fmsave](../reference/fmsave.md)
5. [Current handoff](handoff.md)

## Risks And Invariants

| Risk / invariant | Why it matters | Evidence |
| --- | --- | --- |
| API di fmsave instabile | rompe la lettura a ogni aggiornamento non controllato | K1 in [rischi](../project/risks.md) |
| `uid` vale solo dentro un save; `unique_id` può essere `None` | join e confronti tra carriere sbagliati | K10 |
| Campi "unconfirmed" in fmsave | valori mostrati come certi senza esserlo | K3 |

## High-Value Links

- [Project status](../project/status.md)
- [Work tracker](../project/work-tracker.md)
- [Decisions](../project/decisions.md)
- [Prior art](../reference/prior-art.md)
