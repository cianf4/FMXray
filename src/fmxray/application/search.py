"""Use case: filter, sort and limit the players of a snapshot."""

from collections.abc import Sequence
from dataclasses import dataclass

import polars as pl

from fmxray.application.ports import CatalogStore, SnapshotStore
from fmxray.application.snapshots import find_snapshot
from fmxray.domain.fields import PLAYER_CATALOG, Unit
from fmxray.domain.search.compile import to_expr
from fmxray.domain.search.derived import is_internal_column, prepare_frame
from fmxray.domain.search.parser import DEFAULT_SORT, SortKey
from fmxray.domain.search.spec import Spec, fields_in
from fmxray.domain.snapshot import SnapshotMeta

CACHED_SNAPSHOTS = 2

_MONEY_FIELDS = frozenset(
    spec.name for spec in PLAYER_CATALOG.fields if spec.unit is Unit.MONEY_INTERNAL
)


@dataclass(frozen=True)
class SearchResult:
    meta: SnapshotMeta
    frame: pl.DataFrame
    total: int  # rows matching the filter, before the limit
    money_fields: frozenset[str]  # fields used that are in the save's internal money unit


class SearchPlayers:
    def __init__(self, store: SnapshotStore, catalog: CatalogStore) -> None:
        self._store = store
        self._catalog = catalog
        # Latest and previous snapshot: "new players" compares the two without re-reading.
        self._cached: dict[str, pl.DataFrame] = {}

    def _prepared(self, meta: SnapshotMeta) -> pl.DataFrame:
        frame = self._cached.pop(meta.snapshot_id, None)
        if frame is None:
            raw = self._store.read(meta.career_id, meta.snapshot_id)
            frame = prepare_frame(raw, meta.game_date)
        self._cached[meta.snapshot_id] = frame  # most recently used last
        while len(self._cached) > CACHED_SNAPSHOTS:
            del self._cached[next(iter(self._cached))]
        return frame

    def execute(
        self,
        career_name: str,
        spec: Spec,
        sort: Sequence[SortKey] = DEFAULT_SORT,
        limit: int | None = 50,
        snapshot_id: str | None = None,
    ) -> SearchResult:
        meta = find_snapshot(self._catalog, career_name, snapshot_id)
        frame = self._prepared(meta)
        matched = frame.filter(to_expr(spec, frame.schema))
        total = matched.height
        if sort:
            matched = matched.sort(
                [key.field for key in sort],
                descending=[key.descending for key in sort],
                nulls_last=True,
            )
        if limit is not None:
            matched = matched.head(limit)
        visible = [name for name in matched.columns if not is_internal_column(name)]
        used = fields_in(spec) | {key.field for key in sort}
        return SearchResult(meta, matched.select(visible), total, used & _MONEY_FIELDS)

    def matching_uids(self, meta: SnapshotMeta, spec: Spec) -> frozenset[int]:
        frame = self._prepared(meta)
        return frozenset(frame.filter(to_expr(spec, frame.schema))["uid"].to_list())
