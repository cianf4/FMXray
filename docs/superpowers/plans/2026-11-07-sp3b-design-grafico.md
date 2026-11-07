# SP3b — Design grafico e riordino: piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task, inline (no subagents). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** la finestra di SP3 riordinata (viste a linguette, ricerche salvate in una barra laterale richiudibile, barra a testo a richiesta, chip dei filtri attivi, scheda compatta) e vestita con lo stile scelto dall'utente tra tre proposte, con densità media/compatta e animazioni leggere.

**Architecture:** nessuna logica nuova fuori dalla UI tranne la descrizione dei filtri attivi come chip (`application.filters`, Python puro). I widget nuovi stanno in `ui/` accanto a quelli di SP3; tutti i colori, i font e le misure restano in `ui/theme.py`, che riceve i token della proposta scelta. Le preferenze dell'interfaccia (densità, barra laterale aperta) passano da un piccolo wrapper di `QSettings`.

**Tech Stack:** come SP3 (Python 3.14, PySide6 6.12.0, pytest-qt 4.5.0). Mockup nel visual companion di superpowers; skill `impeccable` e `taste-skill` per due delle tre proposte.

**Spec:** [docs/superpowers/specs/2026-11-07-sp3b-design-grafico-design.md](../specs/2026-11-07-sp3b-design-grafico-design.md); in subordine la [spec di SP3](../specs/2026-11-06-sp3-interfaccia-design.md).

## Global Constraints

- Valgono i Global Constraints dei piani SP1–SP3: niente `uv add`/`uv sync`, `git commit`, `git push` da parte di chi esegue; comandi completi senza segnaposti e senza attribuzioni; si attende "fatto".
- Branch: `feat/sp3b-design`, da `main` aggiornato; il primo commit contiene spec e piano.
- **Nessuna dipendenza nuova** e nessun font nel repo: font di sistema con fallback.
- I mockup usano solo ciò che Qt Style Sheets riproduce: colori, bordi, raggi, padding, font, gradienti lineari semplici; niente ombre sfumate, filtri, transizioni CSS.
- Tutti i colori, font e misure dei widget vengono da `ui/theme.py`.
- Animazioni con `QPropertyAnimation`, durata `ANIMATION_MS = 150`; i test non dipendono dalla loro durata (`animate=False` dove serve).
- Densità di default **media**; **compatta** a un click; scelta ricordata (`QSettings`).
- Interfaccia in inglese con `tr()`; nei mockup nomi e numeri inventati.

## Review Focus

1. **Filtro attivo tolto da una chip mentre il popup è aperto:** il popup e i filtri rapidi si aggiornano subito, nessun filtro "fantasma" → test in Task 3 e Task 6.
2. **Barra a testo chiusa con un filtro avanzato attivo** (es. `or` tra campi): il filtro resta visibile come chip "Advanced filter" rimovibile e i controlli restano bloccati → test in Task 3 e Task 6.
3. **Vista dell'utente con colonne che non esistono più** (salvata prima di un cambio del catalogo): la linguetta mostra solo le colonne note, nessun crash → test in Task 4.
4. **Barra laterale chiusa con ricerche nuove:** il badge con il totale dei nuovi resta visibile da chiusa → test in Task 5.
5. **Preferenze rovinate o mancanti** (`QSettings` vuoto o con valori strani): si parte con densità media e barra chiusa → test in Task 2.

---

### Task 1: Tre mockup e scelta dell'utente

**Files:**
- Create (git-ignorati, in `.superpowers/brainstorm/`): `sp3b-a-claude.html`, `sp3b-b-impeccable.html`, `sp3b-c-taste.html`, `sp3b-compare.html`
- Modify: `docs/superpowers/specs/2026-11-07-sp3b-design-grafico-design.md` (sezione "Scelta dell'utente")

**Interfaces:**
- Produces: la proposta scelta come tabella di token (nomi delle chiavi di `TOKENS` più quelle nuove di Task 2) scritta nella spec, sezione "Scelta dell'utente"; eventuali correzioni dell'utente al layout.

