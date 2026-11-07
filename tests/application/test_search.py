from typing import Any

import polars as pl
import pytest

from fmxray.application.errors import CareerNotFoundError
from fmxray.application.search import SearchPlayers
from fmxray.application.snapshots import load_snapshot, previous_snapshot
from fmxray.domain.search.parser import SortKey, parse
from fmxray.domain.search.spec import MatchAll
from fmxray.domain.snapshot import Snapshot
from tests.application.fakes import InMemoryCatalogStore, InMemorySnapshotStore
from tests.factories import make_meta, make_player_frame


def _setup(
    **columns: list[Any],
) -> tuple[SearchPlayers, InMemoryCatalogStore, InMemorySnapshotStore]:
    store, catalog = InMemorySnapshotStore(), InMemoryCatalogStore()
    career = catalog.get_or_create_career("Roma")
    n = len(next(iter(columns.values())))
    meta = make_meta(career_id=career, row_count=n)
    store.write(Snapshot(meta, make_player_frame(n, **columns)))
    catalog.add_snapshot(meta)
    return SearchPlayers(store, catalog), catalog, store


def test_filters_sorts_and_limits() -> None:
    search, _, _ = _setup(age=[18, 25, 20, 19], pa=[150, 190, 170, 160])
    result = search.execute("Roma", parse("age<22"), sort=(SortKey("pa", True),), limit=2)
    assert result.frame["uid"].to_list() == [1002, 1003]
    assert result.total == 3


def test_empty_query_returns_all_sorted_by_ca() -> None:
    search, _, _ = _setup(ca=[120, 150, 90])
    result = search.execute("Roma", MatchAll())
    assert result.frame["uid"].to_list() == [1001, 1000, 1002]
    assert result.total == 3


def test_missing_values_sorted_last() -> None:
    search, _, _ = _setup(ca=[None, 150, 90])
    for descending in (True, False):
        result = search.execute("Roma", MatchAll(), sort=(SortKey("ca", descending),))
        assert result.frame["uid"].to_list()[-1] == 1000


def test_money_fields_reported() -> None:
    search, _, _ = _setup(transfer_value=[500, 5000])
    result = search.execute("Roma", parse("value>1000"), sort=(SortKey("contract_wage", True),))
    assert result.money_fields == {"transfer_value", "contract_wage"}
    assert search.execute("Roma", parse("age<30")).money_fields == frozenset()


def test_unknown_career_raises() -> None:
    search, _, _ = _setup(age=[18])
    with pytest.raises(CareerNotFoundError):
        search.execute("Lazio", MatchAll())


def test_matching_uids_and_previous_snapshot() -> None:
    search, catalog, store = _setup(pa=[185, 150])
    meta = catalog.snapshots[0]
    assert search.matching_uids(meta, parse("pa>180")) == {1000}
    assert previous_snapshot(catalog, meta.career_id, meta.snapshot_id) is None
    loaded, frame = load_snapshot(store, catalog, "Roma")
    assert loaded == meta and frame.height == 2


class _CountingStore(InMemorySnapshotStore):
    def __init__(self) -> None:
        super().__init__()
        self.reads: list[str] = []

    def read(self, career_id: int, snapshot_id: str) -> pl.DataFrame:
        self.reads.append(snapshot_id)
        return super().read(career_id, snapshot_id)


def test_two_snapshots_stay_cached() -> None:
    store, catalog = _CountingStore(), InMemoryCatalogStore()
    career = catalog.get_or_create_career("Roma")
    metas = [
        make_meta(snapshot_id=f"s{i}", career_id=career, source_sha256=str(i) * 64)
        for i in range(2)
    ]
    for meta in metas:
        store.write(Snapshot(meta, make_player_frame(3)))
        catalog.add_snapshot(meta)
    search = SearchPlayers(store, catalog)
    for _ in range(3):  # what counting "new" players for each saved search does
        for meta in metas:
            search.matching_uids(meta, MatchAll())
    assert store.reads == ["s0", "s1"]
