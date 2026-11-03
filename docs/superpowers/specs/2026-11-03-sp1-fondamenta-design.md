# SP1 — Fondamenta: design

> Sottoprogetto 1 della [spec madre](2026-11-03-fm-x-ray-design.md) (§12). Dopo l'approvazione di questa spec: `superpowers:writing-plans` → `docs/superpowers/plans/2026-11-03-sp1-fondamenta.md` → `superpowers:executing-plans` con TDD.

## Intento

Mettere in piedi lo scheletro su cui poggia tutto il resto. Alla fine di SP1 un comando da terminale legge un save FM27 reale, lo trasforma in uno snapshot nel nostro formato e lo registra nel catalogo, con la CI verde su Linux e Windows. In più raccogliamo le risposte alle verifiche V1–V7 che decidono i dettagli di SP2 e SP3.

## Obiettivi

1. Progetto uv con layout `src/fmxray`, strumenti di qualità e CI su GitHub Actions (Linux + Windows).
2. Pacchetti `domain`, `application`, `adapters`, `cli`, `bootstrap` con le **regole di import verificate** in CI.
3. **Catalogo dei campi** nel dominio: nome, tipo, gruppo, unità, provenienza.
4. **Adattatore fmsave**: unico punto che importa fmsave; da un save produce metadati + DataFrame Polars con le nostre colonne.
5. **Snapshot store** su Parquet e **catalogo** su SQLite.
6. Caso d'uso **ImportSave**: copia del save, hash, salto se già importato, lettura, scrittura dello snapshot, registrazione.
7. CLI: `fmxray import`, `fmxray snapshots`, `fmxray show`.
8. Verifiche V1–V7 registrate nella wiki.

## Non obiettivi (restano ad altri sottoprogetti)

- Filtri, ricerca, CSV (SP2). Interfaccia grafica, watcher della cartella, PySide6 (SP3). Sfoltimento dello storico e newgen (SP4). Rating, proiezioni, asking price (SP5–SP7). Eseguibili (SP8).
- Conversione dei soldi nella valuta mostrata: in SP1 si misura il fattore (V4), non si applica.

## Anti-obiettivi (sarebbe un fallimento anche se funzionasse)

- Un tipo o un modulo di fmsave visibile fuori da `fmxray.adapters.fmsave_source`.
- Logica dentro `__main__` o nei comandi CLI invece che nei casi d'uso.
- Un save o dati di gioco tracciati da git, anche come fixture di test.
- Un import che, se fallisce a metà, lascia uno snapshot parziale registrato nel catalogo.

## Vincoli

- **Python 3.14** *(mia proposta, era 3.13 nella spec madre)*: tutte le dipendenze hanno wheel per la 3.14 (PySide6 6.12 abi3 fino a <3.16, Polars, pyarrow, mypy, Hypothesis) e fmsave sulla 3.14 usa lo zstd della libreria standard invece di `backports-zstd`. Fallback 3.13.
- **Dipendenze di runtime, versioni esatte nel lock:** `fmsave==0.9.3`, `polars` 2.x, `platformdirs`. Niente pandas, niente pyarrow se Polars basta per Parquet (da verificare nel piano).
- **Dipendenze di sviluppo:** `ruff`, `mypy`, `pytest`, `hypothesis`, `import-linter`.
- **Installazioni:** le lancia l'utente (`uv sync`); il piano le stampa, non le esegue.
- Codice e identificatori in inglese, documentazione in italiano; niente segnaposti nei comandi; niente attribuzioni a Claude nei commit.
- **Polars 2.x** è una major nuova: ogni API usata va controllata nella documentazione della versione bloccata.
- **fmsave**: le API usate (`fmsave.open`, `Save.info` → `SaveInfo.game/build/known_build/db_version/game_date`, `Save.players()`, `Table.to_polars()`, `fmsave.field_status`, eccezioni `UnsupportedGameError`, `ReaderCheckError`, `CorruptSaveError`, `UnknownBuildWarning`) vanno verificate nel pacchetto installato prima di scrivere l'adattatore.

