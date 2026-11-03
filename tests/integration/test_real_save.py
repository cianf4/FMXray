from pathlib import Path

import polars as pl
import pytest

from fmxray.adapters.fmsave_source import FmsaveSaveSource
from fmxray.domain.fields import HIDDEN_ATTRIBUTES, PERSONALITY

pytestmark = pytest.mark.real_save


def test_reads_real_save(real_save_path: Path) -> None:
    reading = FmsaveSaveSource().read(real_save_path)
    frame = reading.frame
    assert reading.game in {"FM26", "FM27"}
    assert frame.height > 50_000
    for column in ("ca", "pa"):
        assert frame.filter(~pl.col(column).is_between(1, 200)).height == 0
    for column in HIDDEN_ATTRIBUTES:
        assert frame[column].null_count() == 0
    # fmsave leaves a handful of person blocks incomplete (no name, age or personality).
    complete = frame.filter(pl.col("name").is_not_null())
    assert frame.height - complete.height < 10
    for column in PERSONALITY:
        assert complete[column].null_count() == 0
