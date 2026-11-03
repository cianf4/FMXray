import pytest

from fmxray.bootstrap import main


def test_main_prints_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "fmxray 0.1.0" in capsys.readouterr().out