## Decisioni

### Layout e regole di import (spec madre §3)

```text
src/fmxray/
├── __main__.py            # solo: from fmxray.bootstrap import main; main()
├── bootstrap.py           # composition root
├── domain/
│   ├── fields.py          # FieldSpec, FieldCatalog, Provenance
│   └── snapshot.py        # SnapshotMeta, Snapshot (meta + pl.DataFrame)
├── application/
│   ├── ports.py           # SaveSource, SnapshotStore, CatalogStore (Protocol)
│   ├── errors.py          # errori applicativi (save illeggibile, build non supportata, …)
│   └── import_save.py     # caso d'uso ImportSave
├── adapters/
│   ├── fmsave_source/     # l'unico che importa fmsave
│   ├── parquet_store/
│   └── sqlite_catalog/
└── cli/
    └── commands.py        # argparse → casi d'uso
```

Contratti import-linter: `domain` non importa nulla del progetto; `application` solo `domain`; `cli` solo `application` e `domain`; `fmsave` importabile solo da `fmxray.adapters.fmsave_source`; nessun adattatore importa un altro adattatore.

### Modello (design)

- **`Provenance`**: `VERIFIED`, `UNCONFIRMED`, `DERIVED`, `ESTIMATE`.
- **`FieldSpec`**: nome della colonna nostra, tipo Polars, gruppo (identity, club, ability, technical, mental, physical, goalkeeping, hidden, personality, contract, value, …), unità (`raw_1_100`, `display_1_20`, `money_internal`, `cm`, `date`, …).
- **`FieldCatalog`**: l'elenco ufficiale delle nostre colonne; la provenienza di ogni campo **dipende dallo snapshot** (build e versione di fmsave), quindi viaggia nei metadati dello snapshot, non nel catalogo statico.
- **`SnapshotMeta`**: `snapshot_id`, `career_id`, `game` (FM26/FM27), `build`, `known_build`, `db_version`, `game_date`, `imported_at`, `source_sha256`, `source_kind` (`fmsave`), `reader_version` (versione di fmsave), `row_count`, provenienze per campo.
- **Colonne**: un sottoinsieme curato dei 218 campi piatti di fmsave, rinominati nei nostri nomi stabili. Fuori i campi `unknown_*`. Attributi in tutte e due le scale. Soldi nell'unità interna.

### Storage (design, spec madre §5)

- Cartella dati da `platformdirs.user_data_dir("fmxray")`, sovrascrivibile con `--data-dir` o `FMXRAY_DATA_DIR` (usata dai test).
- `snapshots/<career_id>/<snapshot_id>.parquet` (zstd) + metadati nel catalogo SQLite.
- Scrittura **atomica**: file temporaneo nella stessa cartella → rename → riga nel catalogo in una transazione. Se il catalogo fallisce, il file viene rimosso.
- Schema SQLite versionato con `PRAGMA user_version` e migrazioni in codice (SP1: versione 1 con `careers` e `snapshots`).

### Import (design)

1. Calcola SHA-256 del file; se già nel catalogo per quella carriera → "già importato", esce.
2. Copia il save in una cartella temporanea e legge la copia.
3. Apre con fmsave (`strict` off per FM26, i controlli FM27 sono comunque bloccanti); intercetta `UnknownBuildWarning` e lo registra nei metadati.
4. Converte `players()` in DataFrame con le nostre colonne, valida lo schema contro il `FieldCatalog`.
5. Scrive lo snapshot e lo registra.

Gli errori di fmsave vengono tradotti in errori applicativi solo dentro l'adattatore.

### CLI (design)

| Comando | Effetto |
| --- | --- |
| `fmxray import SAVE --career NOME` | importa un save in una carriera (la crea se non esiste) |
| `fmxray snapshots [--career NOME]` | elenca gli snapshot con data di gioco, build, righe |
| `fmxray show NOME_GIOCATORE [--snapshot ID]` | stampa tutti i campi di un giocatore raggruppati, con la provenienza: serve per le verifiche nel gioco |

### Test (utente: tre livelli; design: dettagli)

