from datetime import date
from pathlib import Path

import polars as pl
import pytest

from fmxray.application.export import export_csv
from fmxray.domain.search.derived import prepare_frame
from fmxray.domain.search.errors import UnknownFieldError
from tests.factories import make_player_frame


def _frame() -> pl.DataFrame:
    frame = make_player_frame(2, natural_positions=[["AMC", "STC"], []])
    return prepare_frame(frame, date(2026, 9, 12))


def test_roundtrip_with_accents_and_lists(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    assert export_csv(_frame(), path) == 2
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    back = pl.read_csv(path)
    assert back["name"][0] == "Ünal Çelik"
    assert back["natural_positions"][0] == "AMC|STC"
    assert "contract_left" in back.columns


def test_internal_columns_not_exported(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    export_csv(_frame(), path)
    assert not [c for c in pl.read_csv(path).columns if c.endswith("__folded")]


def test_columns_selects_and_orders(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    export_csv(_frame(), path, columns=["pa", "name"])
    assert path.read_text(encoding="utf-8-sig").splitlines()[0] == "pa,name"


def test_unknown_column_raises(tmp_path: Path) -> None:
    with pytest.raises(UnknownFieldError) as error:
        export_csv(_frame(), tmp_path / "out.csv", columns=["nmae"])
    assert "name" in error.value.suggestions
