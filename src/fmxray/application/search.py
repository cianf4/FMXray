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
        # ponytail: one-entry cache, enough for the CLI and a GUI showing one snapshot.
        self._cached: tuple[str, pl.DataFrame] | None = None

    def _prepared(self, meta: SnapshotMeta) -> pl.DataFrame:
        if self._cached is None or self._cached[0] != meta.snapshot_id:
            frame = self._store.read(meta.career_id, meta.snapshot_id)
            self._cached = (meta.snapshot_id, prepare_frame(frame, meta.game_date))
        return self._cached[1]

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