- [ ] **Step 1:** avviare il visual companion (`scripts/start-server.sh --project-dir` sulla radice del repo) e verificare `server-info`.
- [ ] **Step 2:** ogni proposta mostra la stessa schermata: barra della carriera, riga dei filtri con "All filters (N)" e chip, linguette delle viste, tabella (densità media, 12 righe inventate, attributi colorati per fascia), barra laterale chiusa con badge, scheda compatta, e accanto il popup dei filtri aperto sulla scheda Positions. Proposta A: direzione scelta da Claude. Proposta B: caricare la skill `impeccable` e seguirne il processo per una direzione propria. Proposta C: caricare la skill `taste-skill` e seguirne il processo per una direzione propria. Ogni proposta elenca in fondo i suoi token (colori, font, raggi, spaziature, altezze di riga media/compatta).
- [ ] **Step 3:** controllo di fattibilità: nessuna proprietà CSS fuori dai Global Constraints in nessuna delle tre (ricerca nel file di `box-shadow`, `filter`, `transition`, `backdrop`); le tre messe affiancate in `sp3b-compare.html` con scelta cliccabile.
- [ ] **Step 4: punto di arresto.** Mostrare l'URL completo del companion e attendere la scelta dell'utente (una proposta o un mix con indicazioni). Scrivere la scelta e i token nella spec.

### Task 2: Token, densità e preferenze

**Files:**
- Modify: `src/fmxray/ui/theme.py`, `tests/ui/test_theme.py`
- Create: `src/fmxray/ui/settings.py`, `tests/ui/test_settings.py`

**Interfaces:**
- Produces:
  - `theme.py`: `TOKENS` con i valori della proposta scelta più le chiavi nuove `font_numbers` (famiglia per i numeri, con fallback), `row_height_medium`, `row_height_compact`, `chip_background`, `chip_text`, `primary`, `primary_text`; `class Density(StrEnum)`: `MEDIUM = "medium"`, `COMPACT = "compact"`; `row_height(density: Density, tokens: Mapping[str, str] = TOKENS) -> int`; `stylesheet(tokens=TOKENS)` invariato nella firma; `ANIMATION_MS = 150`.
  - `settings.py`: `class UiSettings`: `__init__(self, store: QSettings)`; proprietà `density: Density` (valore non valido o mancante → `Density.MEDIUM`) e `sidebar_open: bool` (default `False`), entrambe con setter che scrivono subito.
- [ ] **Step 1: test** `test_theme.py`: `test_row_heights` (`row_height(Density.COMPACT) < row_height(Density.MEDIUM)`); `test_new_tokens_present`; i test esistenti restano. `test_settings.py` (`QSettings` su un file `.ini` in `tmp_path`): `test_defaults`, `test_roundtrip`, `test_bad_values_fall_back` (`density="huge"`, `sidebar_open="maybe"`).
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.

### Task 3: Chip dei filtri attivi

**Files:**
- Modify: `src/fmxray/application/filters.py`, `tests/application/test_filters.py`
- Create: `src/fmxray/ui/filter_chips.py`, `tests/ui/test_filter_chips.py`

**Interfaces:**
- Produces:
  - `filters.py`: `@dataclass(frozen=True) class Chip(key: str, label: str)`; `describe(state: FilterState) -> tuple[Chip, ...]` in ordine di `FILTER_TABS` (chiave = nome del campo, `"positions"` o `"name_or_club"`); etichette: range `"age 15–21"`, `"pa ≥ 180"`, `"age ≤ 21"`; posizioni `"DC ≥18 · DM ≥15"` (con `" (all)"` in modalità ALL); scelte `"traits: a, b"`; flag `"free agent: yes"`; testi `"club name ~ roma"`; `name_or_club` `"“roma”"`; `remove_chip(state: FilterState, key: str) -> FilterState`.
  - `filter_chips.py`: `class FilterChips(QWidget)`: `set_chips(chips: Sequence[Chip], advanced: str | None = None) -> None` (con `advanced` una sola chip "Advanced filter" con il testo nel tooltip); segnali `chip_removed(str)` e `advanced_removed()`; `labels() -> list[str]`.
