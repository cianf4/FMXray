# SP3b — Rifinitura visiva: piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task, inline (no subagents). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** l'app di SP3b con:
- la tabella che riempie lo schermo;
- il look del mockup su fondo nero e accento `#3ea6ff`;
- testo nitido in Inter 11pt;
- la scheda del giocatore in QML con l'esagono delle 6 aree;
- animazioni fluide.

**Architecture:**
- **Esagono:** le aree sono logica di gioco, quindi stanno in `domain/profile.py`, in Python puro.
- **Scheda del giocatore:** diventa un `QQuickWidget` che carica `ui/qml/PlayerCard.qml`.
  - Un `CardModel(QObject)` in `ui/card_model.py` prepara testi, colori e aree.
  - Il QML li mostra soltanto e anima le transizioni.
- **Resto della finestra:** resta in Qt Widgets.
  - Delegato disegnato per le pillole degli attributi.
  - Foglio di stile con `:hover` al posto di `HoverFade`.
  - Barra laterale sovrapposta alla tabella.
- **Colori, font e misure:** vengono tutti da `ui/theme.py`, anche quelli del QML.

**Tech Stack:** come SP3b (Python 3.14, PySide6 6.12.0, pytest-qt 4.5.0, QtAwesome 1.4.2), più i moduli di PySide6 già installati QtQuick, QtQuickWidgets, QtQuick.Shapes e QtQuick.Effects. Font Inter (OFL) al posto di Figtree.

**Spec:** [docs/superpowers/specs/2026-11-08-sp3b-rifinitura-visiva-design.md](../specs/2026-11-08-sp3b-rifinitura-visiva-design.md); in subordine la [spec del design grafico](../specs/2026-11-07-sp3b-design-grafico-design.md).

## Global Constraints

- **Regole dei piani SP1–SP3b:**
  - niente `uv add`, `uv sync`, `git commit`, `git push` da parte di chi esegue;
  - comandi completi, senza segnaposti e senza attribuzioni;
  - si attende "fatto".
- **Branch:** `feat/sp3b-design` (già su origin); la PR si apre dopo questo piano.
- **Nessuna dipendenza Python nuova.** Font: `Inter-Variable.ttf` e `OFL-Inter.txt` in `src/fmxray/ui/fonts/` (sorgente: google/fonts `ofl/inter/Inter[opsz,wght].ttf` e `ofl/inter/OFL.txt`). Figtree e la sua licenza escono.
- **Token** (spec, tabella "Token nuovi"):

  | Token | Valore | Token | Valore |
  | --- | --- | --- | --- |
  | background | `#0e0f12` | primary_text | `#06223a` |
  | surface | `#16181d` | selection | `#163450` |
  | raised | `#1f2228` | chip_background | `#15314a` |
  | border | `#272a31` | chip_text | `#bfe1ff` |
  | text | `#eef1f5` | new | `#3ea6ff` |
  | text_muted | `#8f97a6` | font_text | `Inter` |
  | accent, primary | `#3ea6ff` | font_size | `11pt` |

  - Altezze delle righe: `row_height_medium` 30, `row_height_compact` 24.
  - Raggi: controlli 6, `panel_radius` 10.
  - Bande degli attributi invariate.
- **Animazioni:** `ANIMATION_MS = 150` per i widget, `CARD_ANIMATION_MS = 250` (OutCubic) per la scheda QML. I test non dipendono dalla durata.
- **QML:** nessun colore scritto nei file `.qml`, tutti arrivano da `TOKENS`. I file stanno in `src/fmxray/ui/qml/` e vanno nel wheel.
- **Testi:** interfaccia in inglese con `tr()` / `qsTr()`; nei test nomi inventati.

## Review Focus

