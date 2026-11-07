# SP3 — Interfaccia della Fase 1: piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task, inline (no subagents). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `uv run fmxray-gui` apre la finestra di FM X-Ray sul save reale: filtri dai controlli (popup a schede, campo dei ruoli, filtri rapidi), barra a testo sincronizzata, tabella, scheda del giocatore, ricerche salvate e viste di colonne; quando FM salva, la tabella si aggiorna da sola.

**Architecture:** tutta la logica che non disegna sta fuori da Qt: `FilterState` ↔ `Spec`, mappa delle schede dei filtri, viste di colonne e `BrowseSession` in `application`; `to_text` (inverso di `parse`) in `domain.search`. Il nuovo pacchetto `fmxray.ui` contiene solo widget, modello Qt della tabella, watcher e worker. Viste personalizzate e cartelle delle carriere vanno nel catalogo SQLite (migrazione 3).

**Tech Stack:** come SP2 più PySide6 6.12.0 (Qt Widgets) e pytest-qt 4.5.0.

**Spec:** [docs/superpowers/specs/2026-11-06-sp3-interfaccia-design.md](../specs/2026-11-06-sp3-interfaccia-design.md); in subordine la [spec madre](../specs/2026-11-03-fm-x-ray-design.md) §6, §8.

## Global Constraints

- Valgono i Global Constraints dei piani di SP1 e SP2: chi esegue non lancia `uv add`/`uv sync`, `git commit`, `git push`; stampa comandi completi (niente segnaposti, niente attribuzioni a Claude) e attende "fatto". API di PySide6 e Polars verificate sulla versione installata.
- Branch: `feat/sp3-interfaccia`, da `main` aggiornato; il primo commit contiene spec e piano.
- Dipendenze nuove, versioni esatte: `PySide6==6.12.0`, `pytest-qt==4.5.0` (dev).
- Interfaccia in inglese; ogni testo visibile passa da `self.tr(...)` (o `QCoreApplication.translate`).
- `fmxray.domain` e `fmxray.application` non importano PySide6; `fmxray.ui` non importa `fmxray.adapters` né `fmxray.bootstrap` (contratti import-linter).
- Linux e Windows; test Qt con `QT_QPA_PLATFORM=offscreen` impostato in `tests/conftest.py`.
- Soglie dei ruoli: natural `>= 18`, accomplished `>= 15` (come SP2).
- Nessun dato SI/SEGA nel repo; nei test solo dati di `tests/factories.py`.

## Review Focus

1. **Nuovo snapshot mentre l'utente sta filtrando** (import automatico): filtri, ordinamento e selezione restano; se il giocatore selezionato non c'è più, la scheda si svuota → test in Task 8.
2. **Barra a testo con testo a metà o sbagliato** (`age<`, `finishng>15`): nessun crash, errore accanto alla barra, controlli e tabella restano all'ultimo filtro valido → test in Task 8.
3. **Import fallito dal watcher** (save scritto a metà o rovinato): messaggio nella barra di stato, snapshot precedente ancora mostrato, nessun nuovo tentativo finché il file non cambia → test in Task 9.
4. **Primo avvio o carriera senza snapshot:** finestra vuota con "Import…" e scelta della cartella, nessuna eccezione → test in Task 8.
5. **Record incompleti** (nome, età o personalità mancanti, come nel save reale): `-` in tabella e scheda, "copy name" disattivato → test in Task 5 e Task 6.

---

### Task 1: Dipendenze, scheletro di `ui`, `App` in `application`

