from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from fmxray.application.errors import UnreadableSaveError
from fmxray.bootstrap import build_app
from fmxray.cli.commands import App, run
from tests.application.fakes import FakeSaveSource, make_reading
from tests.factories import make_player_frame


def _app(tmp_path: Path, source: FakeSaveSource | None = None) -> App:
    return build_app(tmp_path / "data", source=source or FakeSaveSource(make_reading()))


def _run(app: App, *argv: str) -> int:
    return run(list(argv), lambda _data_dir: app)


def _save(tmp_path: Path, name: str = "Roma.fm") -> Path:
    path = tmp_path / name
    path.write_bytes(b"save")
    return path


def test_import_then_already_imported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    app, save = _app(tmp_path), _save(tmp_path)
    assert _run(app, "import", str(save), "--career", "Roma") == 0
    assert "imported" in capsys.readouterr().out
    assert _run(app, "import", str(save), "--career", "Roma") == 0
    assert "already imported:" in capsys.readouterr().out


def test_snapshots_lists_imported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    app = _app(tmp_path)
    _run(app, "import", str(_save(tmp_path)), "--career", "Roma")
    capsys.readouterr()
    assert _run(app, "snapshots", "--career", "Roma") == 0
    out = capsys.readouterr().out
    assert "2026-09-12" in out and "27.0.0+2493426" in out


def test_show_single_match_prints_groups_and_provenance(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    app = _app(tmp_path)
    _run(app, "import", str(_save(tmp_path)), "--career", "Roma")
    capsys.readouterr()
    assert _run(app, "show", "dybala", "--career", "Roma") == 0
    out = capsys.readouterr().out
    assert "HIDDEN" in out and "consistency" in out and "unconfirmed" in out


def test_show_ambiguous_lists_uids_and_returns_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    app = _app(tmp_path)
    _run(app, "import", str(_save(tmp_path)), "--career", "Roma")
    capsys.readouterr()
    assert _run(app, "show", "a", "--career", "Roma") == 2
    out = capsys.readouterr().out
    assert "1000" in out and "1001" in out


def test_show_no_match_returns_1(tmp_path: Path) -> None:
    app = _app(tmp_path)
    _run(app, "import", str(_save(tmp_path)), "--career", "Roma")
    assert _run(app, "show", "zzz", "--career", "Roma") == 1


def test_import_path_with_spaces(tmp_path: Path) -> None:
    app = _app(tmp_path)
    save = _save(tmp_path, "Roma 2 (v02).fm")
    assert _run(app, "import", str(save), "--career", "Roma") == 0


def test_error_goes_to_stderr_with_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    app = _app(tmp_path, FakeSaveSource(UnreadableSaveError("save looks damaged")))
    assert _run(app, "import", str(_save(tmp_path)), "--career", "Roma") == 1
    assert "save looks damaged" in capsys.readouterr().err


def _imported(tmp_path: Path, rows: int = 3) -> App:
    app = _app(tmp_path, FakeSaveSource(make_reading(rows)))
    _run(app, "import", str(_save(tmp_path)), "--career", "Roma")
    return app


def test_search_prints_table_and_total(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    app = _imported(tmp_path)
    capsys.readouterr()
    assert _run(app, "search", "ca>=101 age<30", "--career", "Roma", "--limit", "1") == 0
    out = capsys.readouterr().out
    assert "Mile Svilar" in out  # highest ca first
    assert "Paulo Dybala" not in out
    assert out.strip().endswith("1 of 2 players")


def test_search_unknown_field_suggests_exit_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    app = _imported(tmp_path)
    capsys.readouterr()
    assert _run(app, "search", "finishng>15", "--career", "Roma") == 1
    assert "finishing" in capsys.readouterr().err


def test_search_rejects_bad_limit(tmp_path: Path) -> None:
    app = _imported(tmp_path)
    with pytest.raises(SystemExit):
        _run(app, "search", "", "--career", "Roma", "--limit", "0")


def test_search_csv_writes_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    app = _imported(tmp_path)
    capsys.readouterr()
    out_file = tmp_path / "out.csv"
    argv = ("search", "", "--career", "Roma", "--csv", str(out_file), "--columns", "uid,name")
    assert _run(app, *argv) == 0
    assert f"wrote 3 rows to {out_file}" in capsys.readouterr().out
    assert out_file.read_text(encoding="utf-8-sig").splitlines()[0] == "uid,name"


def test_search_money_note_on_stderr(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    app = _imported(tmp_path)
    capsys.readouterr()
    assert _run(app, "search", "value>0", "--career", "Roma") == 0
    assert "internal unit" in capsys.readouterr().err
    _run(app, "search", "age>0", "--career", "Roma")
    assert capsys.readouterr().err == ""


def test_searches_save_list_run_delete(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    app = _imported(tmp_path)
    assert _run(app, "searches", "save", "young", "age<30") == 0
    assert _run(app, "searches", "save", "young", "age<20") == 1
    assert _run(app, "searches", "save", "young", "age<20", "--replace") == 0
    capsys.readouterr()
    assert _run(app, "searches", "list") == 0
    assert "young" in capsys.readouterr().out
    assert _run(app, "searches", "run", "young", "--career", "Roma") == 0
    assert "(0 new)" in capsys.readouterr().out
    assert _run(app, "searches", "delete", "young") == 0
    assert _run(app, "searches", "delete", "young") == 1


def test_searches_run_marks_new_players(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    source = FakeSaveSource(make_reading())
    app = _app(tmp_path, source)
    first = replace(make_reading(), frame=make_player_frame(3, pa=[185, 150, 150]))
    source.reading = first
    _run(app, "import", str(_save(tmp_path, "a.fm")), "--career", "Roma")
    later = replace(first, game_date=date(2026, 10, 1), frame=make_player_frame(3, pa=[185] * 3))
    source.reading = later
    path = _save(tmp_path, "b.fm")
    path.write_bytes(b"another save")
    _run(app, "import", str(path), "--career", "Roma")
    _run(app, "searches", "save", "wonderkids", "pa>180")
    capsys.readouterr()
    assert _run(app, "searches", "run", "wonderkids", "--career", "Roma") == 0
    lines = capsys.readouterr().out.splitlines()
    assert sum(line.startswith("*") for line in lines) == 2
    assert lines[-1] == "3 of 3 players (2 new)"


def test_search_csv_columns_tolerate_spaces(tmp_path: Path) -> None:
    app = _imported(tmp_path)
    out_file = tmp_path / "out.csv"
    argv = ("search", "", "--career", "Roma", "--csv", str(out_file), "--columns", "uid, name")
    assert _run(app, *argv) == 0
    assert out_file.read_text(encoding="utf-8-sig").splitlines()[0] == "uid,name"
