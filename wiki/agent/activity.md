---
title: Agent Activity
updated: 2026-10-31
sources:
  - wiki/log.md
source_commit: unknown
confidence: high
---

# Agent Activity

Log append-only.

## 2026-10-31 - Claude Code (Opus 5.5) - wiki init

- **Trigger:** `/codebase-wiki-llm:wiki-init` lanciato dall'utente durante il brainstorming.
- **Intent:** salvare contesto e decisioni prima di scrivere la spec madre.
- **Actions:** ricerca online (fmsave 0.9.0, FMSuperScout, Genie Scout 26, FM-Arena, FM26-Analyst, fm26rte, data di uscita di FM27); lettura della struttura di Quizard come modello di processo; creazione della wiki.
- **Files changed:** tutta `wiki/` (nuova).
- **Validation:** Not verified - nessun codice; i fatti esterni sono citati con URL.
- **Decisions:** D1–D9 in [decisioni](../project/decisions.md).
- **Follow-up:** chiudere i temi aperti, spec madre, verifiche V1–V4 su un save reale, `/wiki-lint`.

## 2026-11-03 - Claude Code (Opus 5.5) - spec madre

- **Trigger:** l'utente approva in blocco le raccomandazioni ("vai").
- **Actions:** scritta la spec madre; rilettura inline al posto del builder check con sotto-agente; decisioni D12–D20 in wiki.
- **Follow-up:** revisione utente; lingua UI e repo da confermare; poi SP1.

## 2026-11-03 - Claude Code (Opus 5.5) - esecuzione SP1

- **Trigger:** piano SP1 approvato.
- **Actions:** Task 1–8 con TDD inline (executing-plans); import del save reale; wiki dei moduli.
- **Validation:** `uv run pytest` → 55 passed (incluso il save reale); ruff, mypy, lint-imports puliti.
- **Decisions:** rulings nel ledger di esecuzione (record incompleti di fmsave, `App` in `cli`, dati dei giocatori solo in `local/`).
- **Follow-up:** V1/V4 (confronto nel gioco), V5/V7 (nuovo save), revisione finale, merge, SP2.

## 2026-11-04 - Claude Code (Opus 5.5) - chiusura SP1

- **Actions:** fix CI (setup-uv v10.3.3), fix errori fmsave non tradotti, PR #1 creata con `gh`, unita dall'utente.
- **Validation:** CI verde su ubuntu-latest e windows-latest.
- **Follow-up:** SP2.

## 2026-11-04 - Claude Code (Opus 5.5) - esecuzione SP2

- **Trigger:** piano SP2 approvato ("vai, procedi").
- **Actions:** Task 1–8 con TDD inline; verifica sul save reale (`search "age<22 pa>180"`, `search "finishng>15"` → suggerisce `finishing`).
- **Validation:** `uv run pytest` → 117 passed (save reale incluso); ruff, mypy, lint-imports puliti; ricerca sul save reale 2–8 ms.
- **Decisions:** rulings nel ledger (posizione in `UnknownFieldError`, controllo dei tipi nel parser, `find_snapshot`, alias anche in `--columns`, commit raggruppati).
- **Follow-up:** commit e push dall'utente, CI, PR; V5 decide se `uid` basta per i "nuovi risultati".

## 2026-11-06 - Claude Code (Opus 5.5) - wiki portatile

- **Trigger:** l'utente vuole poter continuare dal PC aziendale (Windows).
- **Intent:** un Claude nuovo deve capire stato, storia e prossimi passi dal solo repo.
- **Actions:** `wiki-sync` (stato SP2 chiuso, SP3 in brainstorming, sezione "Su un PC nuovo" in context); `CLAUDE.md` con le regole di lavoro imparate nella chat.
- **Files changed:** pagine elencate nel log del 2026-11-06, `CLAUDE.md`.
- **Validation:** Not verified - solo documentazione.
- **Decisions:** le regole di lavoro stanno in `CLAUDE.md` del repo, non solo nella memoria locale di Claude.
- **Follow-up:** brainstorming SP3.

## 2026-11-06 - Claude Code (Opus 5.5) - esecuzione SP3

- **Trigger:** piano SP3 approvato; dipendenze installate dall'utente (`uv add`).
- **Actions:** Task 1–10 inline con TDD; misure sul save reale (apertura ~1 s, filtri 13–100 ms).
- **Validation:** `uv run pytest` → 209 passed (save reale incluso); ruff, mypy, lint-imports (7 contratti) puliti.
- **Decisions:** D23–D25; rulings nel ledger (spin box invece di un cursore a due maniglie, watcher a polling, `list_careers`, scheda dalla riga del risultato).
- **Follow-up:** prova a mano dell'utente, commit, PR, SP3b.

## 2026-11-07 - Claude Code (Opus 5.5) - SP3b design grafico

- **Trigger:** utente: "troppe informazioni a schermo", riordino e grafica.
- **Actions:** tre mockup (A Claude, B impeccable con dado e7d2b799, C taste-skill data-terminal); scelta A con il blu di C; QtAwesome e font inclusi su richiesta; riordino, chip, linguette, barra laterale, densità, animazioni; screenshot offscreen confrontati con il mockup.
- **Validation:** `uv run pytest` → 247 passed (save reale incluso); ruff, mypy, lint-imports puliti.
- **Decisions:** D26; rulings nel ledger (una sola nota "unconfirmed" invece dei segni per colonna, scheda a due blocchi per riga).
- **Follow-up:** prova dell'utente, PR, SP4.

## 2026-11-08 - Claude Code (Opus 5.5) - SP3b rifinitura visiva

- **Trigger:** prova dell'utente: spazio vuoto a schermo intero, stile lontano dal mockup, font sgranati, animazioni a scatti; richiesta di esagono e più abbellimenti.
- **Actions:** cause trovate con screenshot a 1920 px; spec e piano `2026-11-08-sp3b-rifinitura-visiva`; Task 1–7 inline con TDD (Inter e token, `domain/profile.py`, tabella, filtri rapidi, barra sovrapposta, scheda QML).
- **Validation:** `uv run pytest` → 271 passed (save reale incluso); ruff, mypy, lint-imports puliti; wheel con `ui/qml/*.qml` e Inter.
- **Decisions:** D27; rulings nel ledger (ombre senza `MultiEffect`, spazio della tabella diviso in proporzione invece che tutto a Name, testo QML con rendering nativo).
- **Follow-up:** prova dell'utente, commit, PR, SP4.
- **2026-11-08, dopo la prova:** nomi e valori enum senza underscore in stile FM (`humanize`), valori in azzurrino `#a8d4ff`; errori QML in chiusura corretti (modello figlio della vista). `uv run pytest` → 275 passed.