**Files:**
- Modify: `pyproject.toml` (dipendenze dall'utente; script `fmxray-gui`; contratti import-linter), `.github/workflows/ci.yml`, `.gitignore` (`.impeccable/`), `src/fmxray/cli/commands.py`, `src/fmxray/bootstrap.py`, `tests/conftest.py`, `tests/cli/test_commands.py`
- Create: `src/fmxray/application/app.py`, `src/fmxray/ui/__init__.py`, `src/fmxray/ui/run.py`, `tests/ui/__init__.py`, `tests/ui/test_smoke.py`

**Interfaces:**
- Produces: `fmxray.application.app.App` (stessi campi di oggi, spostata da `cli/commands.py`; `cli` la importa da lì); `fmxray.ui.run.run_gui(app: App, argv: Sequence[str]) -> int` (crea `QApplication`, mostra la finestra, `exec()`); `fmxray.bootstrap.gui_main(argv: Sequence[str] | None = None) -> int`; script `fmxray-gui = "fmxray.bootstrap:gui_main"`.

- [ ] **Step 1:** stampare per l'utente, su `feat/sp3-interfaccia`: `uv add "PySide6==6.12.0"` e `uv add --dev "pytest-qt==4.5.0"`; attendere "fatto".
- [ ] **Step 2:** verificare: `uv run python -c "import PySide6, pytestqt; print(PySide6.__version__)"` → `6.12.0`. Se pytest-qt non si importa su 3.14: fermarsi e riportare l'errore (rischio nella spec).
- [ ] **Step 3: test** `tests/ui/test_smoke.py::test_main_window_opens` — `run_gui` non si testa (blocca); il test crea la finestra principale vuota con `qtbot` (classe provvisoria `MainWindow` in `ui/main_window.py`, sostituita in Task 8) e verifica `window.windowTitle() == "FM X-Ray"`. In `tests/conftest.py`: `os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")` prima di ogni import Qt.
- [ ] **Step 4:** contratti in `pyproject.toml`: `"ui does not know adapters or bootstrap"` (forbidden `fmxray.adapters`, `fmxray.bootstrap` da `fmxray.ui`); `"domain and application do not import Qt"` (forbidden `PySide6` da `fmxray.domain`, `fmxray.application`). Aggiungere `fmxray.ui` dove serve nei contratti esistenti (cli e ui indipendenti).
- [ ] **Step 5:** CI: sul solo job `ubuntu-latest`, prima di `uv sync`, `sudo apt-get update && sudo apt-get install -y libegl1 libxkbcommon0 libgl1`; verificare che i test Qt girino in CI (Step 8 di Task 10). Se servono altre librerie, aggiungerle qui e annotarlo nel ledger.
- [ ] **Step 6:** FAIL → spostare `App`, `run_gui`, `gui_main` → PASS; `uv run pytest`, ruff, mypy, lint-imports.
- [ ] **Step 7:** Stampare: `git add pyproject.toml uv.lock .gitignore .github src tests && git commit -m "feat(ui): scheletro PySide6 e App condivisa"`

### Task 2: `to_text`, inverso di `parse`

**Files:**
- Create: `src/fmxray/domain/search/printer.py`, `tests/domain/search/test_printer.py`
- Modify: `src/fmxray/domain/search/spec.py` (`ListContains.value: Value`; `from_json` conserva il tipo con `_value_from_json` invece di `str(...)`; test di roundtrip JSON con un intero), `src/fmxray/domain/search/parser.py` (`campo:valore` su liste di interi → intero)

**Interfaces:**
- Consumes: nodi di `spec.py`, `parse`, `SEARCH_SCHEMA`.
- Produces: `to_text(spec: Spec) -> str`. `MatchAll` → `""`; testo sempre tra virgolette; `Or` dentro `And` e figli composti di `Not` tra parentesi; date ISO; booleani `true`/`false`. Valori di testo che contengono `"` → `ValueError` (la UI li toglie prima).

- [ ] **Step 1: test** `test_printer.py`: `test_examples` — `to_text(parse("age<22 pa>180 (pos:dc or pos:dm) not club:roma"))` riparsato dà lo stesso albero; `test_match_all_is_empty`; `test_quotes_rejected`; `test_list_of_ints` — `parse("second_nation_ids:7") == ListContains("second_nation_ids", 7)`; `test_roundtrip` (Hypothesis) — alberi normalizzati (nessun `And` figlio diretto di `And`, nessun `Or` di `Or`, almeno 2 figli, testo già piegato con `fold`, senza `"`), su campi di tipo intero, decimale, data, booleano, testo e lista: `parse(to_text(s)) == s`.
- [ ] **Step 2:** FAIL → implementare → PASS; tutta `tests/domain`; ruff, mypy, lint-imports.
- [ ] **Step 3:** Stampare: `git add src/fmxray/domain/search tests/domain/search && git commit -m "feat(search): to_text, inverso del parser"`

### Task 3: `FilterState` e mappa delle schede dei filtri

**Files:**
- Create: `src/fmxray/application/filters.py`, `src/fmxray/application/filter_layout.py`, `tests/application/test_filters.py`, `tests/application/test_filter_layout.py`

**Interfaces:**
- Consumes: nodi `Spec`, `fold`, `SEARCH_SCHEMA`, `PLAYER_CATALOG`, `POSITIONS`, `POSITION_THRESHOLD`, `NATURAL_THRESHOLD`.
- Produces in `filters.py`:
  - `class Mode(StrEnum)`: `ANY = "any"`, `ALL = "all"`.
  - `@dataclass(frozen=True) class Range(low: Value | None = None, high: Value | None = None)` (estremi inclusi).
  - `@dataclass(frozen=True) class FilterState`: `ranges: Mapping[str, Range]`, `positions: Mapping[str, int]` (codice → soglia), `positions_mode: Mode = Mode.ANY`, `choices: Mapping[str, frozenset[Value]]`, `choice_modes: Mapping[str, Mode]`, `flags: Mapping[str, bool]`, `texts: Mapping[str, str]`, `name_or_club: str = ""`; tutti con default vuoto. `EMPTY = FilterState()`.
  - `to_spec(state: FilterState) -> Spec`: `Range` → `GE`/`LE`; posizioni → `Comparison("pos_x", GE, soglia)` unite da `Or` (any) o `And` (all); `choices` su lista → `ListContains` per valore (any/all), su scalare (es. `nation_id`) → `Comparison(EQ)` unite da `Or`; `flags` → `EQ`; `texts` → `TextContains(f, fold(t))`; `name_or_club` → `Or(TextContains("name", …), TextContains("club_name", …))`. Congiunti in ordine fisso (ordine di `FILTER_TABS`), uniti in `And`; nessuno → `MatchAll()`.
  - `from_spec(spec: Spec) -> FilterState | None`: inverso; `None` se l'albero non è rappresentabile (es. `Or` tra campi diversi che non sia la forma di `name_or_club`). Su campi interi normalizza `LT n` → `high = n - 1`, `GT n` → `low = n + 1`, `EQ n` → `low = high = n`; `LT`/`GT` su decimali e date → `None`.
  - `active_count(state: FilterState) -> int`.
- Produces in `filter_layout.py`: `@dataclass(frozen=True) class FilterBlock(title: str, fields: tuple[str, ...])`; `@dataclass(frozen=True) class FilterTab(title: str, blocks: tuple[FilterBlock, ...])`; `FILTER_TABS: tuple[FilterTab, ...]` con le schede della spec (General, Positions, Attributes, Hidden & personality, Contract & value, Traits); `QUICK_FIELDS = ("age", "ca", "pa")`; `slider_bounds(field: str) -> tuple[int, int] | None`: `DISPLAY_1_20` → `(1, 20)`, `RAW_1_100` → `(1, 100)`, `ca`/`pa` → `(1, 200)`, altrimenti `None` (spin box con min/max dello snapshot).

- [ ] **Step 1: test** `test_filter_layout.py::test_every_field_is_filterable` — l'unione dei campi di `FILTER_TABS` (con `pos_*` coperti dalla scheda Positions) contiene ogni nome di `SEARCH_SCHEMA`; `test_slider_bounds`.
- [ ] **Step 2: test** `test_filters.py`: `test_empty_state_matches_all`; `test_quick_filters` — età 15–21, PA ≥ 180, DC naturale e DM accomplished in any → `parse("age>=15 age<=21 pa>=180 (pos_dc>=18 or pos_dm>=15)")`; `test_positions_all_mode`; `test_traits_any_and_all`; `test_name_or_club`; `test_lt_normalised` — `from_spec(parse("age<22")).ranges["age"] == Range(high=21)`; `test_not_representable` — `from_spec(parse("age<22 or ca>150")) is None`, `from_spec(parse("not club:roma")) is None`; `test_roundtrip` (Hypothesis) — `from_spec(to_spec(s)) == s` per stati senza voci vuote; `test_state_and_text_select_same_players` — su `prepare_frame(make_player_frame(30), …)` `to_spec(s)` e `parse(to_text(to_spec(s)))` filtrano le stesse righe.
- [ ] **Step 3:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 4:** Stampare: `git add src/fmxray/application/filters.py src/fmxray/application/filter_layout.py tests/application && git commit -m "feat(application): stato dei filtri e mappa delle schede"`

### Task 4: Viste di colonne e cartelle delle carriere (SQLite v3)

**Files:**
- Create: `src/fmxray/application/column_views.py`, `src/fmxray/application/save_folders.py`, `src/fmxray/adapters/sqlite_catalog/user_state.py`, `tests/application/test_column_views.py`, `tests/application/test_save_folders.py`, `tests/adapters/test_user_state.py`
- Modify: `ports.py`, `schema.py` (migrazione 3), `sqlite_catalog/__init__.py`, `application/app.py`, `bootstrap.py`, `tests/application/fakes.py`, `tests/adapters/test_sqlite_catalog.py` (`test_user_version_is_3`)

**Interfaces:**
- Produces:
  - `column_views.py`: `@dataclass(frozen=True) class ColumnView(name: str, columns: tuple[str, ...])`; `BUILTIN_VIEWS: tuple[ColumnView, ...]` = General (`name, age, club_name, ca, pa, natural_positions, transfer_value, contract_end`), Technical, Mental, Physical, Goalkeeping (attributi del gruppo), Hidden (hidden + personalità), Contract, **Hidden by FM** (`name, age, club_name, ca, pa` + hidden + personalità); ogni vista inizia con `name`.
  - `ports.py`: `ColumnViewStore(Protocol)`: `save(view: ColumnView) -> None` (sovrascrive), `list() -> list[ColumnView]`, `delete(name: str) -> bool`; `CareerSourceStore(Protocol)`: `set(career_id: int, path: Path) -> None`, `get(career_id: int) -> Path | None`.
  - Migrazione 3: `column_views(name TEXT PRIMARY KEY, columns_json TEXT NOT NULL)`, `career_sources(career_id INTEGER PRIMARY KEY REFERENCES careers(id), path TEXT NOT NULL)`.
  - `SqliteColumnViewStore(db_path)`, `SqliteCareerSourceStore(db_path)` in `user_state.py`, stessa `migrate`.
  - `save_folders.py`: `default_save_folders(env: Mapping[str, str], home: Path) -> list[Path]` → solo le cartelle esistenti tra: Windows `%LOCALAPPDATA%\Sports Interactive\Football Manager 27\games` e `…\cloud\games`; Linux con Proton `steamapps/compatdata/4530370/pfx/drive_c/users/steamuser/AppData/Local/Sports Interactive/Football Manager 27/{games,cloud/games}` sotto `~/.steam/debian-installation`, `~/.steam/steam`, `~/.local/share/Steam`. *(La cartella Windows è da verificare: annotarlo in `wiki/agent/context.md`.)*
  - `App` guadagna `column_views: ColumnViewStore`, `career_sources: CareerSourceStore`, `import_factory: Callable[[], ImportSave]` (costruisce adattatori nuovi: le connessioni SQLite non si condividono tra thread).
- [ ] **Step 1: test** `test_column_views.py::test_builtin_views_use_known_fields` (ogni colonna in `SEARCH_SCHEMA`), `test_hidden_by_fm_view`; `test_user_state.py`: `test_view_save_list_delete`, `test_view_overwrite`, `test_career_source_set_get`, `test_v2_database_is_migrated`; `test_save_folders.py::test_finds_existing_proton_and_windows_folders` (cartelle create in `tmp_path`, `env={"LOCALAPPDATA": …}`), `test_missing_folders_skipped`.
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 3:** Stampare: `git add src tests && git commit -m "feat: viste di colonne e cartelle delle carriere"`

### Task 5: Tema e modello della tabella

**Files:**
- Create: `src/fmxray/ui/theme.py`, `src/fmxray/ui/table_model.py`, `tests/ui/test_theme.py`, `tests/ui/test_table_model.py`

**Interfaces:**
- Produces:
  - `theme.py`: `TOKENS: Mapping[str, str]` (colori di fondo, testo, bordo, selezione, `unconfirmed`, `estimate`, `new`, fasce `band_1`…`band_4`, font, spaziature); `stylesheet(tokens: Mapping[str, str] = TOKENS) -> str` (QSS); `attribute_band(value: int | None) -> str | None` → `band_1` (1–5), `band_2` (6–10), `band_3` (11–15), `band_4` (16–20), `None` se mancante. Tutti i colori di `ui` vengono da `TOKENS`.
  - `table_model.py`: `class PlayerTableModel(QAbstractTableModel)`: `set_result(frame: pl.DataFrame, columns: Sequence[str], provenance: Mapping[str, Provenance], new_uids: frozenset[int] = frozenset()) -> None` (le colonne visibili diventano liste Python una volta sola); `uid_at(row: int) -> int`; `row_of(uid: int) -> int | None`; segnale `sort_requested(str, bool)` emesso da `sort()` (l'ordinamento lo fa Polars in `BrowseSession`). `DisplayRole`: `-` per i mancanti, liste unite da `, `; `ForegroundRole` dalle fasce sugli attributi 1–20; intestazione con `DecorationRole`/`ToolTipRole` se la colonna è `unconfirmed`; colonna 0 con il segno dei nuovi.
- [ ] **Step 1: test** `test_theme.py`: `test_attribute_bands` (1, 5, 6, 15, 16, 20, `None`); `test_stylesheet_uses_tokens` (cambiando un token cambia il QSS).
- [ ] **Step 2: test** `test_table_model.py` (pytest-qt `qtmodeltester` compreso): `test_model_passes_qt_checks`; `test_missing_values_show_dash` (frame con `name=None`); `test_unconfirmed_header_tooltip` e `test_no_mark_when_verified`; `test_new_mark`; `test_sort_emits_request`; `test_set_result_fast` — 126.427 righe sintetiche, vista General: `set_result` sotto `0.5` s (miglior tempo di 3).
- [ ] **Step 3:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 4:** Stampare: `git add src/fmxray/ui tests/ui && git commit -m "feat(ui): tema a token e modello della tabella"`

### Task 6: Campo dei ruoli e scheda del giocatore

**Files:**
- Create: `src/fmxray/ui/pitch.py`, `src/fmxray/ui/player_card.py`, `tests/ui/test_pitch.py`, `tests/ui/test_player_card.py`

**Interfaces:**
- Produces:
  - `pitch.py`: `class PitchWidget(QWidget)` con le 15 posizioni (`POSITIONS`) disposte come nel wireframe; modalità `selectable: bool`; `set_ratings(ratings: Mapping[str, int | None]) -> None` (sola lettura, per la scheda); `set_selection(thresholds: Mapping[str, int]) -> None`; segnale `selection_changed(dict)` (codice → soglia): click su una posizione la aggiunge con `NATURAL_THRESHOLD`, la scelta del livello (natural / accomplished / soglia 1–20) da un menu sulla posizione, secondo click la toglie.
  - `player_card.py`: `class PlayerCard(QWidget)`: `show_player(meta: SnapshotMeta, values: Mapping[str, object]) -> None`, `clear() -> None`; testata (nome, pulsante "Copy name" → `QGuiApplication.clipboard()`, età, club, ruoli, CA/PA), schede Attributes (Technical/Mental/Physical o Goalkeeping), Hidden, Contract, Positions (`PitchWidget` in sola lettura); segno `unconfirmed` sui gruppi.
- [ ] **Step 1: test** `test_pitch.py`: `test_click_adds_natural_position`, `test_second_click_removes`, `test_level_menu_sets_accomplished`, `test_read_only_ignores_clicks`. `test_player_card.py`: `test_copy_name_to_clipboard`; `test_incomplete_record` (nome `None` → `-`, pulsante disattivato); `test_attribute_tabs_show_all_attributes`; `test_clear_empties_card`.
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 3:** Stampare: `git add src/fmxray/ui tests/ui && git commit -m "feat(ui): campo dei ruoli e scheda del giocatore"`

### Task 7: Popup dei filtri e filtri rapidi

**Files:**
- Create: `src/fmxray/ui/filters_dialog.py`, `src/fmxray/ui/quick_filters.py`, `src/fmxray/ui/range_slider.py`, `tests/ui/test_filters_dialog.py`, `tests/ui/test_quick_filters.py`

**Interfaces:**
- Consumes: `FilterState`, `Range`, `Mode`, `FILTER_TABS`, `QUICK_FIELDS`, `slider_bounds`, `PitchWidget`.
- Produces:
  - `range_slider.py`: `class RangeControl(QWidget)` (due maniglie se `slider_bounds` dà limiti, altrimenti due spin box o date), segnale `range_changed(str, object)` con `Range`; gli estremi lasciati ai limiti diventano `None`.
  - `filters_dialog.py`: `class FiltersDialog(QDialog)` non modale costruito da `FILTER_TABS` (una scheda Qt per `FilterTab`, un gruppo per `FilterBlock`, il controllo giusto per tipo: `RangeControl`, caselle "any/all" per le liste, tre stati per i booleani, testo per `TEXT_FIELDS`, `PitchWidget` selezionabile per le posizioni); `set_state(state: FilterState) -> None`; `set_locked(locked: bool) -> None` (mostra "Advanced filter from the text bar"); segnale `state_changed(object)`; pulsanti "Reset" per scheda e globale; in fondo `N active filters · M players` (`set_counts(active: int, players: int)`).
  - `quick_filters.py`: `class QuickFilters(QWidget)` per `QUICK_FIELDS`, ruoli, `name_or_club`; stessi `set_state`, `set_locked`, `state_changed`; pulsante "All filters… (N active)" con segnale `open_all_requested()`.
  - Le opzioni delle liste (tratti, nazioni) vengono dai valori distinti dello snapshot: `set_options(field: str, values: Sequence[Value]) -> None`.
- [ ] **Step 1: test** `test_filters_dialog.py`: `test_one_tab_per_filter_tab`; `test_every_field_has_a_control` (scorre `FILTER_TABS`); `test_slider_emits_state` (determination 15–20 → `state.ranges["determination"] == Range(15, None)`); `test_set_state_updates_controls`; `test_locked_disables_controls`; `test_reset_tab`. `test_quick_filters.py`: `test_age_and_pa`, `test_name_or_club`, `test_shared_state_with_dialog` (stato impostato dal popup appare nei filtri rapidi).
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 3:** Stampare: `git add src/fmxray/ui tests/ui && git commit -m "feat(ui): popup dei filtri e filtri rapidi"`

### Task 8: `BrowseSession` e finestra principale

**Files:**
- Create: `src/fmxray/application/session.py`, `tests/application/test_session.py`, `tests/ui/test_main_window.py`
- Modify: `src/fmxray/ui/main_window.py`, `src/fmxray/ui/run.py`

**Interfaces:**
- Consumes: `App`, `SearchPlayers`, `RunSavedSearch`, `SaveSearch`, `export_csv`, `to_text`, `parse`, `to_spec`, `from_spec`, `BUILTIN_VIEWS`, widget dei Task 5–7.
- Produces:
  - `session.py`: `class BrowseSession`: `__init__(self, app: App)`; attributi `career: str | None`, `snapshot_id: str | None`, `filters: FilterState`, `advanced: Spec | None`, `sort: tuple[SortKey, ...] = DEFAULT_SORT`, `view: ColumnView`, `active_saved: str | None`; `spec` (proprietà: `advanced` se presente, altrimenti `to_spec(filters)`); `text` (= `to_text(spec)`); `set_filters(state)` (azzera `advanced`); `set_text(text: str) -> None` (`parse`; se `from_spec` dà uno stato lo usa, altrimenti `advanced`; errori `SearchError` propagati senza toccare lo stato); `refresh() -> SearchResult` (`limit=None`); `new_uids() -> frozenset[int]` (vuoto senza ricerca salvata attiva); `saved_new_counts() -> dict[str, int]`; `open_saved(name)` (carica lo spec salvato con `set_text` del suo albero).
  - `MainWindow(QMainWindow)`: `__init__(self, app: App, session: BrowseSession)`; layout A della spec; un `QTimer` single-shot di `FILTER_DEBOUNCE_MS = 150` tra un cambio di filtro e `refresh()`; barra a testo con errore mostrato accanto (stile `unconfirmed` dei token) senza cambiare la tabella; selezione → `ShowPlayer.details` → `PlayerCard`; "Save search" (dialogo col nome, `SaveSearch.execute(name, session.text)`), "Export CSV" (`QFileDialog`, tutte le righe filtrate, colonne della vista attiva), viste (pronte + salvate, "Save view…" dalle colonne correnti), stato vuoto con "Import…" se non ci sono carriere o snapshot; `reload_snapshot() -> None` (rilegge l'ultimo snapshot mantenendo filtri, ordinamento e selezione).
- [ ] **Step 1: test** `test_session.py` (store in memoria): `test_controls_and_text_stay_in_sync`; `test_advanced_text_locks_controls` (`set_text("age<22 or ca>150")` → `advanced` non `None`); `test_bad_text_keeps_previous_state` (`age<`, `finishng>15` → eccezione, `spec` invariato); `test_new_uids_for_saved_search`; `test_saved_new_counts`.
- [ ] **Step 2: test** `test_main_window.py` (app costruita con `build_app` su `tmp_path` e `FakeSaveSource`, come `tests/cli`): `test_empty_state_offers_import` (nessuna carriera); `test_quick_filter_updates_table` (`qtbot.waitUntil` sul conteggio); `test_age_pa_from_controls_match_cli` — età ≤ 21 e PA ≥ 181 dai controlli = stessi `uid` di `fmxray search "age<22 pa>180"`; `test_text_bar_error_shown_table_unchanged`; `test_selection_shows_card`; `test_reload_keeps_filters_sort_selection`; `test_reload_clears_card_when_player_gone`; `test_export_csv_all_filtered_rows` (dialogo sostituito con `monkeypatch`).
- [ ] **Step 3:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 4:** Stampare: `git add src tests && git commit -m "feat(ui): finestra principale e sessione di ricerca"`

### Task 9: Watcher della cartella e import in background

**Files:**
- Create: `src/fmxray/ui/watcher.py`, `src/fmxray/ui/import_worker.py`, `tests/ui/test_watcher.py`, `tests/ui/test_import_worker.py`
- Modify: `src/fmxray/ui/main_window.py`, `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: `App.import_factory`, `App.career_sources`, `default_save_folders`.
- Produces:
  - `watcher.py`: `class SaveFolderWatcher(QObject)`: `watch(path: Path) -> None` (cartella o file), `stop() -> None`; `QFileSystemWatcher` su cartella e file `.fm`; un file cambiato si considera pronto quando la dimensione resta uguale per `STABLE_FOR_MS = 3000`, controllata ogni `POLL_MS = 500`; segnale `save_ready(Path)` una volta per versione del file (stessa dimensione e `mtime` → nessun nuovo segnale).
  - `import_worker.py`: `class ImportRunner(QObject)`: `start(path: Path, career: str) -> None` (in `QThreadPool`, con `App.import_factory()` creato **nel thread** del lavoro); segnali `imported(object)` (`ImportResult`), `failed(str)`; un import alla volta, uno successivo in attesa sostituisce quello in coda.
  - `MainWindow`: "Watch folder…" e associazione salvata con `career_sources.set`; al primo avvio propone `default_save_folders(os.environ, Path.home())`; `imported` con stato `IMPORTED` → `reload_snapshot()`; `failed` → messaggio nella barra di stato.
- [ ] **Step 1: test** `test_watcher.py` (file in `tmp_path`, `qtbot.waitSignal`): `test_emits_after_size_is_stable`; `test_no_signal_while_growing` (file che cresce ogni 200 ms per 2 s); `test_same_version_not_emitted_twice`. `test_import_worker.py`: `test_import_runs_off_main_thread` (il `FakeSaveSource` registra `threading.get_ident()` diverso da quello del test); `test_failure_signal` (`UnreadableSaveError`). `test_main_window.py`: `test_new_save_refreshes_table` (watcher simulato che emette `save_ready`); `test_failed_import_keeps_previous_snapshot`.
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.
- [ ] **Step 3:** Stampare: `git add src tests && git commit -m "feat(ui): aggiornamento automatico dalla cartella dei save"`

### Task 10: Verifica sul save reale, wiki, PR

**Files:**
- Modify: `tests/integration/test_real_save.py`; wiki: crea `wiki/modules/ui.md`; aggiorna `wiki/modules/{README,application,sqlite-catalog,search}.md`, `wiki/engineering/{architecture,testing,development,change-map}.md`, `wiki/agent/{handoff,activity,context}.md`, `wiki/project/{status,work-tracker,decisions}.md`, `wiki/index.md`, `wiki/log.md`

- [ ] **Step 1: test** `test_real_save.py::test_gui_loads_real_save` (marker `real_save`): import in una cartella dati temporanea, `MainWindow` con `qtbot`, conteggio righe = giocatori dello snapshot; filtro età ≤ 21 e PA ≥ 181 dai controlli = `uid` del filtro Polars a mano.
- [ ] **Step 2:** `uv run pytest` (con il save) → verde; ruff, mypy, lint-imports.
- [ ] **Step 3:** chi esegue avvia `uv run fmxray-gui`, prova filtri, popup, ruoli, scheda, ricerche salvate, viste ed export, e riporta il risultato; poi l'utente copia un save nella cartella sorvegliata (o salva da FM) e conferma l'aggiornamento automatico.
- [ ] **Step 4:** wiki (pagina `ui` con struttura, flussi, thread; decisioni nuove: SP3b, `App` in `application`, import nel thread con adattatori propri); revisione finale inline con i Review Focus; `superpowers:verification-before-completion`.
- [ ] **Step 5:** Stampare: `git add src tests && git commit -m "test: GUI sul save reale"`, `git add wiki && git commit -m "docs: wiki dell'interfaccia"`, `git push -u origin feat/sp3-interfaccia`; poi PR con `gh pr create` (descrizione in `local/pr-sp3.md`, senza attribuzioni); CI verde su Linux e Windows (controlla anche lo Step 5 di Task 1).
