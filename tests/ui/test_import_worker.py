import threading
from pathlib import Path

from pytestqt.qtbot import QtBot

from fmxray.application.errors import UnreadableSaveError
from fmxray.application.import_save import ImportResult, ImportStatus
from fmxray.application.ports import SaveReading
from fmxray.bootstrap import build_app
from fmxray.ui.import_worker import ImportRunner
from tests.application.fakes import FakeSaveSource, make_reading


class _ThreadRecordingSource(FakeSaveSource):
    def read(self, path: Path) -> SaveReading:
        self.thread = threading.get_ident()
        return super().read(path)


def _save(tmp_path: Path) -> Path:
    save = tmp_path / "Roma.fm"
    save.write_bytes(b"save")
    return save


def test_import_runs_off_main_thread(qtbot: QtBot, tmp_path: Path) -> None:
    source = _ThreadRecordingSource(make_reading())
    runner = ImportRunner(build_app(tmp_path / "data", source=source).import_factory)
    with qtbot.waitSignal(runner.imported, timeout=10_000) as blocker:
        runner.start(_save(tmp_path), "Roma")
    result = blocker.args[0]
    assert isinstance(result, ImportResult) and result.status is ImportStatus.IMPORTED
    assert source.thread != threading.get_ident()


def test_failure_signal(qtbot: QtBot, tmp_path: Path) -> None:
    source = FakeSaveSource(UnreadableSaveError("save looks damaged"))
    runner = ImportRunner(build_app(tmp_path / "data", source=source).import_factory)
    with qtbot.waitSignal(runner.failed, timeout=10_000) as blocker:
        runner.start(_save(tmp_path), "Roma")
    assert "save looks damaged" in blocker.args[0]