1. **Giocatore senza attributi noti** (tutti `None`): l'esagono va al centro, le etichette mostrano "-", nessun crash → test in Task 2 e Task 6.
2. **Portiere che ha anche ruoli di movimento** (`["GK", "DC"]`): usa le aree da portiere; un giocatore senza ruoli usa quelle di movimento → test in Task 2.
3. **Soldi ai bordi delle soglie** (`None`, `999`, `999_999`, negativi): niente `1000K`, niente crash → test in Task 3.
4. **Finestra ridimensionata con la barra laterale aperta:** il pannello sovrapposto segue l'altezza e la tabella non si sposta → test in Task 5.
5. **QML assente o con errori nel pacchetto installato:** il wheel contiene i `.qml`; un errore di caricamento diventa un messaggio leggibile nella scheda, non una finestra vuota senza spiegazione → test in Task 6, verifica del wheel in Task 7.

---

### Task 1: Inter, token e foglio di stile

**Files:**
- Modify: `src/fmxray/ui/theme.py`, `tests/ui/test_theme.py`, `tests/ui/test_icons_fonts.py`
- Fonts: `src/fmxray/ui/fonts/` (via `Figtree-Variable.ttf` e `OFL-Figtree.txt`, dentro `Inter-Variable.ttf` e `OFL-Inter.txt`)

**Interfaces:**
- Produces:
  - in `TOKENS`: i valori dei Global Constraints, più `"panel_radius": "10px"`;
  - `CARD_ANIMATION_MS = 250`;
  - `_FONT_FILES = ("Inter-Variable.ttf", "JetBrainsMono-Variable.ttf")`;
  - QSS con `QFrame#panel { background: $surface; border: 1px solid $border; border-radius: $panel_radius; }` e regole `:hover` per `QPushButton`, `QToolButton` (sfondo `$border`) e `QPushButton[role="primary"]:hover` (accento schiarito, token `primary_hover` = `#6bbaff`);
  - riga sotto il mouse nella tabella: `QTableView::item:hover { background: $raised; }`.

- [ ] **Step 0:** stampare per l'utente un blocco unico, poi attendere "fatto":
  ```bash
  curl -L -o "src/fmxray/ui/fonts/Inter-Variable.ttf" "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf"
  curl -L -o "src/fmxray/ui/fonts/OFL-Inter.txt" "https://github.com/google/fonts/raw/main/ofl/inter/OFL.txt"
  ```
  Chi esegue cancella `Figtree-Variable.ttf` e `OFL-Figtree.txt`.
- [ ] **Step 1: test.**
  - `test_fonts_load`: le famiglie sono `("Inter", "JetBrains Mono")`.
  - `test_new_tokens_present`: `TOKENS["accent"] == "#3ea6ff"`, `TOKENS["background"] == "#0e0f12"`, `TOKENS["font_size"] == "11pt"`, `"panel_radius" in TOKENS`.
  - `test_row_heights`: `row_height(Density.MEDIUM) == 30`, `row_height(Density.COMPACT) == 24`.
  - `test_stylesheet_has_hover_and_panel`: `":hover" in stylesheet()` e `"QFrame#panel" in stylesheet()`.
- [ ] **Step 2:** `uv run pytest tests/ui/test_theme.py tests/ui/test_icons_fonts.py`. Expected: FAIL sui nuovi valori.
- [ ] **Step 3:** aggiornare `theme.py`.
- [ ] **Step 4:** stesso comando. Expected: PASS.

### Task 2: Aree dell'esagono nel domain

**Files:**
- Create: `src/fmxray/domain/profile.py`, `tests/domain/test_profile.py`

**Interfaces:**
- Produces:
  - `Area` (`@dataclass(frozen=True)`, campi `name: str`, `value: float | None`);
  - `OUTFIELD_AREAS` e `GOALKEEPER_AREAS`, entrambi di tipo `tuple[tuple[str, tuple[str, ...]], ...]`, con nomi e attributi esattamente come le due tabelle della spec, nello stesso ordine:
    - movimento: `"Attack"`, `"Technique"`, `"Creativity"`, `"Defence"`, `"Physical"`, `"Mental"`;
    - portieri: `"Shot stopping"`, `"Aerial"`, `"Sweeping"`, `"Distribution"`, `"Physical"`, `"Mental"`;
  - `is_goalkeeper(values: Mapping[str, object]) -> bool`: vero se `"GK"` è in `natural_positions`;
  - `profile(values: Mapping[str, object]) -> tuple[Area, ...]`: sei aree, ognuna la media degli attributi `int` presenti, arrotondata a 1 decimale; `None` se non ce n'è nessuno.

