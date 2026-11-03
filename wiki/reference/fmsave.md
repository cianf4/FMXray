---
title: fmsave (libreria di lettura dei save)
updated: 2026-10-31
sources:
  - https://github.com/rhiever/fmsave
  - https://rhiever.github.io/fmsave/
  - https://rhiever.github.io/fmsave/reference/records.html
  - https://rhiever.github.io/fmsave/guides/trust.html
  - https://rhiever.github.io/fmsave/guides/what-a-save-holds.html
  - https://rhiever.github.io/fmsave/changelog.html
  - https://rhiever.github.io/fmsave/app/
source_commit: unknown
confidence: medium
---

# fmsave

Controllato il **2026-10-31** sulla versione **0.9.0** (uscita il 2026-10-30).
Decade in fretta: rileggere il changelog prima di ogni aggiornamento.

## In breve

| Voce | Valore |
| --- | --- |
| Cosa fa | legge i save `.fm` di FM26 e FM27 (solo build `27.0.0+2486695`) in record Python, DataFrame, CSV, JSON |
| Garanzie | sola lettura; nessuna connessione di rete; non legge la memoria del gioco |
| Licenza | MIT; progetto non affiliato a SI/SEGA |
| Python | 3.12+ |
| Installazione | `pip install fmsave`, `pip install "fmsave[pandas]"`; nel progetto: `uv run fmsave info "local/saves/fm27/Roma.fm"` |
| CLI | `info`, `export` (serve uno scope: `--club`, `--managed-club`, `--competition`, `--nation`, `--all`), `validate` |
| Ritmo di rilascio | 26 release dal 2026-09-18 (0.4.0) al 2026-10-30 (0.9.0), circa 4 a settimana |
| Contributi | il maintainer non fa merge di PR esterne: si apre una issue, e chi la apre viene citato quando la modifica esce. Mai allegare o linkare save |

## Uso base

```python
import fmsave

with fmsave.open("career.fm") as career_save:
    my_club = career_save.managed_clubs()[0]  # vuoto se sei senza panchina
    squad = career_save.players().where(club_uid=my_club.club_uid)
    squad.write_csv("squad.csv")
```

Le `Table` sono immutabili e restano valide dopo la chiusura del save. Metodi:
`where`, `filter`, `sorted_by`, `find`, `by_uid`, `by_id`, `coverage`, export
verso dict, colonne, pandas, polars, CSV, JSON, JSON Lines.

## Reader (30)

| Area | Reader |
| --- | --- |
| Persone | `players()`, `contracts()`, `suspensions()`, `staff()`, `staff_lists()` |
| Club | `clubs()`, `managed_clubs()`, `finances()`, `sponsorships()`, `facilities()`, `stadiums()`, `affiliates()`, `job_vacancies()` |
| Competizioni | `stages()`, `competitions()`, `fixtures()`, `league_tables()`, `competition_rules()`, `transfer_windows()`, `player_match_stats()`, `player_season_stats()`, `player_season_history()` |
| Nazioni | `nations()` |
| Infortuni | `injury_types()`, `injuries()` |
| Solo il club gestito | `training()`, `mentoring()`, `tactics()`, `set_pieces()`, `selections()` |

## Record `Player` (campi principali)

| Gruppo | Campi |
| --- | --- |
| Identità | `uid`, `unique_id`, nomi vari, `birth_date`, `age` |
| Nazionalità | `nation_id`, `second_nation_ids`, `home_grown_*` |
| Club | `club_uid`, `club_name`, `club_reputation`, `club_join_date`, … |
| Abilità | `ability.current`, `ability.potential`, `ability.potential_range_code` |
| Reputazione | `reputation.bucket/home/current/world` (per ordinare usare `current`, mai `bucket`) |
| Attributi | `attributes` (scala 1–20) e `raw_attributes` (scala 1–100), 52 campi ciascuno |
| Piedi | `left_foot`, `right_foot` (1–20), `raw_left_foot`, `raw_right_foot` (1–100) |
| Posizioni | `positions` (15 valori: gk, sw, dl, dc, dr, dm, ml, mc, mr, aml, amc, amr, stc, wbl, wbr); `natural_positions` (≥ 18); `accomplished_positions` (15–17, etichetta di fmsave). Nessun campo "ruolo" |
| Personalità | `personality`: adaptability, ambition, loyalty, pressure, professionalism, sportsmanship, temperament, controversy |
| Tratti | `traits` (bit non riconosciuti → `Trait.UNKNOWN`), `trait_bits` |
| Valore e condizione | `transfer_value` (valuta base del save, valido solo se `transfer_value_state` è OK); `raw_condition`, `raw_match_sharpness` (0–10000, /100 per la %) |
| Altro | `height_cm`, `contract`, `suspensions`, prestiti (`on_loan`, `loan_*`) |

**Hidden tra i 52 attributi:** `dirtiness`, `consistency`, `important_matches`,
`injury_proneness`, `versatility`. Gli altri 8 hidden sono i campi di
`personality`. Totale: i 13 elencati dall'utente. Da verificare su un save reale
(V1 in [requisiti](../project/requirements.md)).

## Identificatori

