---
title: Modulo domain.search (motore di ricerca)
updated: 2026-11-06
sources:
  - src/fmxray/domain/search/
  - src/fmxray/domain/text.py
  - src/fmxray/application/search.py
  - src/fmxray/application/saved_search.py
  - src/fmxray/application/export.py
  - docs/superpowers/specs/2026-11-04-sp2-ricerca-design.md
source_commit: unknown
confidence: high
---

# Modulo domain.search (motore di ricerca)

## Purpose
Filtri combinabili su qualunque campo del giocatore (SP2). Un albero di filtri del dominio (Specification/Composite) è l'unica rappresentazione: la barra a testo lo produce, le ricerche salvate lo conservano in JSON, il compilatore lo trasforma in un `pl.Expr`. Importa solo stdlib, Polars e `fmxray.domain`.

## Public interface
| File | Nome | Ruolo |
| --- | --- | --- |
| `spec.py` | `MatchAll`, `Comparison`, `IsNone`, `TextContains`, `ListContains`, `And`, `Or`, `Not`; `Op` | nodi immutabili |
| `spec.py` | `to_json`, `from_json`, `SPEC_VERSION = 1`, `fields_in` | JSON versionato; campi usati |
| `compile.py` | `to_expr(spec, schema)` | albero → `pl.Expr` |
| `parser.py` | `parse(text)`, `parse_sort(text)`, `SortKey`, `DEFAULT_SORT`, `SEARCH_SCHEMA` | barra a testo e ordinamento |
| `aliases.py` | `ALIASES`, `resolve_field` | nomi corti (`acc`, `det`, `value`, `club`, …) |
| `derived.py` | `prepare_frame(frame, game_date)`, `TEXT_FIELDS`, `DERIVED_FIELDS` | `contract_left`, `free_agent`, colonne `__folded` |
| `printer.py` | `to_text(spec)` | albero → testo della barra, inverso di `parse` |
| `errors.py` | `SearchError` → `UnknownFieldError`, `QueryParseError`, `SpecFormatError` | errori per l'utente (con posizione e suggerimenti) |

## Sintassi della barra
```
query    := or_expr? EOF
or_expr  := and_expr ("or" and_expr)*
and_expr := unary ("and"? unary)*        # spazio = and
unary    := "not" unary | "(" or_expr ")" | term
term     := NAME OP VALUE | NAME ":" VALUE  # OP: < <= > >= = !=
```
| Forma | Significato |
| --- | --- |
| `pos:dc` / `natural:dc` | valutazione nella posizione `>= 15` / `>= 18` |
| `club:roma`, `name:"Ünal Çelik"` | testo contenuto, senza maiuscole e accenti |
| `trait:dictates_tempo`, `natural_positions:amc` | la lista contiene il valore |
| `transfer_value:none` | il valore manca |
| `contract_end<2027-06-30`, `free_agent=true` | date ISO, booleani |
| testo vuoto | tutti i giocatori |

## Invariants
- Un confronto su un valore mancante è falso (`fill_null(False)` sulle foglie): `transfer_value<1000000` esclude chi non ha valore, `not club:roma` include gli svincolati.
- Nome sconosciuto → `UnknownFieldError` con suggerimenti `difflib`, mai "zero risultati".
- Il parser controlla i tipi (`age<abc`, `club_name>3` → `QueryParseError`), così Polars non fallisce durante il filtro.
- Testo e JSON danno lo stesso risultato (test Hypothesis `test_text_and_json_agree`).
- Soldi in unità interna del save: `SearchResult.money_fields` segnala i campi `money_internal` usati.

## Casi d'uso collegati (application)
- `SearchPlayers.execute(career, spec, sort, limit, snapshot_id)` → `SearchResult(meta, frame, total, money_fields)`; valori mancanti in fondo all'ordinamento; cache di un solo frame preparato.
- `SaveSearch`, `RunSavedSearch` → `SavedSearchRun(search, result, new_uids)`: nuovi = `uid` che soddisfano la ricerca nell'ultimo snapshot e non nel precedente (V5: se `uid` non fosse stabile, si cambia solo in `RunSavedSearch`).
- `export_csv(frame, path, columns)`: UTF-8 con BOM, liste unite con `|`, colonne `__folded` escluse; i testi che iniziano con `=`, `+`, `-`, `@`, tab o a capo prendono un `'` davanti, così Excel e LibreOffice non li eseguono come formule.

## Verification
`uv run pytest tests/domain/search tests/application/test_search.py tests/application/test_saved_search.py tests/application/test_export.py`; prestazioni: `tests/application/test_search_performance.py` (< 200 ms su 126.427 righe; sul save reale 2–8 ms).
