from dataclasses import replace
from datetime import date
from pathlib import Path

import polars as pl
import pytest
from PySide6.QtCore import QItemSelectionModel, QSettings, Qt
from PySide6.QtGui import QKeySequence
from pytestqt.qtbot import QtBot

from fmxray.application.app import App
from fmxray.application.errors import UnreadableSaveError
from fmxray.application.filters import Range
from fmxray.application.session import BrowseSession
from fmxray.bootstrap import build_app
from fmxray.domain.search.parser import parse
from fmxray.ui.main_window import MainWindow
from fmxray.ui.settings import UiSettings
from fmxray.ui.theme import Density, row_height
from tests.application.fakes import FakeSaveSource, make_reading
from tests.factories import make_player_frame


class _Env:
    def __init__(self, tmp_path: Path) -> None:
        self.tmp_path = tmp_path
        self.source = FakeSaveSource(make_reading())
        self.app: App = build_app(tmp_path / "data", source=self.source)
        self.saves = 0

    def import_save(self, frame: pl.DataFrame, day: int = 12) -> None:
        self.saves += 1
        self.source.reading = replace(make_reading(), frame=frame, game_date=date(2026, 9, day))
        save = self.tmp_path / f"save{self.saves}.fm"
        save.write_bytes(str(self.saves).encode())
        self.app.import_save.execute(save, "Roma")


@pytest.fixture
def env(tmp_path: Path) -> _Env:
    return _Env(tmp_path)


def _settings(env: _Env) -> UiSettings:
    return UiSettings(QSettings(str(env.tmp_path / "ui.ini"), QSettings.Format.IniFormat))


def _window(qtbot: QtBot, env: _Env) -> MainWindow:
    window = MainWindow(env.app, BrowseSession(env.app), _settings(env))
    qtbot.addWidget(window)
    window.show()
    return window


def _select(window: MainWindow, row: int) -> None:
    index = window.model.index(row, 0)
    flags = (
        QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
    )
    window.table.selectionModel().select(index, flags)
    window.table.setCurrentIndex(index)


def test_empty_state_offers_import(qtbot: QtBot, env: _Env) -> None:
    window = _window(qtbot, env)
    assert window.empty_label.isVisibleTo(window)
    assert window.model.rowCount() == 0