- [ ] **Step 1: test** (`test_profile.py`).
  - `test_every_area_attribute_exists`: ogni nome è in `ATTRIBUTES`.
  - `test_outfield_profile`: tutti gli attributi a 10 tranne `finishing=20` → Attack `12.5`, le altre `10.0`, nomi nell'ordine della spec.
  - `test_missing_attributes_skipped`: Attack con soli `finishing=16` e `heading=12` (gli altri `None`) → `14.0`.
  - `test_no_attributes_gives_none`: `{}` → sei aree con `value is None`.
  - `test_goalkeeper_uses_own_areas`: `natural_positions=["GK", "DC"]` → il primo nome è `"Shot stopping"`.
  - `test_no_positions_is_outfield`: `natural_positions=None` → il primo nome è `"Attack"`.
- [ ] **Step 2:** `uv run pytest tests/domain/test_profile.py`. Expected: FAIL (modulo mancante).
- [ ] **Step 3:** implementare `profile.py`.
- [ ] **Step 4:** stesso comando più `uv run lint-imports`. Expected: PASS, 7 contratti rispettati.

### Task 3: Tabella che riempie lo schermo, soldi compatti, pillole, pannelli

**Files:**
- Create: `src/fmxray/ui/table_delegate.py`, `tests/ui/test_table_delegate.py`
- Modify: `src/fmxray/ui/table_model.py`, `src/fmxray/ui/main_window.py`, `tests/ui/test_table_model.py`, `tests/ui/test_main_window.py`

**Interfaces:**
- Produces:
  - `format_money(value: int | None) -> str`: in `table_model.py`. Sceglie l'unità dopo l'arrotondamento a un decimale e toglie `.0`.
  - Il modello usa `format_money` per le colonne con `Unit.MONEY_INTERNAL`; il `ToolTipRole` di quelle celle è `format_value(value)` (con i separatori).
  - `pill_colors(value: object) -> tuple[QColor, QColor] | None`: in `table_delegate.py`. Restituisce (sfondo, testo): lo sfondo è il colore della banda con alpha 40, il testo è il colore pieno della banda. `None` se il valore non è un `int` tra 1 e 20.
  - `AttributeDelegate(QStyledItemDelegate)`: disegna la pillola (rettangolo arrotondato, raggio 4, centrato, largo quanto il testo + 12 px) per le colonne dei 52 attributi visibili 1–20; per le altre colonne lascia il disegno standard.
  - `MainWindow`:
    - `table_panel: QFrame` e `card_panel: QFrame`, entrambi con objectName `"panel"`, spaziatura 10 px tra i pannelli;
    - `_fit_columns()`: chiamata dopo ogni `set_result`, fa `resizeColumnsToContents()`, poi mette in modalità `Stretch` la colonna `name` (o l'ultima se `name` non c'è) e in `Interactive` le altre;
    - `table.setMouseTracking(True)` per la riga sotto il mouse;
    - il delegato è installato sulla tabella.

- [ ] **Step 1: test.**
  - `test_format_money`: `None`→`"-"`, `999`→`"999"`, `950_000`→`"950K"`, `12_500`→`"12.5K"`, `4_200_000`→`"4.2M"`, `999_999`→`"1M"`, `-2_500`→`"-2.5K"`.
  - `test_money_tooltip_is_full`: tooltip `"187,061,600"`, testo `"187.1M"`.
  - `test_pill_colors`: `3`→ testo `band_1`, `18`→ testo `band_4`, `None` / `"x"` / `0` / `21`→`None`.
  - `test_table_fills_width`, in `test_main_window.py`: finestra 1600×900, `show()`; la somma delle larghezze delle colonne è uguale alla larghezza del viewport della tabella, ±2 px.
  - `test_panels`: `window.table_panel.objectName() == "panel"` e la tabella è discendente di `table_panel`.
