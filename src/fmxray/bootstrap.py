"""Composition root: builds adapters and use cases, then hands over to the CLI."""

import os
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import platformdirs

from fmxray.adapters.fmsave_source import FmsaveSaveSource
from fmxray.adapters.parquet_store import ParquetSnapshotStore
from fmxray.adapters.sqlite_catalog import SqliteCatalogStore, SqliteSavedSearchStore
from fmxray.application.import_save import ImportSave
from fmxray.application.ports import SaveSource
from fmxray.application.saved_search import RunSavedSearch, SaveSearch
from fmxray.application.search import SearchPlayers
from fmxray.application.show_player import ShowPlayer
from fmxray.cli.commands import App, run

DATA_DIR_ENV = "FMXRAY_DATA_DIR"


def resolve_data_dir(cli_value: str | None, env: Mapping[str, str]) -> Path:
    if cli_value:
        return Path(cli_value)
    if env.get(DATA_DIR_ENV):
        return Path(env[DATA_DIR_ENV])
    return Path(platformdirs.user_data_dir("fmxray"))


def _now() -> datetime:
    return datetime.now(UTC)


def build_app(data_dir: Path, source: SaveSource | None = None) -> App:
    workdir = data_dir / "tmp"
    workdir.mkdir(parents=True, exist_ok=True)
    store = ParquetSnapshotStore(data_dir / "snapshots")
    catalog = SqliteCatalogStore(data_dir / "catalog.db")
    saved_searches = SqliteSavedSearchStore(data_dir / "catalog.db")
    search_players = SearchPlayers(store, catalog)
    return App(
        import_save=ImportSave(source or FmsaveSaveSource(), store, catalog, workdir, _now),
        show_player=ShowPlayer(store, catalog),
        catalog=catalog,
        search_players=search_players,
        save_search=SaveSearch(saved_searches, _now),
        run_saved_search=RunSavedSearch(saved_searches, search_players, catalog),
        saved_searches=saved_searches,
    )


def main(argv: Sequence[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    return run(arguments, lambda data_dir: build_app(resolve_data_dir(data_dir, os.environ)))