def test_quick_filter_updates_table(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    assert window.model.rowCount() == 3
    window.quick.range_control("ca").set_range(Range(101, None), emit=True)
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    assert window.text_bar.text() == "ca>=101"


def test_age_pa_from_controls_match_cli(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(4, age=[18, 21, 25, 19], pa=[185, 190, 190, 170]))
    window = _window(qtbot, env)
    window.quick.range_control("age").set_range(Range(None, 21), emit=True)
    window.quick.range_control("pa").set_range(Range(181, None), emit=True)
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    shown = {window.model.uid_at(r) for r in range(window.model.rowCount())}
    expected = env.app.search_players.execute("Roma", parse("age<22 pa>180"), limit=None)
    assert shown == set(expected.frame["uid"].to_list())


def test_text_bar_error_shown_table_unchanged(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.show_text_bar(True)
    qtbot.keyClicks(window.text_bar, "finishng>15")
    assert window.text_error.isVisibleTo(window)
    assert "finishing" in window.text_error.text()
    qtbot.wait(300)
    assert window.model.rowCount() == 3
    window.text_bar.clear()
    qtbot.keyClicks(window.text_bar, "ca>101")
    qtbot.waitUntil(lambda: window.model.rowCount() == 1)
    assert not window.text_error.isVisibleTo(window)


def test_advanced_text_locks_controls(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.show_text_bar(True)
    qtbot.keyClicks(window.text_bar, "age<2 or ca>101")
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    assert not window.filters_dialog.tabs.isEnabled()


def test_selection_shows_card(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    _select(window, 0)
    assert window.card.model.property("name") == "Mile Svilar"  # highest ca first


def test_reload_keeps_filters_sort_selection(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.quick.range_control("ca").set_range(Range(101, None), emit=True)
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    window.model.sort(window.model.columns.index("age"), Qt.SortOrder.AscendingOrder)
    _select(window, 1)
    selected = window.selected_uid()
    env.import_save(make_player_frame(3, ca=[150, 150, 150]), day=20)
    window.reload_snapshot()
    assert window.model.rowCount() == 3
    assert window.text_bar.text() == "ca>=101"
    assert window.session.sort[0].field == "age"
    assert window.selected_uid() == selected


def test_reload_clears_card_when_player_gone(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    _select(window, 0)
    env.import_save(make_player_frame(1, uid=[5000]), day=20)
    window.reload_snapshot()
    assert window.selected_uid() is None
    assert window.card.model.property("name") == ""


def test_export_csv_all_filtered_rows(
    qtbot: QtBot, env: _Env, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.import_save(make_player_frame(80))
    window = _window(qtbot, env)
    out = tmp_path / "out.csv"
    monkeypatch.setattr(
        "fmxray.ui.main_window.QFileDialog.getSaveFileName", lambda *a, **k: (str(out), "")
    )
    window.export_csv()
    exported = pl.read_csv(out)
    assert exported.height == 80
    assert exported.columns == list(window.session.view.columns)


def test_saved_search_shows_new_count(
    qtbot: QtBot, env: _Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env.import_save(make_player_frame(3, pa=[185, 150, 150]))
    env.import_save(make_player_frame(3, pa=[185, 185, 150]), day=20)
    window = _window(qtbot, env)
    window.show_text_bar(True)
    qtbot.keyClicks(window.text_bar, "pa>180")
    monkeypatch.setattr(
        "fmxray.ui.main_window.QInputDialog.getText", lambda *a, **k: ("wonderkids", True)
    )
    window.save_search()
    item = window.sidebar.list.item(0)
    assert item is not None and item.text() == "wonderkids  +1"
    assert window.sidebar.badge_text() == "+1"
    window.sidebar.set_open(True, animate=False)
    window.sidebar.list.setCurrentRow(0)
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    assert window.session.active_saved == "wonderkids"


def test_new_save_refreshes_table(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.quick.range_control("ca").set_range(Range(101, None), emit=True)
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    env.source.reading = replace(
        make_reading(), frame=make_player_frame(3, ca=[150] * 3), game_date=date(2026, 10, 1)
    )
    save = env.tmp_path / "new.fm"
    save.write_bytes(b"new save")
    window.watcher.save_ready.emit(save)
    qtbot.waitUntil(lambda: window.model.rowCount() == 3, timeout=10_000)
    assert window.text_bar.text() == "ca>=101"


def test_failed_import_keeps_previous_snapshot(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    env.source.reading = UnreadableSaveError("save looks damaged")
    save = env.tmp_path / "broken.fm"
    save.write_bytes(b"broken")
    window.watcher.save_ready.emit(save)
    qtbot.waitUntil(lambda: "Import failed" in window.statusBar().currentMessage(), timeout=10_000)
    assert "save looks damaged" in window.statusBar().currentMessage()
    assert window.model.rowCount() == 3


def test_follow_folder_imports_newest_and_watches(qtbot: QtBot, env: _Env) -> None:
    window = _window(qtbot, env)
    folder = env.tmp_path / "games"
    folder.mkdir()
    (folder / "Roma.fm").write_bytes(b"first save")
    window.follow_folder(folder, "Roma")
    qtbot.waitUntil(lambda: window.model.rowCount() == 3, timeout=10_000)
    assert not window.empty_label.isVisibleTo(window)
    assert window.watcher.target == folder
    career_id = env.app.catalog.find_career("Roma")
    assert career_id is not None and env.app.career_sources.get(career_id) == folder


def test_text_bar_hidden_by_default_and_toggles(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    assert not window.text_row.isVisibleTo(window)
    # Offscreen windows never become active, so the shortcut is fired directly.
    assert window.text_shortcut.key() == QKeySequence("Ctrl+K")
    window.text_shortcut.activated.emit()
    assert window.text_row.isVisibleTo(window)
    assert window.focusWidget() is window.text_bar
    window.text_shortcut.activated.emit()
    assert not window.text_row.isVisibleTo(window)


def test_rows_above_table(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    above = [w for w in window.top_rows() if w.isVisibleTo(window)]
    assert above == [window.career_bar, window.filter_bar]


def test_chip_removal_updates_controls(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.quick.range_control("pa").set_range(Range(101, None), emit=True)
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    assert window.chips.labels() == ["pa ≥ 101"]
    window.filters_dialog.show()
    window.chips.remove_button("pa").click()
    qtbot.waitUntil(lambda: window.model.rowCount() == 3)
    assert window.chips.labels() == []
    assert window.quick.range_control("pa").range() == Range()
    assert window.filters_dialog.state().ranges == {}


def test_advanced_filter_chip(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.show_text_bar(True)
    qtbot.keyClicks(window.text_bar, "age<2 or ca>101")
    qtbot.waitUntil(lambda: window.model.rowCount() == 2)
    window.show_text_bar(False)
    assert window.chips.labels() == ["Advanced filter"]
    window.chips.remove_button("advanced").click()
    qtbot.waitUntil(lambda: window.model.rowCount() == 3)
    assert window.session.advanced is None
    assert window.filters_dialog.tabs.isEnabled()


def test_view_tabs_change_columns(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.view_tabs.setCurrentIndex(1)  # Technical
    assert window.model.columns == window.view_tabs.current_view().columns
    assert "finishing" in window.model.columns


def test_density_toggle_persists(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.density_button.click()
    assert window.table.verticalHeader().defaultSectionSize() == row_height(Density.COMPACT)
    again = _window(qtbot, env)
    assert again.density_button.isChecked()
    assert again.table.verticalHeader().defaultSectionSize() == row_height(Density.COMPACT)


def test_table_fills_width(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.resize(1600, 900)
    window.show()
    qtbot.waitExposed(window)
    header = window.table.horizontalHeader()
    used = sum(header.sectionSize(i) for i in range(header.count()))
    assert abs(used - window.table.viewport().width()) <= 2


def test_panels(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    assert window.table_panel.objectName() == window.card_panel.objectName() == "panel"
    assert window.table_panel.isAncestorOf(window.table)
    assert window.card_panel.isAncestorOf(window.card)


def test_open_sidebar_does_not_move_table(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.resize(1400, 800)
    window.show()
    qtbot.waitExposed(window)
    before = window.table.geometry()
    window.sidebar.set_open(True, animate=False)
    assert window.table.geometry() == before
    assert not window.sidebar.panel.isHidden()


def test_extra_width_is_shared(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3))
    window = _window(qtbot, env)
    window.resize(1600, 900)
    window.show()
    qtbot.waitExposed(window)
    name = window.model.columns.index("name")
    share = window.table.horizontalHeader().sectionSize(name) / window.table.viewport().width()
    assert share < 0.4  # the spare width is spread, not all given to one column


def test_columns_keep_width_when_filtering(qtbot: QtBot, env: _Env) -> None:
    env.import_save(make_player_frame(3, name=["Zed", "Bartholomew Longname-Fether", "Quill"]))
    window = _window(qtbot, env)
    window.resize(1600, 900)
    window.show()
    qtbot.waitExposed(window)
    header = window.table.horizontalHeader()
    before = [header.sectionSize(i) for i in range(header.count())]
    window.quick.name_edit.setText("Zed")
    qtbot.waitUntil(lambda: window.model.rowCount() == 1)
    assert [header.sectionSize(i) for i in range(header.count())] == before