- [ ] **Step 2:** `uv run pytest tests/ui/test_table_model.py tests/ui/test_table_delegate.py tests/ui/test_main_window.py`. Expected: FAIL sui nuovi test.
- [ ] **Step 3:** implementare.
- [ ] **Step 4:** stesso comando. Expected: PASS.

### Task 4: Filtri rapidi compatti

**Files:**
- Modify: `src/fmxray/ui/range_slider.py`, `src/fmxray/ui/quick_filters.py`, `tests/ui/test_quick_filters.py`

**Interfaces:**
- Produces:
  - `RangeControl(field, parent=None, min_only: bool = False)`: con `min_only` mostra un solo campo con placeholder `"min"`, `range()` restituisce `Range(min, None)`, `set_range` ignora il massimo;
  - `QuickFilters`: `age` normale, `ca` e `pa` con `min_only=True` ed etichette `"CA ≥"` e `"PA ≥"`.

- [ ] **Step 1: test.**
  - `test_min_only_control`: si scrive `150` → `Range(150, None)`; `set_range(Range(120, 180))` mostra `120` e `range()` restituisce `Range(120, None)`.
  - `test_quick_ca_is_min_only`: `quick.range_control("ca")` ha un solo campo visibile.
  - I test esistenti di `QuickFilters` restano verdi. Quelli che impostano un massimo su CA/PA rapidi passano al popup.
- [ ] **Step 2:** eseguire i test. Expected: FAIL.
- [ ] **Step 3:** implementare.
- [ ] **Step 4:** stesso comando, più `tests/ui/test_main_window.py`. Expected: PASS.

### Task 5: Animazioni leggere: hover nel foglio di stile, barra laterale sovrapposta

**Files:**
- Modify: `src/fmxray/ui/motion.py`, `src/fmxray/ui/saved_sidebar.py`, `src/fmxray/ui/main_window.py`, `tests/ui/test_motion.py`, `tests/ui/test_saved_sidebar.py`, `tests/ui/test_main_window.py`

**Interfaces:**
- Produces:
  - `HoverFade` rimosso, con i suoi test e il suo uso in `main_window`;
  - `SavedSidebar(overlay_parent: QWidget, parent: QWidget | None = None)`:
    - **striscia:** il widget stesso, nel layout, larghezza fissa `SIDEBAR_CLOSED_PX`, con stella e badge;
    - **pannello:** `panel: QFrame`, figlio di `overlay_parent`, fuori dal layout, che contiene `list`;
    - **apertura e chiusura:** `set_open` anima la `geometry` del pannello da larghezza 0 a `SIDEBAR_OPEN_PX`, ancorato al bordo destro della striscia, a tutta altezza di `overlay_parent`. Da chiuso il pannello è nascosto.
    - **ridimensionamento:** un event filter su `overlay_parent` (evento `Resize`) aggiorna l'altezza del pannello.
  - Restano invariati `set_entries`, `badge_text`, `toggled`, `search_chosen`.

- [ ] **Step 1: test.**
  - `test_sidebar_strip_keeps_width`: da aperta `sidebar.width() == SIDEBAR_CLOSED_PX` e `sidebar.panel.width() == SIDEBAR_OPEN_PX`; da chiusa `not sidebar.panel.isVisible()`.
  - `test_open_sidebar_does_not_move_table`, in `test_main_window`: la `geometry()` della tabella è la stessa prima e dopo `set_open(True, animate=False)`.
  - `test_panel_follows_resize`: con la barra aperta, la finestra passa da 900 a 700 di altezza e il pannello è alto quanto il suo `overlay_parent`.
  - I test esistenti del badge da chiusa restano.