- [ ] **Step 1: test** `test_filters.py`: `test_describe_labels` (uno stato con un valore per ogni tipo → etichette esatte qui sopra); `test_remove_chip_each_kind` (per ogni chiave di `describe`, `remove_chip` toglie solo quel filtro); `test_describe_empty`. `test_filter_chips.py`: `test_shows_labels`, `test_click_remove_emits_key`, `test_advanced_chip`.
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.

### Task 4: Linguette delle viste

**Files:**
- Create: `src/fmxray/ui/view_tabs.py`, `tests/ui/test_view_tabs.py`

**Interfaces:**
- Consumes: `ColumnView`, `BUILTIN_VIEWS`, `SEARCH_SCHEMA`.
- Produces: `class ViewTabs(QTabBar)`: `set_views(views: Sequence[ColumnView]) -> None` (pronte poi dell'utente, più una linguetta finale `+`); `current_view() -> ColumnView`; segnali `view_chosen(object)` (`ColumnView` con le sole colonne presenti in `SEARCH_SCHEMA`) e `save_requested()` (click su `+`, che non diventa la linguetta attiva); `show_custom(view: ColumnView) -> None` (aggiunge o aggiorna una linguetta "Custom" prima di `+`).
- [ ] **Step 1: test** `test_view_tabs.py`: `test_builtin_then_user_then_plus`; `test_choosing_emits_view`; `test_plus_requests_save_and_keeps_current`; `test_unknown_columns_dropped` (vista utente con `"gone_field"`); `test_custom_tab`.
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.

### Task 5: Barra laterale delle ricerche salvate

**Files:**
- Create: `src/fmxray/ui/saved_sidebar.py`, `tests/ui/test_saved_sidebar.py`

**Interfaces:**
- Produces: `@dataclass(frozen=True) class SavedEntry(name: str, query_text: str, new: int)`; `class SavedSidebar(QWidget)`: `set_entries(entries: Sequence[SavedEntry]) -> None`; `set_open(open_: bool, animate: bool = True) -> None`; `is_open() -> bool`; `badge_text() -> str` (totale dei nuovi, `""` se zero, visibile anche da chiusa); segnali `search_chosen(str)`, `toggled(bool)`; da chiusa larghezza `SIDEBAR_CLOSED_PX = 44`, da aperta `SIDEBAR_OPEN_PX = 220`, animata su `maximumWidth` con `ANIMATION_MS`.
- [ ] **Step 1: test** `test_saved_sidebar.py`: `test_entries_with_new_counts` (`"wonderkids"` con 3 nuovi → testo dell'elemento contiene `+3`); `test_badge_visible_when_closed` (totale `4` da due ricerche); `test_toggle_without_animation` (`set_open(True, animate=False)` → `maximumWidth() == SIDEBAR_OPEN_PX`); `test_choosing_emits_name`.
- [ ] **Step 2:** FAIL → implementare → PASS; ruff, mypy, lint-imports.

### Task 6: Finestra riordinata e scheda compatta

**Files:**
- Modify: `src/fmxray/ui/main_window.py`, `src/fmxray/ui/player_card.py`, `src/fmxray/ui/quick_filters.py`, `src/fmxray/ui/run.py`, `tests/ui/test_main_window.py`, `tests/ui/test_player_card.py`, `tests/ui/test_quick_filters.py`, `tests/integration/test_real_save.py` se tocca il layout

**Interfaces:**
- Consumes: Task 2–5.
- Produces:
  - `MainWindow(app, session, settings: UiSettings | None = None)` (`None` → `UiSettings(QSettings("fmxray", "fmxray"))`); attributi pubblici: `sidebar: SavedSidebar` (sostituisce `saved_list`), `view_tabs: ViewTabs` (sostituisce `views_list`), `chips: FilterChips`, `text_row: QWidget` (contiene `text_bar` e `text_error`), `density_button: QToolButton` (checkable, "Compact"); restano `quick`, `filters_dialog`, `text_bar`, `text_error`, `table`, `model`, `card`, `empty_label`, `watcher`.
  - Layout: riga 1 = carriera, snapshot, informazioni, Import…, Watch folder…, densità; riga 2 = "All filters (N)" come pulsante principale (proprietà `role="primary"`), filtri rapidi, chip, icona della barra a testo, Save search, Export CSV; `text_row` nascosta di default, mostrata o nascosta con l'icona e con la scorciatoia `TEXT_BAR_SHORTCUT = "Ctrl+K"` (focus sulla barra quando si apre); poi linguette, tabella, scheda; `sidebar` a sinistra.
  - `QuickFilters`: il pulsante "All filters" passa alla riga dei filtri come pulsante principale (`all_button` resta l'attributo pubblico).
  - `PlayerCard`: testata compatta in tre righe (nome + "Copy name"; `età · club · ruoli`; `CA` e `PA` grandi con `font_numbers`); `field_label` resta per tutti i campi delle schede interne; cambio di giocatore con dissolvenza `ANIMATION_MS` (disattivabile: `PlayerCard(animate=False)` nei test).
  - `FiltersDialog`: all'apertura dissolvenza di `windowOpacity` da 0 a 1 in `ANIMATION_MS` (dove la piattaforma non supporta l'opacità della finestra, si apre e basta).
  - Densità: `density_button` alterna media/compatta, applica `row_height` alle righe della tabella e scrive `settings.density`; all'avvio legge `settings.density` e `settings.sidebar_open`.
- [ ] **Step 1: test** `test_main_window.py`: aggiornare `saved_list` → `sidebar`; nuovi `test_text_bar_hidden_by_default_and_toggles` (`text_row` nascosta; `Ctrl+K` la mostra e dà il focus a `text_bar`); `test_rows_above_table` (con `text_row` nascosta, sopra la tabella ci sono solo le due righe: `career_bar` e `filter_bar`); `test_chip_removal_updates_controls` (PA ≥ 180 dai filtri rapidi → chip → rimozione → filtri rapidi e popup vuoti, tabella di nuovo completa); `test_advanced_filter_chip` (testo `age<2 or ca>101` → chip "Advanced filter"; rimozione → filtro vuoto, controlli sbloccati); `test_view_tabs_change_columns` (linguetta Technical → colonne della vista); `test_density_toggle_persists` (`UiSettings` su `.ini` in `tmp_path`: compatta → nuova finestra con le stesse impostazioni parte compatta, altezza riga = `row_height(Density.COMPACT)`). `test_player_card.py`: `test_compact_header` (tre righe di testata, CA e PA presenti). Tutti i test di SP3 restano verdi.
- [ ] **Step 2:** FAIL → implementare → PASS; tutta la suite; ruff, mypy, lint-imports.

### Task 7: Stile applicato, prova dell'utente, wiki, PR

**Files:**
- Modify: `src/fmxray/ui/theme.py` (QSS della proposta scelta), `wiki/modules/ui.md`, `wiki/project/{status,work-tracker,decisions}.md`, `wiki/agent/{handoff,activity}.md`, `wiki/log.md`

- [ ] **Step 1:** QSS completo della proposta scelta in `stylesheet()` (pulsante principale, chip, linguette, barra laterale, tabella media/compatta, popup, scheda); controllo che nessun colore sia scritto fuori da `theme.py`: `grep -rnE "#[0-9a-fA-F]{6}|QColor\(\"" src/fmxray/ui --include=*.py | grep -v theme.py` → nessun risultato.
- [ ] **Step 2:** screenshot offscreen della finestra con dati sintetici (`QWidget.grab()` salvato nella cartella del brainstorm) messo accanto al mockup scelto nel companion; correzioni finché la differenza è solo di dettaglio.
- [ ] **Step 3:** `uv run pytest` (con il save) → verde; ruff, mypy, lint-imports.
- [ ] **Step 4:** l'utente avvia `uv run fmxray-gui` e prova riordino, stile, densità e animazioni; correzioni con TDD.
- [ ] **Step 5:** wiki (pagina `ui` aggiornata con il nuovo layout e i token; decisione sullo stile scelto); revisione finale inline con i Review Focus; `superpowers:verification-before-completion`.
- [ ] **Step 6:** stampare i commit raggruppati (`application`, `ui` e test, wiki), `git push -u origin feat/sp3b-design` e poi la PR con `gh pr create` (descrizione in `local/pr-sp3b.md`, senza attribuzioni).