| ID | Significato |
| --- | --- |
| `uid` | chiave di join dentro un save; **cambia** tra carriere diverse dallo stesso database |
| `unique_id` | Unique ID del database del gioco, stabile tra carriere dallo stesso database; può essere `None` |
| `database_id` | su competizioni e nazioni, per collegare una mappa esterna id → nome |

Per i club, `uid` 0 è valido: nei filtri usare `is not None`.

## Contratti

`Contract`: `wage` (settimanale, valuta base), `start`, `end`, `squad_status`,
`kind`, `clauses`, `chain`, dati del prestito. **Le clausole rescissorie non hanno
un campo dedicato:** sono `Clause` dentro `clauses` (`kind`, `parameter`,
`value`), con `value` nell'unità interna del save. I valori di `ClauseKind` sono
nella pagina Enums (non ancora letta).

## Affidabilità

- Ogni campo è `verified` o `unconfirmed`:
  `fmsave.field_status(fmsave.Player, "attributes.finishing")` → `"verified"`,
  `fmsave.field_status(fmsave.Player, "contract.wage")` → `"unconfirmed"`.
  Un campo senza stato registrato solleva `KeyError`.
- `table.coverage["<colonna>"]` dà la quota di valori non `None`; un `None` può
  voler dire dato assente, join non risolto o decodifica fallita.
- I controlli avvisano per default; `strict=True` li fa sollevare. I guasti
  strutturali sollevano sempre.
- **FM27:** ogni save emette `UnknownBuildWarning`; un controllo fallito ferma
  sempre il reader; limite di decompressione 256 MiB per frame e 512 MiB totali;
  tutti i campi FM27 sono non confermati.

## Cosa non legge

- Nomi di competizioni, nazioni, città (stanno nel database installato del
  gioco); si può passare una mappa `database_id → nome` con
  `fmsave.read_competition_names("file.csv")`.
- Asking price, debito dei club, disponibilità del giorno, formazioni complete,
  quasi tutti gli attributi dello staff (solo `adaptability`).
- I soldi non sono convertiti nella valuta mostrata.
- Se il gioco è aperto, bisogna copiare il save e leggere la copia.

## Web app di fmsave

[rhiever.github.io/fmsave/app](https://rhiever.github.io/fmsave/app/): legge il
save nel browser (nessun upload). Mostra squadra, tutti i giocatori o la
shortlist; attributi, CA/PA, hidden, personalità, contratti, statistiche della
stagione; ruota a percentili per ruolo; filtri per nome, ruolo, età,
competizione e soglie percentuali; export CSV. È il termine di paragone diretto
della nostra Fase 1.

## Domande aperte

- Tempi di lettura e memoria su un save grande (non documentati).
- Significato di `potential_range_code` (PA espressa come intervallo?).
- Come si presentano i newgen: `unique_id` nuovo o `None`? (la 0.5.9 dice "newly generated players read").

## Verifiche su un save reale (2026-11-03)

Save FM27 dell'utente (`local/saves/fm27/Roma.fm`, 120 MB, data di gioco 2026-09-12), fmsave **0.9.3**,
build `27.0.0+2493426` (**non registrata**: fmsave usa i layout della `2486695` dove lo schema coincide).

| Voce | Risultato |
| --- | --- |
| `fmsave validate --json` (tutti i 30 reader) | ~63 s reali su Linux (V3, prima misura) |
| `players()` | ok, **126.427** giocatori, 218 colonne piatte |
| 13 hidden (5 attributi + 8 personalità) | presenti, copertura 100% (V1 strutturale; da verificare nel gioco) |
| CA / PA | copertura 100%; `potential_range_code` sempre vuoto |
| `unique_id` | 99,99% valorizzato |
| `transfer_value` | 73% (resto: stato non OK) |
| `contract_clauses` | 99,9%; 9532 code di contratto non interpretate |
| Reader non ok | `finances`, `sponsorships` (failed), `training`, `mentoring` (error): non ci servono |
| `field_status` | tutti i 747 campi **unconfirmed** su FM27 |
| `players()` da solo | ~21 s + ~5 s per `to_columns()` (V3) |
| Clausole rescissorie (V2) | presenti come `contract_clauses` (tuple di dict `kind`, `kind_code`, `parameter`, `value`): `minimum_fee_release` 4796, `minimum_fee_release_domestic` 1759, `minimum_fee_release_foreign` 228, `relegation_release` 170, `minimum_fee_release_domestic_higher_division` 53, `non_promotion_release` 8; 42 tipi in totale, molti `unknown` |
| `SaveInfo` | `game`, `build`, `build_number`, `known_build`, `db_version`, `game_date` (V6: 2026-09-12), `save_name`, `file_name` |
| `field_status(Player, "attributes.finishing")` | path con punti; descrive FM26; su FM27 vale sempre `unconfirmed` |
| `transfer_value_state` | `ok`, `zero`, `unset`, `placeholder` |
| `fmxray import` completo (V3) | ~33 s; snapshot Parquet 16 MB; re-import dello stesso file: solo hash |
| Record incompleti | 2 giocatori senza nome, età e personalità (blocchi persona non decodificati) |
