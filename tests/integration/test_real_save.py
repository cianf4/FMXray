from pathlib import Path

import polars as pl
import pytest

from fmxray.adapters.fmsave_source import FmsaveSaveSource
from fmxray.bootstrap import main
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


def test_search_matches_manual_filter(real_save_path: Path, tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    out_file = tmp_path / "out.csv"
    assert (
        main(["--data-dir", str(data_dir), "import", str(real_save_path), "--career", "Roma"]) == 0
    )
    argv = ["--data-dir", str(data_dir), "search", "age<22 pa>180", "--career", "Roma"]
    assert main([*argv, "--limit", "100000", "--csv", str(out_file)]) == 0
    snapshot = next((data_dir / "snapshots").rglob("*.parquet"))
    expected = pl.read_parquet(snapshot).filter((pl.col("age") < 22) & (pl.col("pa") > 180))
    assert set(pl.read_csv(out_file)["uid"].to_list()) == set(expected["uid"].to_list())
