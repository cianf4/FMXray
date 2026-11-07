"""The use cases and stores an interface needs, assembled by `bootstrap`."""

from collections.abc import Callable
from dataclasses import dataclass

from fmxray.application.import_save import ImportSave
from fmxray.application.ports import (
    CareerSourceStore,
    CatalogStore,
    ColumnViewStore,
    SavedSearchStore,
)
from fmxray.application.saved_search import RunSavedSearch, SaveSearch
from fmxray.application.search import SearchPlayers
from fmxray.application.show_player import ShowPlayer


@dataclass(frozen=True)
class App:
    import_save: ImportSave
    show_player: ShowPlayer
    catalog: CatalogStore
    search_players: SearchPlayers
    save_search: SaveSearch
    run_saved_search: RunSavedSearch
    saved_searches: SavedSearchStore
    column_views: ColumnViewStore
    career_sources: CareerSourceStore
    # Builds an ImportSave with its own connections: SQLite ones cannot cross threads.
    import_factory: Callable[[], ImportSave]
