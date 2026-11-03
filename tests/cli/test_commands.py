from pathlib import Path

import pytest

from fmxray.application.errors import UnreadableSaveError
from fmxray.bootstrap import build_app
from fmxray.cli.commands import App, run
from tests.application.fakes import FakeSaveSource, make_reading


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
