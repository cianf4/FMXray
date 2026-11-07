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
    assert model.headerData(1, horizontal, Qt.ItemDataRole.DisplayRole) == "age"


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
