"""Export of search results to CSV that Excel and LibreOffice open correctly."""

from collections.abc import Sequence
from pathlib import Path

import polars as pl

from fmxray.domain.search.aliases import resolve_field
from fmxray.domain.search.derived import is_internal_column

LIST_SEPARATOR = "|"
# Spreadsheets run cells starting with these as formulas; a leading ' shows them as text.
_FORMULA_START = r"^[=+\-@\t\r]"


def export_csv(frame: pl.DataFrame, path: Path, columns: Sequence[str] | None = None) -> int:
    """Write `frame` as UTF-8 CSV with BOM; returns the rows written."""
    visible = [name for name in frame.columns if not is_internal_column(name)]
    chosen = visible if columns is None else [resolve_field(c, visible) for c in columns]
    lists = [name for name in chosen if isinstance(frame.schema[name], pl.List)]
    out = frame.select(chosen).with_columns(
        pl.col(name).cast(pl.List(pl.String)).list.join(LIST_SEPARATOR) for name in lists
    )
    out = out.with_columns(
        pl.col(pl.String).str.replace(_FORMULA_START, "'$0")  # applies to joined lists too
    )
    out.write_csv(path, include_bom=True)
    return out.height
