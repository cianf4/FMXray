import time
from datetime import date

import polars as pl

from fmxray.domain.search.compile import to_expr
from fmxray.domain.search.derived import prepare_frame
from fmxray.domain.search.parser import parse
from tests.factories import make_player_frame

ROWS = 126_427  # players in the user's real FM27 save
BUDGET_SECONDS = 0.2


def test_search_under_200ms() -> None:
    frame = make_player_frame(1).sample(ROWS, with_replacement=True, seed=0)
    uid = pl.int_range(ROWS, dtype=pl.Int64)
    frame = frame.with_columns(
        uid.alias("uid"),
        (uid % 25 + 15).cast(pl.Int16).alias("age"),
        (uid % 200).cast(pl.Int16).alias("pa"),
        (uid % 20 + 1).cast(pl.Int16).alias("pos_dc"),
    )
    prepared = prepare_frame(frame, date(2026, 9, 12))
    spec = parse("age<22 pa>180 pos:dc")
    timings = []
    for _ in range(3):
        start = time.perf_counter()
        prepared.filter(to_expr(spec, prepared.schema)).sort("ca", descending=True).head(50)
        timings.append(time.perf_counter() - start)
    assert min(timings) < BUDGET_SECONDS