- [ ] **Step 2:** eseguire i test. Expected: FAIL.
- [ ] **Step 3:** implementare.
- [ ] **Step 4:** `uv run pytest tests/ui`. Expected: PASS.

### Task 6: Scheda del giocatore in QML con esagono

**Files:**
- Create:
  - `src/fmxray/ui/card_model.py`
  - `src/fmxray/ui/qml/PlayerCard.qml`, `Hexagon.qml`, `FieldGrid.qml`, `MiniPitch.qml`
  - `tests/ui/test_card_model.py`
- Modify: `src/fmxray/ui/player_card.py` (riscritto), `tests/ui/test_player_card.py` (riscritto), `src/fmxray/ui/main_window.py` (solo il pannello della scheda)

**Interfaces:**
- Consumes:
  - `profile`, `is_goalkeeper` (Task 2);
  - `TOKENS`, `CARD_ANIMATION_MS`, `attribute_band` (Task 1);
  - `format_value`, `format_money` (Task 3);
  - `_PLACES` e `position_label` di `ui/pitch.py`: `_PLACES` diventa pubblico come `PLACES`.
- Produces:
  - **`CardModel(QObject)`**:
    - metodi `set_player(meta: SnapshotMeta, values: Mapping[str, object]) -> None` e `clear() -> None`;
    - un segnale `changed`;
    - proprietà Qt in sola lettura, tutte con `notify=changed`. Le liste di `dict` restano semplici, così il QML le legge come modello:

      | Proprietà | Tipo | Contenuto |
      | --- | --- | --- |
      | `empty` | `bool` | |
      | `name` | `str` | |
      | `initials` | `str` | massimo 2 lettere |
      | `summary` | `str` | `summary_line` attuale |
      | `ca`, `pa` | `str` | |
      | `caFraction`, `paFraction` | `float` | valore/200, limitato a 0–1, 0 se manca |
      | `growth` | `str` | `"room to grow 57"` o `""` |
      | `areas` | `list[dict]` | `{"name", "value": float (0 se None), "label": "15.0" o "-"}` |
      | `tabs` | `list[dict]` | `{"title", "groups": [{"title", "rows": [{"label", "value", "color"}]}]}` |
      | `positions` | `list[dict]` | `{"label", "row", "column", "value", "color"}` |
      | `unconfirmed` | `bool` | |

    - le tabs hanno gli stessi titoli e campi di `_TABS` della scheda attuale;
    - nelle righe dei rated `color` è il token della banda, altrimenti `TOKENS["text"]`; i soldi passano da `format_money`.
  - **`PlayerCard(QWidget)`**:
    - `show_player(meta, values)`, `clear()`, `copy_name()`;
    - attributi `model: CardModel` e `view: QQuickWidget`;
    - `setMinimumWidth(320)`;
    - il contesto QML riceve `card` (il modello) e `theme` (`dict(TOKENS)` più `animationMs`);
    - se `view.status()` è `Error`, mostra al posto della vista una `QLabel` con il testo degli errori.
  - **QML**, contenuto della spec, sezione "Scheda in QML":
    - **testata:** iniziali, nome, pulsante copia che chiama `card.copyName()`, riepilogo, CA/PA, barra di crescita;
    - **`Hexagon`:** `Shape` con griglia a 3 anelli e poligono; sei proprietà `real v0…v5` con `Behavior on vN { NumberAnimation { duration: theme.animationMs; easing.type: Easing.OutCubic } }`;
    - **linguette:** fila di pulsanti testuali con sottolineatura accento, poi `FieldGrid` per gruppo e `MiniPitch` per Positions;
    - **resto:** nota non confermati, stato vuoto `"Select a player"`, ombra `MultiEffect` sul pannello. CA e PA scorrono con `Behavior on` di una proprietà numerica mostrata con `Math.round`.

