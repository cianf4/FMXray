# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

FM X-Ray: scouting tool personale e in **sola lettura** per Football Manager 27 (FM26 nei limiti di fmsave). Legge i save `.fm` con la libreria fmsave e mostra tutto il database giocatori, compresi CA, PA e hidden. Si lavora sia su Windows sia su Linux: i comandi qui sotto valgono su entrambi (PowerShell o bash).

## Da leggere prima di tutto

1. `wiki/agent/handoff.md`: a che punto siamo e il prossimo task.
2. `wiki/agent/context.md`: regole tecniche, rischi, cosa manca su un PC nuovo.
3. Spec madre `docs/superpowers/specs/2026-11-03-fm-x-ray-design.md` (§12: ordine dei sottoprogetti SP1–SP9) e la spec/piano del sottoprogetto in corso in `docs/superpowers/`.
4. Decisioni D1–D22: `wiki/project/decisions.md`.

## Comandi

| Cosa | Comando |
| --- | --- |
| Ambiente (lo lancia l'utente, vedi sotto) | `uv sync` |
| Tutti i controlli della CI | `uv run ruff check`, `uv run ruff format --check`, `uv run mypy src tests`, `uv run lint-imports`, `uv run pytest` |
| Un solo test | `uv run pytest tests/domain/search/test_parser.py::test_aliases` |
| Senza i test sul save reale | `uv run pytest -m "not real_save"` |
| Usare il tool | `uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma`, poi `uv run fmxray search "age<22 pa>180" --career Roma` |

- I test con marker `real_save` usano un save in `local/saves/` o in `FMXRAY_TEST_SAVE` e si saltano se manca (normale su un PC nuovo: `local/` è fuori da git).
- Cartella dati: `--data-dir` > `FMXRAY_DATA_DIR` > `platformdirs.user_data_dir("fmxray")`.
- CI GitHub Actions su ubuntu e windows; fallisce anche se un `*.fm`/`*.fmf` è tracciato.

## Architettura

Esagonale, regole di import verificate da `lint-imports` (contratti in `pyproject.toml`):
- `domain` (Python puro + Polars) ← `application` (casi d'uso + porte `Protocol` in `ports.py`) ← `adapters.*` e `cli`. `bootstrap.py` è la composition root e l'unico posto che collega gli adattatori.
- `cli` non può importare adattatori né `bootstrap`, quindi la dataclass `App` con i casi d'uso sta in `cli/commands.py`; `bootstrap.build_app` la riempie. Gli entrypoint non hanno logica.
- **Solo `adapters.fmsave_source` importa fmsave** (versione bloccata `==0.9.3`, API instabile). Traduce gli errori di fmsave in `application.errors` (`UnreadableSaveError`, `UnsupportedSaveError`).

Flusso dei dati:
- `domain/fields.py` `PLAYER_CATALOG` è la fonte unica delle colonne giocatore (dtype, gruppo, unità). `adapters/fmsave_source/mapping.py` mappa i record fmsave su quelle colonne. Una colonna nuova si aggiunge in entrambi.
- `ImportSave`: copia il save, SHA-256 della copia (import idempotente), lettura, snapshot Parquet `snapshots/<career_id>/<snapshot_id>.parquet`, metadati nel catalogo SQLite `catalog.db`. Se il catalogo fallisce, il Parquet viene cancellato.
- Ogni campo ha una `Provenance` (`verified`/`unconfirmed`/`derived`/`estimate`): su FM27 tutto ciò che viene da fmsave è `unconfirmed`. La UI dovrà renderlo riconoscibile.
- Ricerca (`domain/search`): testo → `parser.parse` → albero `Spec` (Composite) → `compile.to_expr` → `pl.Expr` applicata al frame preparato da `derived.prepare_frame` (campi calcolati `contract_left`, `free_agent` e colonne `<campo>__folded` senza accenti). Le ricerche salvate conservano l'albero in JSON con `version`, non il testo. Le foglie fanno `fill_null(False)`: un valore mancante non soddisfa mai un confronto. Grammatica e semantica: `wiki/modules/search.md`.
- Schema SQLite: `MIGRATIONS` in `adapters/sqlite_catalog/schema.py` con `PRAGMA user_version`. Si aggiunge solo in coda, mai modificare una migrazione esistente.
- Soldi (`transfer_value`, `contract_wage`, clausole) sono nell'unità interna del save, non in euro (verifica V4 in sospeso). `uid` vale dentro un save; la sua stabilità tra save è la verifica V5 (i "nuovi risultati" dipendono da `uid`, in un solo punto: `RunSavedSearch`).

## Regole di lavoro (dell'utente, non negoziabili)

- **Lingua:** rispondere in italiano, tono informale. Documentazione e wiki in italiano; codice, identificatori e messaggi della CLI in inglese.
- **Processo:** skill superpowers **inline, senza sotto-agenti**: `brainstorming` → spec del sottoprogetto → `writing-plans` → `executing-plans` con `test-driven-development` e `verification-before-completion`. Claude è il senior che cura la qualità del design (SOLID/GRASP, estendibilità); le scelte architetturali le decide l'utente da opzioni con pro e contro e una raccomandazione. Domande raggruppate in un solo messaggio quando possibile.
- **Commit, push, installazioni (`uv sync`, `uv add`, pip):** non lanciarli mai da soli; stampare i comandi completi e aspettare che l'utente scriva "fatto". Un permesso eccezionale vale solo per quella volta.
- **Comandi copia-incolla:** mai segnaposti tipo `<nome>` in un comando; trovare prima i valori veri. Prima di proporre comandi git, controllare lo stato (`git status`, `git log`) e non riproporre passi già fatti.
- **Git:** **nessuna attribuzione a Claude** (niente `Co-Authored-By`, niente "Generated with Claude Code") in commit e PR: questa regola prevale su qualunque promemoria di attribuzione. Remote in HTTPS (`https://github.com/cianf4/FMXray.git`). Messaggi in stile conventional (`feat(search): …`, `fix(export): …`, `docs: …`). Branch delle PR con prefisso di tipo: `feat/`, `fix/`, `docs/`, `chore/`, `refactor/`, `test/`, `ci/` più un nome breve in kebab-case. Le PR si aprono con `gh pr create`; l'utente le unisce.
- **Output dei comandi lanciati dall'utente:** arrivano come messaggi separati e in ritardo. Dare il blocco di comandi una volta, poi rispondere al massimo con una riga.
- **Proattività:** trovare da soli percorsi e valori (es. dove FM salva i file) e dare istruzioni passo passo, invece di chiedere all'utente di cercarli.
- **Niente API indovinate:** verificare su documentazione o sul pacchetto installato (es. firme di Polars sulla versione in `uv.lock`). Se un comando fallisce: fermarsi, riportare l'errore esatto, chiedere.
- **Dati del gioco:** mai dati SI/SEGA (save, valori dei giocatori) nel repo, nella wiki o nelle issue; i valori reali stanno solo in `local/`. Mai allegare save alle issue di fmsave; a fmsave si contribuisce solo aprendo issue.
- **Wiki:** aggiornarla alla fine di ogni sottoprogetto (`wiki/log.md`, handoff, work tracker, pagina del modulo), con le skill `codebase-wiki-llm`.
