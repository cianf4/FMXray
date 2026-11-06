---
title: Agent Context
updated: 2026-11-06
sources:
  - wiki/index.md
  - wiki/project/decisions.md
  - wiki/project/requirements.md
  - wiki/reference/fmsave.md
source_commit: 9bfc8a1
confidence: medium
---

# Agent Context

## Project Snapshot

- Project: FM X-Ray
- Purpose: scouting tool personale e in sola lettura per FM27 (FM26 nei limiti di fmsave) che legge i save e mostra tutto il database giocatori, compresi CA, PA e hidden. Fonte: [project brief](../project-docs/project-brief.md)
- Current status: SP1 e SP2 chiusi in `main`; SP3 (interfaccia) in brainstorming ([stato](../project/status.md))
- Primary languages/frameworks: Python 3.14, fmsave 0.9.3, Polars 2.x, SQLite; UI PySide6 da SP3
- Main runtime/deploy target: app desktop locale, Windows e Linux

## Architecture At A Glance

| Area | Purpose | Start here |
| --- | --- | --- |
| Fonte dati (fmsave) | lettura del save, dietro un unico adattatore | [architettura](../engineering/architecture.md), [fmsave](../reference/fmsave.md) |
| Fonte dati RAM (Fase 3) | seconda fonte dello stesso modello | [decisioni](../project/decisions.md) D6 |
| Moduli | domain (incluso `domain.search`), application, adapters, cli | [moduli](../modules/README.md) |

## Non-Negotiable Technical Rules

- Sola lettura, nessuna rete, nessun dato di SI/SEGA nel repo, nelle issue o nella wiki - Source: D1 in [decisioni](../project/decisions.md)
- Solo l'adattatore importa fmsave; versione di fmsave bloccata - Source: D2, D3
- Processo superpowers inline (niente subagent): brainstorming → spec → piano → `executing-plans` + TDD - Source: D8
- Documentazione in italiano, codice in inglese - Source: D8
- Niente `git commit`/`push` né `pip`/`uv` install automatici: stampare il comando per l'utente - Source: CLAUDE.md dell'utente
- Niente API indovinate: verificare sulla documentazione - Source: CLAUDE.md dell'utente
- Regole di lavoro complete (comandi, git, branch, comunicazione): `CLAUDE.md` alla radice del repo

## Core Commands

| Task | Command | Working directory | Evidence |
| --- | --- | --- | --- |
| Setup | `uv sync` (la lancia l'utente) | `.` | `pyproject.toml` |
| Test | `uv run pytest` | `.` | `pyproject.toml` |
| Lint | `uv run ruff check && uv run ruff format --check && uv run mypy src tests && uv run lint-imports` | `.` | `.github/workflows/ci.yml` |
| Build | Not verified - nessun eseguibile prima di SP8 | `.` | spec madre §11 |
| Importare un save | `uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma` | `.` | `src/fmxray/cli/commands.py` |
| Cercare | `uv run fmxray search "age<22 pa>180" --career Roma` | `.` | [search](../modules/search.md) |
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

## Su un PC nuovo

- `local/` è fuori da git: niente save, niente scheda V1/V4, niente testi delle PR. I test con marker `real_save` vengono saltati: è normale.
- Per i test sul save reale: copiare un `.fm` in `local/saves/fm27/` oppure impostare `FMXRAY_TEST_SAVE`. Su Windows i save di FM27 stanno in `%LOCALAPPDATA%\Sports Interactive\Football Manager 27\` (cartella esatta: Not verified su Windows).
- Cartella dati dell'app: `platformdirs.user_data_dir("fmxray")` (su Windows sotto `%LOCALAPPDATA%`); la si cambia con `--data-dir` o `FMXRAY_DATA_DIR`.

## High-Value Links

- [Project status](../project/status.md)
- [Work tracker](../project/work-tracker.md)
- [Decisions](../project/decisions.md)
- [Prior art](../reference/prior-art.md)
