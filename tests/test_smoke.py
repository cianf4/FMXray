from pathlib import Path

import pytest

from fmxray.bootstrap import main, resolve_data_dir


def test_main_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert "fmxray 0.1.0" in capsys.readouterr().out


def test_resolve_data_dir_priority(tmp_path: Path) -> None:
    env = {"FMXRAY_DATA_DIR": str(tmp_path / "env")}
    assert resolve_data_dir(str(tmp_path / "cli"), env) == tmp_path / "cli"
    assert resolve_data_dir(None, env) == tmp_path / "env"
    assert resolve_data_dir(None, {}).name == "fmxray"