- [ ] **Step 1: test** (`test_card_model.py`, senza QML).
  - `test_header`: `ca=131`, `pa=188` → `ca == "131"`, `growth == "room to grow 57"`, `caFraction == 0.655`.
  - `test_initials`: `"Ünal Çelik"` → `"ÜÇ"`; nome `None` → `""`.
  - `test_areas_from_profile`: sei `areas`, la prima `"Attack"`, `label` con un decimale.
  - `test_empty_player_areas`: tutti gli attributi `None` → ogni `value == 0` e `label == "-"`.
  - `test_tabs_cover_all_fields`: ogni attributo di `ATTRIBUTES` e di `PERSONALITY` compare in qualche `rows[*]["label"]`, come nel vecchio `test_attribute_tabs_show_all_attributes`.
  - `test_band_colours`: `finishing=3` → `color == TOKENS["band_1"]`.
  - `test_unconfirmed_flag`: provenienze di default → `True`; tutte `VERIFIED` → `False`.
  - `test_clear`: `empty` è `True` e `name == ""`.
  - `test_positions`: 15 voci, `"ST"` alla riga 0.
- [ ] **Step 2: test** (`test_player_card.py`, riscritto).
  - `test_qml_loads`: `card.view.status() == QQuickWidget.Status.Ready` e `card.view.errors() == []`.
  - `test_copy_name_to_clipboard`: via `card.copy_name()`.
  - `test_shows_player_without_errors`: `show_player` e poi `clear()`; nessun errore QML, e la proprietà `v0` dell'oggetto `Hexagon` (trovato con `objectName` `"hexagon"`) è un numero.
  - `test_qml_error_is_shown`: `PlayerCard(qml=Path("missing.qml"))` mostra una `QLabel` di errore. Per questo il costruttore accetta il parametro `qml: Path = CARD_QML`.
- [ ] **Step 3:** `uv run pytest tests/ui/test_card_model.py tests/ui/test_player_card.py`. Expected: FAIL.
- [ ] **Step 4:** implementare `card_model.py`, i QML e `player_card.py`. In `main_window` la scheda va nel `card_panel`.
- [ ] **Step 5:** `uv run pytest tests/ui`. Expected: PASS.

### Task 7: Verifica, prova dell'utente, wiki

**Files:**
- Modify:
  - wiki: `wiki/modules/ui.md`, `wiki/project/decisions.md` (D27: scheda in QML, Inter, accento `#3ea6ff`), `wiki/project/status.md`, `wiki/project/work-tracker.md`, `wiki/agent/handoff.md`, `wiki/agent/activity.md`, `wiki/log.md`;
  - `local/pr-sp3b.md`.

- [ ] **Step 1:** tutti i controlli della CI:
  ```bash
  uv run ruff check
  uv run ruff format --check
  uv run mypy src tests
  uv run lint-imports
  uv run pytest
  ```
  Expected: tutto verde.
- [ ] **Step 2: verifica del wheel.** `uv build --wheel -o` nella cartella scratchpad, poi listare il contenuto. Expected: ci sono `fmxray/ui/qml/*.qml` e `fmxray/ui/fonts/Inter-Variable.ttf`, non c'è Figtree. Se i `.qml` mancano, ruling e regola in `pyproject.toml`.
- [ ] **Step 3: screenshot a 1920×1040 con il save reale** (offscreen):
  - la tabella riempie la larghezza;
  - nella scheda ci sono l'esagono e la barra di crescita;
  - confronto col mockup C;
  - correzioni in un solo passaggio.
- [ ] **Step 4: prova dell'utente.** L'utente lancia `uv run fmxray-gui` e prova:
  - schermo intero;
  - cambio di giocatore (l'esagono si trasforma);
  - barra laterale;
  - hover;
  - densità.
- [ ] **Step 5:** aggiornare la wiki e `local/pr-sp3b.md`.
- [ ] **Step 6:** stampare i commit raggruppati, poi `git push` e il comando `gh pr create` già usato per SP3b:
  - `docs` per spec e piano;
  - `build(ui)` per i font;
  - `feat(domain)` per le aree;
  - `feat(ui)` per tabella, filtri, animazioni e scheda;
  - `docs` per la wiki.
