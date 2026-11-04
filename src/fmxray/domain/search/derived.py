"""Columns computed at search time: derived fields and accent-folded text."""

from collections.abc import Mapping
from datetime import date

import polars as pl

from fmxray.domain.search.compile import FOLDED_SUFFIX
from fmxray.domain.text import fold

TEXT_FIELDS: tuple[str, ...] = (
    "name", "full_name", "club_name", "loan_parent_club_name",
    "contract_squad_status", "transfer_value_state",
)  # fmt: skip

DERIVED_FIELDS: Mapping[str, pl.DataType] = {
    "contract_left": pl.Int32(),
    "free_agent": pl.Boolean(),
}


def is_internal_column(name: str) -> bool:
    return name.endswith(FOLDED_SUFFIX)


def _contract_left(game_date: date | None) -> pl.Expr:
    if game_date is None:
        return pl.lit(None, dtype=pl.Int32())
    end = pl.col("contract_end")
    months = (end.dt.year().cast(pl.Int32) - game_date.year) * 12 + (
        end.dt.month().cast(pl.Int32) - game_date.month
    )
    return months - (end.dt.day() < game_date.day).cast(pl.Int32)


def prepare_frame(frame: pl.DataFrame, game_date: date | None) -> pl.DataFrame:
    folded = [
        pl.Series(f + FOLDED_SUFFIX, [None if v is None else fold(v) for v in frame[f]], pl.String)
        for f in TEXT_FIELDS
    ]
    return frame.with_columns(
        _contract_left(game_date).cast(pl.Int32).alias("contract_left"),
        pl.col("club_uid").is_null().alias("free_agent"),
        *folded,
    )
