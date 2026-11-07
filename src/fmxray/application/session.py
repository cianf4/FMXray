"""What the user is looking at: career, snapshot, filters, sort, columns.

Holds no Qt: the window calls it and draws what it returns.
"""

from collections.abc import Sequence

import polars as pl

from fmxray.application.app import App
from fmxray.application.column_views import BUILTIN_VIEWS, ColumnView
from fmxray.application.filters import EMPTY, FilterState, from_spec, to_spec
from fmxray.application.search import SearchResult
from fmxray.domain.search.parser import DEFAULT_SORT, SortKey, parse
from fmxray.domain.search.printer import to_text
from fmxray.domain.search.spec import MatchAll, Spec, Value


class BrowseSession:
    def __init__(self, app: App) -> None:
        self.app = app
        self.career: str | None = None
        self.snapshot_id: str | None = None  # None = latest
        self.filters: FilterState = EMPTY
        self.advanced: Spec | None = None  # typed in the text bar, beyond the controls
        self.sort: Sequence[SortKey] = DEFAULT_SORT
        self.view: ColumnView = BUILTIN_VIEWS[0]
        self.active_saved: str | None = None

    @property
    def spec(self) -> Spec:
        return self.advanced if self.advanced is not None else to_spec(self.filters)

    @property
    def text(self) -> str:
        return to_text(self.spec)

    def _use(self, spec: Spec) -> None:
        state = from_spec(spec)
        self.filters, self.advanced = (state, None) if state is not None else (EMPTY, spec)

    def set_filters(self, state: FilterState) -> None:
        self.filters, self.advanced, self.active_saved = state, None, None

    def set_text(self, text: str) -> None:
        """Raises `SearchError` and keeps the current filter if `text` does not parse."""
        spec = parse(text)
        self._use(spec)
        self.active_saved = None

    def open_saved(self, name: str) -> None:
        search = self.app.saved_searches.get(name)
        if search is None:
            return
        self._use(search.spec)
        self.active_saved = name

    def refresh(self) -> SearchResult | None:
        """The current result (all rows), or None when there is no career to show."""
        if self.career is None or self.app.catalog.find_career(self.career) is None:
            return None
        return self.app.search_players.execute(
            self.career, self.spec, self.sort, None, self.snapshot_id
        )

    def new_uids(self) -> frozenset[int]:
        if self.active_saved is None or self.career is None:
            return frozenset()
        return self.app.run_saved_search.execute(self.active_saved, self.career, limit=1).new_uids

    def saved_new_counts(self) -> dict[str, int]:
        if self.career is None:
            return {}
        runs = (
            self.app.run_saved_search.execute(s.name, self.career, limit=1)
            for s in self.app.saved_searches.list()
        )
        return {run.search.name: len(run.new_uids) for run in runs}

    def options(self, field: str) -> list[Value]:
        """Distinct values of a field in the current snapshot, for choice lists."""
        if self.career is None:
            return []
        frame = self.app.search_players.execute(
            self.career, MatchAll(), (), None, self.snapshot_id
        ).frame
        column = frame[field]
        if isinstance(column.dtype, pl.List):
            column = column.explode()
        return sorted(column.drop_nulls().unique().to_list())