- **Dominio e applicazione:** factory che generano DataFrame sintetici validi per il `FieldCatalog`; fake in memoria delle porte; Hypothesis sulle invarianti (schema rispettato, import idempotente).
- **Adattatore fmsave:** il modulo fmsave viene sostituito da un fake con la stessa forma (oggetto `Save` con `info`, `players()` che restituisce un oggetto con `to_polars()`), così i test girano senza save.
- **Integrazione:** marker `real_save`; il test cerca il save in `FMXRAY_TEST_SAVE` o in `local/saves/**/*.fm` e si salta se non c'è. In CI non c'è mai.
- **Store:** Parquet e SQLite testati su cartelle temporanee (`tmp_path`).

### CI

GitHub Actions, matrice `ubuntu-latest` + `windows-latest`: `uv sync --locked`, `ruff check`, `ruff format --check`, `mypy --strict`, `lint-imports`, `pytest`, e un passo che fallisce se `git ls-files` contiene `*.fm` o `*.fmf`.

### Verifiche V1–V7 (design: come)

| ID | Come | Chi |
| --- | --- | --- |
| V1 | `fmxray show` su 4 giocatori della Roma; confronto con la loro scheda nel gioco (attributi, piede, ruoli, contratto, valore). CA e hidden si confrontano con lo stesso giocatore visto in fmsave web app solo come controllo incrociato | utente nel gioco, Claude prepara la tabella |
| V2 | elenco dei `ClauseKind` presenti nel save e confronto con 2 clausole viste nel gioco | Claude + utente |
| V3 | tempo di `fmxray import` e dimensione del Parquet | Claude |
| V4 | rapporto tra `transfer_value`/`wage` e i valori mostrati nel gioco per 4 giocatori | utente nel gioco |
| V5 | importare il prossimo `Roma.fm` dopo una sessione di gioco e confrontare `uid` e `unique_id` | utente gioca, Claude confronta |
| V6 | fatto: `SaveInfo.game_date` = 2026-09-12 | — |
| V7 | sullo stesso confronto di V5: le persone nuove hanno `unique_id` nuovo, `None` o riusato? | Claude |

I risultati vanno in `wiki/reference/fmsave.md`; quelli che smentiscono fmsave diventano una bozza di commento per la issue [#62](https://github.com/rhiever/fmsave/issues/62), che l'utente pubblica se vuole.

## Save di riferimento

- Sorgente: la cartella **cloud** di FM27 sotto Proton, `~/.steam/debian-installation/steamapps/compatdata/4530370/pfx/drive_c/users/steamuser/AppData/Local/Sports Interactive/Football Manager 27/cloud/games/` (la cartella `Documents/.../games/` contiene copie più vecchie).
- Carriera di lavoro: solo `Roma.fm`, copiato in `local/saves/fm27/Roma.fm`.
- Per V5 e V7 serve una nuova versione di `Roma.fm` dopo una sessione di gioco, da copiare dalla stessa cartella cloud verso la fine di SP1.

## Lasciato a chi costruisce

- Nomi esatti delle colonne nostre e loro gruppi.
- Formato di output della CLI (tabella testuale semplice).
- Se usare `hatchling` o il build backend di uv nel `pyproject.toml`.
- Struttura interna dei test e delle factory.

## Criteri di successo

1. `uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma` crea uno snapshot Parquet e una riga nel catalogo; rilanciato, dice "già importato".
2. `uv run fmxray show` stampa un giocatore della Roma con tutti i gruppi di campi e la provenienza `unconfirmed`.
3. `uv run pytest` passa senza save; con il save presente passano anche i test `real_save`.
4. `ruff`, `mypy --strict` e `lint-imports` sono puliti; la CI è verde su Linux e Windows.
5. Nessun modulo fuori da `adapters/fmsave_source` importa fmsave (garantito da `lint-imports`).
6. V1–V4, V6 registrate nella wiki; V5 e V7 registrate appena c'è il secondo save.
7. Wiki aggiornata: `engineering/*` e una pagina per modulo in `modules/`.
