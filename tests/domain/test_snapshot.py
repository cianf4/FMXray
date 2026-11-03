import polars as pl
import pytest
from hypothesis import given
from hypothesis import strategies as st

from fmxray.domain.errors import SchemaMismatchError
from fmxray.domain.fields import PLAYER_CATALOG
from fmxray.domain.snapshot import Snapshot, validate_frame
from tests.factories import make_meta, make_player_frame


def test_valid_snapshot_builds() -> None:
    Snapshot(make_meta(row_count=3), make_player_frame(3))


def test_missing_column_raises() -> None:
    frame = make_player_frame(3).drop("ca")
    with pytest.raises(SchemaMismatchError, match="ca"):
        validate_frame(frame, PLAYER_CATALOG)


def test_wrong_dtype_raises() -> None:
    frame = make_player_frame(3).with_columns(pl.col("ca").cast(pl.String))
    with pytest.raises(SchemaMismatchError, match="ca"):
        validate_frame(frame, PLAYER_CATALOG)


def test_row_count_must_match() -> None:
    with pytest.raises(ValueError, match="row_count"):
        Snapshot(make_meta(row_count=5), make_player_frame(3))


@given(st.integers(min_value=0, max_value=50))
def test_factory_frames_always_valid(n: int) -> None:
    validate_frame(make_player_frame(n), PLAYER_CATALOG)
