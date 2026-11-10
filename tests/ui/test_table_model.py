import time

import polars as pl
from PySide6.QtCore import Qt
from pytestqt.modeltest import ModelTester
from pytestqt.qtbot import QtBot

from fmxray.application.column_views import BUILTIN_VIEWS
from fmxray.domain.fields import Provenance
from fmxray.ui.table_model import PlayerTableModel
from tests.factories import make_player_frame

_COLUMNS = ("name", "age", "ca", "natural_positions")
_ROWS = 126_427


def _model(
    frame: pl.DataFrame | None = None, new_uids: frozenset[int] = frozenset()
) -> PlayerTableModel:
    model = PlayerTableModel()
    provenance = {"ca": Provenance.UNCONFIRMED, "age": Provenance.VERIFIED}
    shown = frame if frame is not None else make_player_frame(3)
    model.set_result(shown, _COLUMNS, provenance, new_uids)
    return model


def _display(model: PlayerTableModel, row: int, column: int) -> object:
    return model.data(model.index(row, column), Qt.ItemDataRole.DisplayRole)


def test_model_passes_qt_checks(qtmodeltester: ModelTester) -> None:
    qtmodeltester.check(_model())


def test_missing_values_show_dash() -> None:
    frame = make_player_frame(2, name=[None, "Mile Svilar"], natural_positions=[["DC", "DM"], []])
    model = _model(frame)
    assert _display(model, 0, 0) == "-"
    assert _display(model, 0, 3) == "DC, DM"
    assert model.uid_at(1) == 1001
    assert model.row_of(1001) == 1
    assert model.row_of(9) is None


def test_unconfirmed_header_tooltip() -> None:
    model = _model()
    horizontal = Qt.Orientation.Horizontal
    tooltip = model.headerData(2, horizontal, Qt.ItemDataRole.ToolTipRole)
    assert isinstance(tooltip, str) and "unconfirmed" in tooltip
    assert str(model.headerData(2, horizontal, Qt.ItemDataRole.DisplayRole)).endswith("ⓘ")


def test_no_mark_when_verified() -> None:
    model = _model()
    horizontal = Qt.Orientation.Horizontal
    assert model.headerData(1, horizontal, Qt.ItemDataRole.ToolTipRole) is None
    assert model.headerData(1, horizontal, Qt.ItemDataRole.DisplayRole) == "Age"


def test_new_mark() -> None:
    model = _model(new_uids=frozenset({1001}))
    assert str(_display(model, 1, 0)).startswith("● ")
    assert not str(_display(model, 0, 0)).startswith("● ")


def test_sort_emits_request(qtbot: QtBot) -> None:
    model = _model()
    with qtbot.waitSignal(model.sort_requested) as blocker:
        model.sort(1, Qt.SortOrder.DescendingOrder)
    assert blocker.args == ["age", True]


def test_set_result_fast() -> None:
    frame = make_player_frame(1).sample(_ROWS, with_replacement=True, seed=0)
    general = next(v for v in BUILTIN_VIEWS if v.name == "General")
    model = PlayerTableModel()
    timings = []
    for _ in range(3):
        start = time.perf_counter()
        model.set_result(frame, general.columns, {})
        timings.append(time.perf_counter() - start)
    assert model.rowCount() == _ROWS
    assert min(timings) < 0.5


def test_numbers_right_aligned_in_number_font() -> None:
    from PySide6.QtGui import QFont

    from fmxray.ui.theme import TOKENS

    model = _model()
    alignment = model.data(model.index(0, 1), Qt.ItemDataRole.TextAlignmentRole)  # age
    assert alignment == Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    font = model.data(model.index(0, 1), Qt.ItemDataRole.FontRole)
    assert isinstance(font, QFont) and font.family() == TOKENS["font_numbers"]
    assert model.data(model.index(0, 0), Qt.ItemDataRole.TextAlignmentRole) is None  # name


def test_no_marks_when_every_column_is_unconfirmed() -> None:
    model = PlayerTableModel()
    every = {c: Provenance.UNCONFIRMED for c in _COLUMNS}
    model.set_result(make_player_frame(3), _COLUMNS, every)
    horizontal = Qt.Orientation.Horizontal
    assert model.headerData(2, horizontal, Qt.ItemDataRole.DisplayRole) == "CA"
    assert model.all_unconfirmed()


def test_readable_headers_and_big_numbers() -> None:
    from fmxray.ui.table_model import column_title, format_value

    assert [column_title(c) for c in ("name", "ca", "natural_positions", "transfer_value")] == [
        "Name", "CA", "Positions", "Value",
    ]  # fmt: skip
    assert column_title("long_shots") == "Long Shots"
    assert format_value(12_950_000) == "12,950,000"
    assert format_value(1999) == "1999"


def test_format_money() -> None:
    from fmxray.ui.table_model import format_money

    cases = {None: "-", 999: "999", 950_000: "950K", 12_500: "12.5K", 4_200_000: "4.2M",
             999_999: "1M", -2_500: "-2.5K"}  # fmt: skip
    assert {value: format_money(value) for value in cases} == cases


def test_money_tooltip_is_full(qtbot: QtBot) -> None:
    model = PlayerTableModel()
    frame = make_player_frame(1, transfer_value=[187_061_600])
    model.set_result(frame, ("name", "transfer_value"), {})
    index = model.index(0, 1)
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "187.1M"
    assert model.data(index, Qt.ItemDataRole.ToolTipRole) == "187,061,600"


def test_enum_values_are_readable(qtbot: QtBot) -> None:
    model = PlayerTableModel()
    frame = make_player_frame(
        1, contract_squad_status=["regular_starter"], traits=[["dives_into_tackles"]]
    )
    model.set_result(frame, ("name", "contract_squad_status", "traits"), {})
    assert _display(model, 0, 1) == "Regular Starter"
    assert _display(model, 0, 2) == "Dives into Tackles"
