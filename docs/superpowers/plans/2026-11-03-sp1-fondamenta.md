# SP1 — Fondamenta: piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task, inline (no subagents). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** un comando `fmxray import` legge un save FM27 reale, ne fa uno snapshot Parquet registrato in un catalogo SQLite, con architettura esagonale verificata da import-linter e CI verde su Linux e Windows.

**Architecture:** pacchetti `domain` (catalogo campi, snapshot), `application` (porte `Protocol`, caso d'uso `ImportSave`), `adapters` (`fmsave_source`, `parquet_store`, `sqlite_catalog`), `cli` (argparse), `bootstrap` (composition root). Solo `fmsave_source` importa fmsave e usa `Table.to_columns()` (niente extra `polars` di fmsave): il DataFrame lo costruiamo noi con lo schema del catalogo.

**Tech Stack:** Python 3.14, uv, fmsave 0.9.3, Polars 2.x, platformdirs, sqlite3 e hashlib della stdlib; ruff, mypy, pytest, Hypothesis, import-linter.

**Spec:** [docs/superpowers/specs/2026-11-03-sp1-fondamenta-design.md](../specs/2026-11-03-sp1-fondamenta-design.md); in subordine la [spec madre](../specs/2026-11-03-fm-x-ray-design.md).

## Global Constraints

- `requires-python = ">=3.14"`; build backend `uv_build`; layout `src/fmxray`.
- Runtime: `fmsave==0.9.3`, `polars>=2.1,<3`, `platformdirs>=4.14`. Dev (gruppo `dev`): `pytest>=9.2`, `hypothesis>=6.170`, `mypy>=2.4`, `ruff>=0.17`, `import-linter>=2.15`. Nient'altro.
- **Processo:** chi esegue **non** lancia `uv sync`/`uv add`, `git commit` o `git push`: stampa il comando, l'utente lo lancia, poi si prosegue. Ogni comando stampato è completo, senza segnaposti. Messaggi di commit senza attribuzioni a Claude.
- Prima di usare un'API di Polars, fmsave, platformdirs o import-linter, verificarla nel pacchetto installato (`uv run python -c "import inspect, X; print(inspect.signature(...))"`) o nella sua documentazione per la versione bloccata.
- Solo `fmxray.adapters.fmsave_source` importa `fmsave`. Nessun tipo di fmsave esce dall'adattatore.
- `__main__.py` contiene solo la chiamata a `fmxray.bootstrap.main`.
- Nessun file di gioco in git; i test reali leggono `FMXRAY_TEST_SAVE` o `local/saves/**/*.fm`.
- Codice, identificatori, messaggi CLI in inglese; documenti in italiano.
- Su FM27 la provenienza di ogni campo letto è `UNCONFIRMED`; i campi calcolati da noi sono `DERIVED`.
- Soldi sempre nell'unità interna del save (nessuna conversione in SP1).

## Review Focus

1. **Save che cambia durante l'import** (FM che salva mentre copiamo): hash e lettura si fanno sulla **copia**, mai sull'originale → test in Task 4.
2. **Percorsi con spazi, parentesi e Unicode** (`Roma 2 (v02).fm`, cartelle Proton): import e CLI funzionano → test in Task 4 e Task 8.
3. **Stesso save in due carriere diverse**: consentito; lo stesso save due volte nella stessa carriera → "already imported" → test in Task 6 e Task 4.
4. **Nome giocatore ambiguo o con accenti in `show`**: ricerca senza maiuscole e accenti; più risultati → elenco con `uid`, nessuna scelta arbitraria → test in Task 8.
5. **Errore a metà import** (catalogo che fallisce dopo la scrittura del Parquet): nessun file orfano e nessuna riga nel catalogo → test in Task 4 e Task 5.

---

### Task 1: Scheletro del progetto, strumenti e CI

**Files:**
- Create: `pyproject.toml`, `src/fmxray/__init__.py`, `src/fmxray/__main__.py`, `src/fmxray/bootstrap.py`, `src/fmxray/{domain,application,adapters,cli}/__init__.py`, `src/fmxray/adapters/{fmsave_source,parquet_store,sqlite_catalog}/__init__.py`, `src/fmxray/py.typed`, `tests/__init__.py`, `tests/conftest.py`, `tests/test_smoke.py`, `.github/workflows/ci.yml`, `.python-version`
- Modify: `.gitignore` (aggiungere `.hypothesis/`)

**Interfaces:**
- Produces: `fmxray.bootstrap.main(argv: Sequence[str] | None = None) -> int` (per ora stampa la versione e ritorna 0); entry point `fmxray = "fmxray.bootstrap:main"`; marker pytest `real_save`.

- [ ] **Step 1:** Scrivere `pyproject.toml` con: metadati (`name = "fmxray"`, `version = "0.1.0"`, licenza MIT), dipendenze e gruppo `dev` dei Global Constraints, `[project.scripts]`, `[tool.ruff]` (`target-version = "py314"`, `line-length = 100`, `select = ["E","F","W","I","B","UP","SIM","RUF"]`), `[tool.mypy]` (`strict = true`, `python_version = "3.14"`), `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `addopts = "-ra --strict-markers"`, marker `real_save: needs a real FM save, skipped when absent`).
- [ ] **Step 2:** Contratti `[tool.importlinter]` in `pyproject.toml`, `root_package = "fmxray"`, `include_external_packages = true`:
  1. *forbidden* `fmxray.domain` → `fmxray.application`, `fmxray.adapters`, `fmxray.cli`, `fmxray.bootstrap`;
  2. *forbidden* `fmxray.application` → `fmxray.adapters`, `fmxray.cli`, `fmxray.bootstrap`;
  3. *forbidden* `fmxray.cli` → `fmxray.adapters`, `fmxray.bootstrap`;
  4. *forbidden* `fmxray.domain`, `fmxray.application`, `fmxray.cli`, `fmxray.adapters.parquet_store`, `fmxray.adapters.sqlite_catalog` → `fmsave` (con indirect imports ammessi, così `bootstrap` può importare l'adattatore; verificare il nome esatto dell'opzione nella doc di import-linter 2.15);
  5. *independence* tra `fmxray.adapters.fmsave_source`, `fmxray.adapters.parquet_store`, `fmxray.adapters.sqlite_catalog`.
- [ ] **Step 3:** `.python-version` con `3.14`; `__main__.py` = `from fmxray.bootstrap import main` + `raise SystemExit(main())`; `bootstrap.main` stampa `fmxray 0.1.0` (da `importlib.metadata.version("fmxray")`).
- [ ] **Step 4:** `tests/test_smoke.py::test_main_prints_version` — `main([])` ritorna `0` e lo stdout (`capsys`) contiene `fmxray 0.1.0`.
- [ ] **Step 5:** `.github/workflows/ci.yml`: trigger `push` e `pull_request`; matrice `os: [ubuntu-latest, windows-latest]`; passi checkout, setup-uv (ultime major di `actions/checkout` e `astral-sh/setup-uv`, verificate sulle loro pagine di release), `uv sync --locked`, `uv run ruff check`, `uv run ruff format --check`, `uv run mypy src tests`, `uv run lint-imports`, `uv run pytest`, e un passo `git ls-files "*.fm" "*.fmf"` che fallisce se l'output non è vuoto.
- [ ] **Step 6:** Stampare per l'utente e attendere: `uv sync`
- [ ] **Step 7:** Verifica: `uv run pytest` → 1 passed; `uv run ruff check`, `uv run ruff format --check`, `uv run mypy src tests`, `uv run lint-imports` → nessun errore, 5 contratti kept.
- [ ] **Step 8:** Stampare per l'utente: `git add -A && git commit -m "build: scheletro del progetto, strumenti e CI"`

### Task 2: Catalogo dei campi

**Files:**
- Create: `src/fmxray/domain/fields.py`, `tests/domain/__init__.py`, `tests/domain/test_fields.py`

**Interfaces:**
- Produces:
  - `class Provenance(StrEnum)`: `VERIFIED = "verified"`, `UNCONFIRMED = "unconfirmed"`, `DERIVED = "derived"`, `ESTIMATE = "estimate"`.
  - `class FieldGroup(StrEnum)`: `IDENTITY, NATIONALITY, CLUB, ABILITY, REPUTATION, TECHNICAL, MENTAL, PHYSICAL, GOALKEEPING, HIDDEN, PERSONALITY, FEET, POSITIONS, CONDITION, VALUE, CONTRACT, LOAN, TRAITS`.
  - `class Unit(StrEnum)`: `NONE, RAW_1_100, DISPLAY_1_20, MONEY_INTERNAL, CM, DATE, RAW_0_10000`.
  - `@dataclass(frozen=True) class FieldSpec`: `name: str`, `dtype: pl.DataType`, `group: FieldGroup`, `unit: Unit = Unit.NONE`.
  - `ATTRIBUTES: tuple[str, ...]` — i 52 nomi nell'ordine di `fmsave.Attributes` (`crossing` … `concentration`, vedi `wiki/reference/fmsave.md`).
  - `HIDDEN_ATTRIBUTES = ("dirtiness", "consistency", "important_matches", "injury_proneness", "versatility")`.
  - `PERSONALITY = ("adaptability", "ambition", "loyalty", "pressure", "professionalism", "sportsmanship", "temperament", "controversy")`.
  - `POSITIONS = ("gk","sw","dl","dc","dr","dm","ml","mc","mr","aml","amc","amr","stc","wbl","wbr")`.
  - `RELEASE_CLAUSES: Mapping[str, str]` — colonna nostra → `kind` di fmsave: `release_fee_min → minimum_fee_release`, `release_fee_domestic → minimum_fee_release_domestic`, `release_fee_foreign → minimum_fee_release_foreign`, `release_fee_domestic_higher → minimum_fee_release_domestic_higher_division`, `relegation_release_fee → relegation_release`, `non_promotion_release_fee → non_promotion_release`.
  - `class FieldCatalog`: `fields: tuple[FieldSpec, ...]`; `names() -> tuple[str, ...]`; `get(name: str) -> FieldSpec` (KeyError se assente); `in_group(group: FieldGroup) -> tuple[FieldSpec, ...]`; `polars_schema() -> pl.Schema`.
  - `PLAYER_CATALOG: FieldCatalog`. Regole di nome: attributo in scala 1–20 = nome dell'attributo, scala 1–100 = `<nome>_raw`; personalità = nome; posizioni = `pos_<codice>`; `ca`, `pa`; il resto come le colonne piatte di fmsave senza prefisso dove non ambiguo (`uid`, `unique_id`, `name`, `full_name`, `birth_date`, `age`, `nation_id`, `second_nation_ids`, `height_cm`, `club_uid`, `club_name`, `club_reputation`, `natural_positions`, `accomplished_positions`, `left_foot`, `right_foot`, `left_foot_raw`, `right_foot_raw`, `reputation_current`, `reputation_world`, `reputation_home`, `transfer_value`, `transfer_value_state`, `condition_raw`, `match_sharpness_raw`, `traits`, `on_loan`, `loan_parent_club_uid`, `loan_parent_club_name`, `loan_end`, `contract_wage`, `contract_start`, `contract_end`, `contract_squad_status`) più le colonne di `RELEASE_CLAUSES`. Gruppi: gli attributi tecnici/mentali/fisici/portiere come nell'interfaccia di FM; i 5 hidden in `HIDDEN` in entrambe le scale.

- [ ] **Step 1: test** in `tests/domain/test_fields.py`:
  - `test_names_are_unique` — `len(set(PLAYER_CATALOG.names())) == len(PLAYER_CATALOG.names())`.
  - `test_every_attribute_in_both_scales` — per ogni `a in ATTRIBUTES`: `get(a).unit is Unit.DISPLAY_1_20` e `get(f"{a}_raw").unit is Unit.RAW_1_100`; `len(ATTRIBUTES) == 52`.
  - `test_thirteen_hidden_values` — i 5 `HIDDEN_ATTRIBUTES` (e i loro `_raw`) stanno in `FieldGroup.HIDDEN`; gli 8 `PERSONALITY` in `FieldGroup.PERSONALITY`.
  - `test_money_fields_are_internal_units` — `transfer_value`, `contract_wage` e tutte le chiavi di `RELEASE_CLAUSES` hanno `Unit.MONEY_INTERNAL`.
  - `test_polars_schema_matches_fields` — `list(PLAYER_CATALOG.polars_schema().names()) == list(PLAYER_CATALOG.names())`.
  - `test_get_unknown_field_raises` — `get("nope")` solleva `KeyError`.
- [ ] **Step 2:** `uv run pytest tests/domain/test_fields.py -v` → FAIL (modulo assente).
- [ ] **Step 3:** Implementare `fields.py`. Tipi Polars: interi `pl.Int64` (ID, soldi) o `pl.Int16` (attributi, CA/PA, posizioni), date `pl.Date`, tuple `pl.List(pl.Utf8)` / `pl.List(pl.Int64)`, booleani `pl.Boolean`, stringhe `pl.Utf8`.
- [ ] **Step 4:** test → PASS; `uv run mypy src tests` e `uv run lint-imports` puliti.
- [ ] **Step 5:** Stampare: `git add -A && git commit -m "feat(domain): catalogo dei campi giocatore"`

### Task 3: Snapshot e factory di test

**Files:**
- Create: `src/fmxray/domain/snapshot.py`, `src/fmxray/domain/errors.py`, `tests/factories.py`, `tests/domain/test_snapshot.py`

**Interfaces:**
- Consumes: `PLAYER_CATALOG`, `Provenance` (Task 2).
- Produces:
  - `class SchemaMismatchError(ValueError)` in `domain/errors.py` (messaggio con colonne mancanti, in più, tipi diversi).
  - `@dataclass(frozen=True) class SnapshotMeta`: `snapshot_id: str`, `career_id: int`, `game: str`, `build: str`, `known_build: bool`, `db_version: str`, `game_date: date | None`, `imported_at: datetime` (UTC, aware), `source_sha256: str`, `source_kind: str`, `reader_version: str`, `row_count: int`, `provenance: Mapping[str, Provenance]`, `warnings: tuple[str, ...]`.
  - `@dataclass(frozen=True) class Snapshot`: `meta: SnapshotMeta`, `frame: pl.DataFrame`; `__post_init__` chiama `validate_frame(frame, PLAYER_CATALOG)` e verifica `meta.row_count == frame.height`.
  - `validate_frame(frame: pl.DataFrame, catalog: FieldCatalog) -> None` — solleva `SchemaMismatchError` se nomi o tipi (in ordine) differiscono da `catalog.polars_schema()`.
  - `tests/factories.py`: `make_player_frame(n: int = 3, **overrides: list[object]) -> pl.DataFrame` (valori validi e deterministici, nomi con accenti inclusi: `"Ünal Çelik"`); `make_meta(**overrides: object) -> SnapshotMeta`.

- [ ] **Step 1: test** `tests/domain/test_snapshot.py`:
  - `test_valid_snapshot_builds` — `Snapshot(make_meta(row_count=3), make_player_frame(3))` non solleva.
  - `test_missing_column_raises` — frame senza `ca` → `SchemaMismatchError` con `"ca"` nel messaggio.
  - `test_wrong_dtype_raises` — `ca` castata a `pl.Utf8` → `SchemaMismatchError`.
  - `test_row_count_must_match` — `row_count=5` con 3 righe → `ValueError`.
  - `test_factory_frames_always_valid` (Hypothesis, `n` in 0..50) — `validate_frame(make_player_frame(n), PLAYER_CATALOG)` non solleva.
- [ ] **Step 2:** test → FAIL. **Step 3:** implementare. **Step 4:** test → PASS, mypy e lint-imports puliti.
- [ ] **Step 5:** Stampare: `git add -A && git commit -m "feat(domain): snapshot con validazione dello schema"`

### Task 4: Porte ed ImportSave

**Files:**
- Create: `src/fmxray/application/ports.py`, `src/fmxray/application/errors.py`, `src/fmxray/application/import_save.py`, `tests/application/__init__.py`, `tests/application/fakes.py`, `tests/application/test_import_save.py`

**Interfaces:**
- Consumes: `Snapshot`, `SnapshotMeta`, `Provenance` (Task 2–3).
- Produces:
  - `@dataclass(frozen=True) class SaveReading`: `game: str`, `build: str`, `known_build: bool`, `db_version: str`, `game_date: date | None`, `reader_version: str`, `warnings: tuple[str, ...]`, `provenance: Mapping[str, Provenance]`, `frame: pl.DataFrame`.
  - `class SaveSource(Protocol)`: `read(self, path: Path) -> SaveReading`.
  - `class SnapshotStore(Protocol)`: `write(self, snapshot: Snapshot) -> None`; `read(self, career_id: int, snapshot_id: str) -> pl.DataFrame`; `delete(self, career_id: int, snapshot_id: str) -> None`.
  - `class CatalogStore(Protocol)`: `get_or_create_career(self, name: str) -> int`; `find_career(self, name: str) -> int | None`; `find_by_sha256(self, career_id: int, sha256: str) -> SnapshotMeta | None`; `add_snapshot(self, meta: SnapshotMeta) -> None`; `list_snapshots(self, career_id: int | None = None) -> list[SnapshotMeta]`; `latest_snapshot(self, career_id: int) -> SnapshotMeta | None`.
  - `application/errors.py`: `class FmxrayError(Exception)`; `UnreadableSaveError(FmxrayError)`; `UnsupportedSaveError(FmxrayError)`; `CareerNotFoundError(FmxrayError)`.
  - `class ImportStatus(StrEnum)`: `IMPORTED = "imported"`, `ALREADY_IMPORTED = "already_imported"`.
  - `@dataclass(frozen=True) class ImportResult`: `status: ImportStatus`, `meta: SnapshotMeta`.
  - `class ImportSave`: `__init__(self, source: SaveSource, store: SnapshotStore, catalog: CatalogStore, workdir: Path, clock: Callable[[], datetime])`; `execute(self, save_path: Path, career_name: str) -> ImportResult`.
  - `tests/application/fakes.py`: `FakeSaveSource(reading: SaveReading | Exception)` che registra i path letti; `InMemorySnapshotStore`; `InMemoryCatalogStore(fail_on_add: bool = False)`.

Algoritmo di `execute` (fissato):
1. `career_id = catalog.get_or_create_career(career_name)`.
2. Copia `save_path` in una `tempfile.TemporaryDirectory(dir=workdir)` mantenendo il nome del file.
3. `sha256` della **copia** con `hashlib.file_digest`.
4. Se `catalog.find_by_sha256(career_id, sha256)` esiste → `ImportResult(ALREADY_IMPORTED, meta_esistente)` senza leggere.
5. `reading = source.read(copia)`; `snapshot_id = str(uuid.uuid7())`; costruisce `SnapshotMeta` (`source_kind="fmsave"`, `imported_at=clock()`) e `Snapshot`.
6. `store.write(snapshot)`; poi `catalog.add_snapshot(meta)`; se `add_snapshot` solleva → `store.delete(career_id, snapshot_id)` e rilancia.

- [ ] **Step 1: test** `tests/application/test_import_save.py`:
  - `test_imports_new_save` — status `IMPORTED`, 1 snapshot nello store e nel catalogo, `meta.row_count == 3`, `meta.game == "FM27"`.
  - `test_same_save_twice_is_already_imported` — seconda chiamata → `ALREADY_IMPORTED`, `FakeSaveSource` letto una volta sola.
  - `test_reads_and_hashes_the_copy_not_the_original` — la fake source verifica che il path letto non sia `save_path`; dopo l'import si modifica l'originale e un nuovo import produce un altro snapshot (hash diverso).
  - `test_path_with_spaces_and_parentheses` — save in `tmp_path / "Proton dir" / "Roma 2 (v02).fm"` → `IMPORTED`.
  - `test_catalog_failure_removes_written_snapshot` — `InMemoryCatalogStore(fail_on_add=True)` → l'eccezione esce e lo store è vuoto.
  - `test_source_error_writes_nothing` — `FakeSaveSource(UnreadableSaveError("x"))` → l'errore esce, store e catalogo senza snapshot.
  - `test_temporary_copy_is_removed` — dopo `execute` (anche in errore) `workdir` è vuota.
- [ ] **Step 2:** test → FAIL. **Step 3:** implementare. **Step 4:** test → PASS, mypy e lint-imports puliti.
- [ ] **Step 5:** Stampare: `git add -A && git commit -m "feat(application): porte e caso d'uso ImportSave"`

### Task 5: Snapshot store Parquet

**Files:**
- Create: `src/fmxray/adapters/parquet_store/store.py`, `tests/adapters/__init__.py`, `tests/adapters/test_parquet_store.py`
- Modify: `src/fmxray/adapters/parquet_store/__init__.py` (esporta `ParquetSnapshotStore`)

**Interfaces:**
- Consumes: porta `SnapshotStore`, `Snapshot` (Task 3–4).
- Produces: `class ParquetSnapshotStore`: `__init__(self, root: Path)`; implementa `SnapshotStore`. File in `root / str(career_id) / f"{snapshot_id}.parquet"`, compressione `zstd`; scrittura su `…parquet.tmp` nella stessa cartella poi `os.replace`; `read` restituisce il DataFrame con lo schema del catalogo; `delete` di un file assente non solleva.

- [ ] **Step 1: test**: `test_roundtrip_preserves_frame` (`read(...)` `.equals(frame)` incluse liste, date e stringhe con accenti); `test_no_tmp_file_left_after_write`; `test_failed_write_leaves_no_file` (monkeypatch di `pl.DataFrame.write_parquet` che solleva → nessun `.parquet` né `.tmp`); `test_delete_missing_is_noop`; `test_read_missing_raises_file_not_found`.
- [ ] **Step 2:** FAIL. **Step 3:** implementare (verificare `write_parquet(compression="zstd")` e `read_parquet` in Polars 2.x). **Step 4:** PASS, mypy, lint-imports.
- [ ] **Step 5:** Stampare: `git add -A && git commit -m "feat(adapters): snapshot store su Parquet"`

### Task 6: Catalogo SQLite

**Files:**
- Create: `src/fmxray/adapters/sqlite_catalog/catalog.py`, `src/fmxray/adapters/sqlite_catalog/schema.py`, `tests/adapters/test_sqlite_catalog.py`
- Modify: `src/fmxray/adapters/sqlite_catalog/__init__.py` (esporta `SqliteCatalogStore`)

**Interfaces:**
- Consumes: porta `CatalogStore`, `SnapshotMeta`, `Provenance`.
- Produces: `class SqliteCatalogStore`: `__init__(self, db_path: Path)` (crea il file e applica le migrazioni); implementa `CatalogStore`; `close(self) -> None`; context manager.
  - `schema.py`: `MIGRATIONS: tuple[str, ...]` (indice = versione − 1) e `migrate(conn: sqlite3.Connection) -> None` che porta `PRAGMA user_version` all'ultima.
  - Versione 1: `careers(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)`; `snapshots(id TEXT PRIMARY KEY, career_id INTEGER NOT NULL REFERENCES careers(id), game TEXT NOT NULL, build TEXT NOT NULL, known_build INTEGER NOT NULL, db_version TEXT NOT NULL, game_date TEXT, imported_at TEXT NOT NULL, source_sha256 TEXT NOT NULL, source_kind TEXT NOT NULL, reader_version TEXT NOT NULL, row_count INTEGER NOT NULL, provenance_json TEXT NOT NULL, warnings_json TEXT NOT NULL, UNIQUE(career_id, source_sha256))`; `PRAGMA foreign_keys = ON`.
  - `list_snapshots` e `latest_snapshot` ordinano per `game_date` (NULL per ultimi) poi `imported_at`.

- [ ] **Step 1: test**: `test_career_is_created_once`; `test_add_and_find_by_sha256` (meta letto == meta scritto, provenienze e `game_date=None` inclusi); `test_same_sha_in_two_careers_is_allowed`; `test_duplicate_sha_in_same_career_raises` (`sqlite3.IntegrityError`); `test_latest_snapshot_orders_by_game_date`; `test_data_survives_reopen`; `test_user_version_is_1`.
- [ ] **Step 2:** FAIL. **Step 3:** implementare. **Step 4:** PASS, mypy, lint-imports.
- [ ] **Step 5:** Stampare: `git add -A && git commit -m "feat(adapters): catalogo snapshot su SQLite"`

### Task 7: Adattatore fmsave

**Files:**
- Create: `src/fmxray/adapters/fmsave_source/source.py`, `src/fmxray/adapters/fmsave_source/mapping.py`, `tests/adapters/fake_fmsave.py`, `tests/adapters/test_fmsave_source.py`, `tests/integration/__init__.py`, `tests/integration/test_real_save.py`
- Modify: `src/fmxray/adapters/fmsave_source/__init__.py` (esporta `FmsaveSaveSource`), `tests/conftest.py` (fixture `real_save_path`)

**Interfaces:**
- Consumes: `SaveSource`, `SaveReading`, errori applicativi, `PLAYER_CATALOG`, `RELEASE_CLAUSES`, `Provenance`.
- Produces:
  - `mapping.py`: `COLUMN_MAP: Mapping[str, str]` (nostra colonna → colonna piatta di fmsave, es. `ca → ability_current`, `finishing → attributes_finishing`, `finishing_raw → raw_attributes_finishing`, `pos_gk → positions_gk`, `condition_raw → raw_condition`); `FIELD_PATHS: Mapping[str, str]` (nostra colonna → path di `field_status`, es. `ca → "ability.current"`); `to_frame(columns: Mapping[str, Sequence[object]]) -> pl.DataFrame` (seleziona e rinomina, ricava le colonne `RELEASE_CLAUSES` da `contract_clauses` prendendo il `value` del primo dict con quel `kind`, altrimenti `None`; costruisce con `PLAYER_CATALOG.polars_schema()`).
  - `source.py`: `class FmsaveSaveSource`: `__init__(self, module: ModuleType | None = None)` (default: `import fmsave`); `read(self, path: Path) -> SaveReading`. Usa `with module.open(path) as save`, `save.info` (`game`, `build`, `known_build`, `db_version`, `game_date`), `save.players().to_columns()`, `module.__version__`; raccoglie gli `UnknownBuildWarning` con `warnings.catch_warnings(record=True)` in `SaveReading.warnings`.
  - Provenienza: colonne di `RELEASE_CLAUSES` → `DERIVED`; se `info.game == "FM27"` tutte le altre → `UNCONFIRMED`; altrimenti `module.field_status(module.Player, FIELD_PATHS[col])` (`"verified"`/`"unconfirmed"`).
  - Errori: `UnsupportedGameError` → `UnsupportedSaveError`; `CorruptSaveError`, `NotAFmSaveError`, `ReaderCheckError` → `UnreadableSaveError` (messaggio originale incluso).
  - `tests/adapters/fake_fmsave.py`: `make_fake_module(game: str = "FM27", columns: dict[str, list[object]] | None = None, open_error: Exception | None = None) -> ModuleType` con le stesse eccezioni, `Player`, `field_status`, `__version__ = "0.9.3"`, `open()` context manager.

- [ ] **Step 1: test** `tests/adapters/test_fmsave_source.py`:
  - `test_maps_columns_to_catalog_schema` — `validate_frame(reading.frame, PLAYER_CATALOG)` non solleva; `reading.frame["ca"].to_list() == [150, 120]` dai dati finti.
  - `test_release_fee_from_clauses` — clausola `{"kind": "minimum_fee_release", "kind_code": 0, "parameter": None, "value": 50000000}` → `release_fee_min == 50000000`; giocatore senza clausole → `None`.
  - `test_fm27_fields_are_unconfirmed_and_release_fees_derived`.
  - `test_fm26_uses_field_status` — il fake risponde `"verified"` per `attributes.finishing` → `provenance["finishing"] is Provenance.VERIFIED`.
  - `test_unknown_build_warning_is_recorded` — il fake emette `UnknownBuildWarning("unverified build")` → presente in `reading.warnings`.
  - `test_errors_are_translated` (parametrizzato) — `UnsupportedGameError` → `UnsupportedSaveError`; `CorruptSaveError`, `NotAFmSaveError`, `ReaderCheckError` → `UnreadableSaveError`.
  - `test_every_catalog_column_is_mapped` — `set(COLUMN_MAP) | set(RELEASE_CLAUSES) == set(PLAYER_CATALOG.names())` e `set(FIELD_PATHS) == set(COLUMN_MAP)`.
- [ ] **Step 2: test di integrazione** `tests/integration/test_real_save.py`, marker `real_save`, fixture `real_save_path` (da `FMXRAY_TEST_SAVE` o primo `local/saves/**/*.fm`, altrimenti `pytest.skip`): `test_reads_real_save` — `game` in `{"FM26","FM27"}`, `frame.height > 50_000`, `ca` e `pa` tutti in 1..200, nessun `None` nei 5 hidden e negli 8 di personalità.
- [ ] **Step 3:** FAIL. **Step 4:** verificare nel pacchetto installato i nomi usati (`fmsave.__version__`, eccezioni, `SaveInfo`), poi implementare. **Step 5:** PASS (con il save presente passa anche l'integrazione), mypy, lint-imports (il contratto 4 deve restare "kept").
- [ ] **Step 6:** Stampare: `git add -A && git commit -m "feat(adapters): sorgente dati fmsave"`

### Task 8: Composition root e CLI

**Files:**
- Create: `src/fmxray/cli/commands.py`, `src/fmxray/cli/render.py`, `src/fmxray/application/show_player.py`, `tests/cli/__init__.py`, `tests/cli/test_commands.py`, `tests/application/test_show_player.py`
- Modify: `src/fmxray/bootstrap.py`, `tests/test_smoke.py`

**Interfaces:**
- Consumes: tutto quanto sopra.
- Produces:
  - `application/show_player.py`: `@dataclass(frozen=True) class PlayerMatch`: `uid: int`, `name: str`, `club_name: str | None`, `age: int`; `class ShowPlayer`: `__init__(self, store: SnapshotStore, catalog: CatalogStore)`; `find(self, career_name: str, query: str, snapshot_id: str | None = None) -> list[PlayerMatch]` (confronto senza maiuscole e accenti, `unicodedata.normalize("NFKD")`, sottostringa di `name` o `full_name`; `CareerNotFoundError` se la carriera non esiste); `details(self, career_name: str, uid: int, snapshot_id: str | None = None) -> tuple[SnapshotMeta, dict[str, object]]`.
  - `bootstrap.py`: `resolve_data_dir(cli_value: str | None, env: Mapping[str, str]) -> Path` (priorità: `--data-dir`, poi `FMXRAY_DATA_DIR`, poi `platformdirs.user_data_dir("fmxray")`); `build_app(data_dir: Path, source: SaveSource | None = None) -> App` (`App` = dataclass con `import_save`, `show_player`, `catalog`); `main(argv: Sequence[str] | None = None) -> int`.
  - `cli/commands.py`: `run(argv: Sequence[str], app_factory: Callable[[Path], App]) -> int` con sottocomandi:
    - `import SAVE --career NAME` → stampa `imported <snapshot_id> (<row_count> players, game date <date>)` oppure `already imported: <snapshot_id>`; ritorna 0.
    - `snapshots [--career NAME]` → una riga per snapshot: id, carriera, data di gioco, build, righe.
    - `show QUERY --career NAME [--uid UID] [--snapshot ID]` → un solo risultato: campi raggruppati per `FieldGroup` con la provenienza; più risultati senza `--uid`: elenco `uid  name  club  age` e ritorna 2; nessun risultato: ritorna 1.
    - `FmxrayError` → messaggio su stderr, ritorna 1. Opzione globale `--data-dir`.
  - `cli/render.py`: funzioni pure che producono le stringhe di output.

- [ ] **Step 1: test** `tests/application/test_show_player.py`: `test_find_ignores_case_and_accents` (`"unal celik"` trova `"Ünal Çelik"`); `test_find_returns_all_matches`; `test_unknown_career_raises`; `test_details_uses_latest_snapshot_by_default`.
- [ ] **Step 2: test** `tests/cli/test_commands.py` (app costruita con `build_app(tmp_path, source=FakeSaveSource(...))`): `test_import_then_already_imported` (output delle due chiamate); `test_snapshots_lists_imported`; `test_show_single_match_prints_groups_and_provenance` (contiene `HIDDEN`, `consistency`, `unconfirmed`); `test_show_ambiguous_lists_uids_and_returns_2`; `test_show_no_match_returns_1`; `test_import_path_with_spaces`; `test_error_goes_to_stderr_with_exit_1`.
- [ ] **Step 3: test** in `tests/test_smoke.py`: `test_resolve_data_dir_priority` (cli > env > platformdirs) e aggiornare il test della versione a `main(["--version"])`.
- [ ] **Step 4:** FAIL. **Step 5:** implementare. **Step 6:** PASS, mypy, ruff, lint-imports.
- [ ] **Step 7:** Stampare: `git add -A && git commit -m "feat(cli): comandi import, snapshots e show"`

### Task 9: Verifiche sul save reale, wiki e chiusura

**Files:**
- Modify: `wiki/reference/fmsave.md`, `wiki/engineering/{architecture,data-model,development,testing,change-map}.md`, `wiki/modules/README.md`, `wiki/agent/{handoff,activity,context}.md`, `wiki/project/{status,work-tracker,requirements}.md`, `wiki/index.md`, `wiki/log.md`
- Create: `wiki/modules/{domain,application,fmsave-source,parquet-store,sqlite-catalog,cli}.md`

- [ ] **Step 1 (V3):** l'utente lancia, stampato da chi esegue:
  `time uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma`
  poi chi esegue misura la dimensione del Parquet (`du -h` sulla cartella snapshot indicata da `fmxray snapshots`). Atteso: `imported …`; rilanciato: `already imported: …`.
- [ ] **Step 2 (V1, V4):** chi esegue sceglie 4 giocatori della Roma (2 titolari, 1 giovane, 1 portiere) e stampa i loro `fmxray show … --career Roma --uid …`; prepara in `wiki/reference/fmsave.md` una tabella da compilare (attributi visibili, piede, ruoli naturali, stipendio, scadenza, valore). L'utente confronta nel gioco e riporta le differenze; da stipendio e valore si ricava il fattore monetario (V4).
- [ ] **Step 3:** se V1 trova differenze con fmsave: bozza di commento per la issue #62 in `local/issue-62-draft.md` (fuori da git, niente valori protetti oltre al minimo necessario); la pubblica l'utente se vuole.
- [ ] **Step 4 (V5, V7):** quando l'utente ha risalvato `Roma.fm` dopo una sessione: copia dalla cartella cloud in `local/saves/fm27/Roma.fm` (sovrascrivendo la copia), nuovo `fmxray import`, confronto di `uid` e `unique_id` tra i due snapshot con uno script usa e getta in `local/` (giocatori comuni, nuovi, spariti); risultati in `wiki/reference/fmsave.md`. Se il secondo save non c'è ancora, segnarlo come bloccato in `wiki/project/work-tracker.md` e chiudere il resto.
- [ ] **Step 5:** wiki: pagine dei moduli (template di `wiki/SCHEMA.md`), `engineering/*` con comandi reali, handoff con SP2 come prossimo compito, log e activity.
- [ ] **Step 6:** verifica finale: `uv run ruff check`, `uv run ruff format --check`, `uv run mypy src tests`, `uv run lint-imports`, `uv run pytest` (con il save presente) → tutto pulito; skill `superpowers:verification-before-completion`.
- [ ] **Step 7:** Stampare: `git add -A && git commit -m "docs: verifiche SP1 e wiki"` e `git push`; dopo il push, l'utente controlla che la CI sia verde su Linux e Windows.
