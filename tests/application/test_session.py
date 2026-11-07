from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from fmxray.application.app import App
from fmxray.application.filters import FilterState, Range
from fmxray.application.session import BrowseSession
from fmxray.bootstrap import build_app
from fmxray.domain.search.errors import SearchError
from fmxray.domain.search.parser import parse
from tests.application.fakes import FakeSaveSource, make_reading
from tests.factories import make_player_frame


def _import(
    app: App, source: FakeSaveSource, tmp_path: Path, name: str, **columns: list[object]
) -> None:
    reading = make_reading()
    source.reading = replace(
        reading,
        frame=make_player_frame(3, **columns),
        game_date=date(2026, 9, 12) if name == "a" else date(2026, 10, 1),
    )
    save = tmp_path / f"{name}.fm"
    save.write_bytes(name.encode())
    app.import_save.execute(save, "Roma")


def _session(tmp_path: Path, *snapshots: dict[str, list[object]]) -> BrowseSession:
    source = FakeSaveSource(make_reading())
    app = build_app(tmp_path / "data", source=source)
    for name, columns in zip("abc", snapshots or ({},), strict=False):
        _import(app, source, tmp_path, name, **columns)
    session = BrowseSession(app)
    session.career = "Roma"
    return session


def test_controls_and_text_stay_in_sync(tmp_path: Path) -> None:
    session = _session(tmp_path)
    session.set_filters(FilterState(ranges={"age": Range(None, 21)}))
    assert session.text == "age<=21"
    session.set_text("pa>=150 pos:dc")
    assert session.filters == FilterState(ranges={"pa": Range(150, None)}, positions={"dc": 15})
    assert session.advanced is None


def test_advanced_text_locks_controls(tmp_path: Path) -> None:
    session = _session(tmp_path)
    session.set_text("age<22 or ca>150")
    assert session.advanced == parse("age<22 or ca>150")
    assert session.spec == parse("age<22 or ca>150")
    session.set_filters(FilterState())
    assert session.advanced is None


def test_bad_text_keeps_previous_state(tmp_path: Path) -> None:
    session = _session(tmp_path)
    session.set_text("age<30")
    for bad in ("age<", "finishng>15"):
        with pytest.raises(SearchError):
            session.set_text(bad)
        assert session.spec == parse("age<=29")


def test_refresh_returns_all_rows(tmp_path: Path) -> None:
    session = _session(tmp_path)
    result = session.refresh()
    assert result is not None and result.total == 3 and result.frame.height == 3


def test_no_career_gives_no_result(tmp_path: Path) -> None:
    session = BrowseSession(build_app(tmp_path / "data", source=FakeSaveSource(make_reading())))
    assert session.refresh() is None


def test_new_uids_for_saved_search(tmp_path: Path) -> None:
    session = _session(tmp_path, {"pa": [185, 150, 150]}, {"pa": [185, 185, 150]})
    session.app.save_search.execute("wonderkids", "pa>180")
    assert session.new_uids() == frozenset()
    session.open_saved("wonderkids")
    assert session.active_saved == "wonderkids"
    assert session.new_uids() == {1001}
    assert session.saved_new_counts() == {"wonderkids": 1}
    session.set_filters(FilterState())
    assert session.active_saved is None


def test_options_from_snapshot(tmp_path: Path) -> None:
    session = _session(tmp_path, {"traits": [["b", "a"], [], ["a"]]})
    assert session.options("traits") == ["a", "b"]
