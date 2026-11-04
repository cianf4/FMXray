from datetime import UTC, datetime

import pytest

from fmxray.application.errors import SavedSearchNotFoundError
from fmxray.application.saved_search import RunSavedSearch, SaveSearch
from fmxray.application.search import SearchPlayers
from fmxray.domain.search.errors import QueryParseError
from fmxray.domain.snapshot import Snapshot
from tests.application.fakes import (
    InMemoryCatalogStore,
    InMemorySavedSearchStore,
    InMemorySnapshotStore,
)
from tests.factories import make_meta, make_player_frame

_NOW = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)


def _setup(*pa_per_snapshot: list[int]) -> tuple[SaveSearch, RunSavedSearch]:
    store, catalog = InMemorySnapshotStore(), InMemoryCatalogStore()
    searches = InMemorySavedSearchStore()
    career = catalog.get_or_create_career("Roma")
    for index, pa in enumerate(pa_per_snapshot):
        meta = make_meta(
            snapshot_id=f"s{index}", career_id=career, source_sha256=str(index) * 64,
            row_count=len(pa),
        )  # fmt: skip
        store.write(Snapshot(meta, make_player_frame(len(pa), pa=pa)))
        catalog.add_snapshot(meta)
    run = RunSavedSearch(searches, SearchPlayers(store, catalog), catalog)
    return SaveSearch(searches, lambda: _NOW), run


def test_save_parses_before_storing() -> None:
    save, run = _setup([185])
    with pytest.raises(QueryParseError):
        save.execute("broken", "age<")
    with pytest.raises(SavedSearchNotFoundError):
        run.execute("broken", "Roma")


def test_new_uids_between_snapshots() -> None:
    save, run = _setup([185, 150], [185, 185])
    saved = save.execute("wonderkids", "pa>180")
    assert saved.created_at == _NOW
    outcome = run.execute("wonderkids", "Roma")
    assert outcome.new_uids == {1001}
    assert outcome.result.total == 2
    assert outcome.search == saved


def test_single_snapshot_has_no_new() -> None:
    save, run = _setup([185, 150])
    save.execute("wonderkids", "pa>180")
    assert run.execute("wonderkids", "Roma").new_uids == frozenset()


def test_unknown_saved_search_raises() -> None:
    _, run = _setup([185])
    with pytest.raises(SavedSearchNotFoundError):
        run.execute("nope", "Roma")
