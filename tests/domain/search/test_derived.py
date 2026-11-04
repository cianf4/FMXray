from datetime import date

import polars as pl

from fmxray.domain.search.derived import is_internal_column, prepare_frame
from tests.factories import make_player_frame

GAME_DATE = date(2026, 9, 12)


def test_contract_left_months() -> None:
    frame = make_player_frame(
        4, contract_end=[date(2027, 6, 30), date(2026, 9, 30), date(2026, 9, 11), None]
    )
    assert prepare_frame(frame, GAME_DATE)["contract_left"].to_list() == [9, 0, -1, None]


def test_contract_left_without_game_date_is_null() -> None:
    assert prepare_frame(make_player_frame(2), None)["contract_left"].null_count() == 2


def test_free_agent() -> None:
    frame = make_player_frame(2, club_uid=[None, 1100])
    assert prepare_frame(frame, GAME_DATE)["free_agent"].to_list() == [True, False]


def test_folded_text_columns_added() -> None:
    prepared = prepare_frame(make_player_frame(1), GAME_DATE)
    assert prepared["name__folded"].to_list() == ["unal celik"]
    assert prepared.schema["contract_left"] == pl.Int32()
    assert is_internal_column("name__folded")
    assert not is_internal_column("name")
