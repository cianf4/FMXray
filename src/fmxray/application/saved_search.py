"""Use cases: save a search, and run it marking players new since the previous snapshot."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

from fmxray.application.errors import SavedSearchNotFoundError
from fmxray.application.ports import CatalogStore, SavedSearch, SavedSearchStore
from fmxray.application.search import SearchPlayers, SearchResult
from fmxray.application.snapshots import previous_snapshot
from fmxray.domain.search.parser import DEFAULT_SORT, SortKey, parse


class SaveSearch:
    def __init__(self, store: SavedSearchStore, clock: Callable[[], datetime]) -> None:
        self._store = store
        self._clock = clock

    def execute(self, name: str, query_text: str, replace: bool = False) -> SavedSearch:
        search = SavedSearch(name, query_text, parse(query_text), self._clock())
        self._store.save(search, replace=replace)
        return search


@dataclass(frozen=True)
class SavedSearchRun:
    search: SavedSearch
    result: SearchResult
    new_uids: frozenset[int]  # match now, did not match in the previous snapshot


class RunSavedSearch:
    def __init__(
        self, searches: SavedSearchStore, search_players: SearchPlayers, catalog: CatalogStore
    ) -> None:
        self._searches = searches
        self._search_players = search_players
        self._catalog = catalog

    def execute(
        self,
        name: str,
        career_name: str,
        sort: Sequence[SortKey] = DEFAULT_SORT,
        limit: int | None = 50,
    ) -> SavedSearchRun:
        search = self._searches.get(name)
        if search is None:
            raise SavedSearchNotFoundError(f"no saved search named {name!r}")
        result = self._search_players.execute(career_name, search.spec, sort, limit)
        meta = result.meta
        # Players are matched by `uid`; if V5 shows it is unstable across saves, switch here.
        previous = previous_snapshot(self._catalog, meta.career_id, meta.snapshot_id)
        new_uids: frozenset[int] = frozenset()
        if previous is not None:
            now = self._search_players.matching_uids(meta, search.spec)
            new_uids = now - self._search_players.matching_uids(previous, search.spec)
        return SavedSearchRun(search, result, new_uids)
