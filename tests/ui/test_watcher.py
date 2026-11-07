from pathlib import Path

from pytestqt.qtbot import QtBot

from fmxray.ui.watcher import SaveFolderWatcher

_STABLE_MS, _POLL_MS = 300, 50


def _watcher(qtbot: QtBot, folder: Path) -> SaveFolderWatcher:
    watcher = SaveFolderWatcher(stable_for_ms=_STABLE_MS, poll_ms=_POLL_MS)
    watcher.watch(folder)
    return watcher


def test_emits_after_size_is_stable(qtbot: QtBot, tmp_path: Path) -> None:
    watcher = _watcher(qtbot, tmp_path)
    save = tmp_path / "Roma.fm"
    with qtbot.waitSignal(watcher.save_ready, timeout=3000) as blocker:
        save.write_bytes(b"x" * 100)
    assert blocker.args == [save]
    watcher.stop()


def test_existing_saves_are_not_emitted(qtbot: QtBot, tmp_path: Path) -> None:
    (tmp_path / "old.fm").write_bytes(b"old")
    watcher = _watcher(qtbot, tmp_path)
    with qtbot.assertNotEmitted(watcher.save_ready, wait=_STABLE_MS * 3):
        (tmp_path / "notes.txt").write_text("not a save")
    watcher.stop()


def test_no_signal_while_growing(qtbot: QtBot, tmp_path: Path) -> None:
    watcher = _watcher(qtbot, tmp_path)
    save = tmp_path / "Roma.fm"
    with qtbot.assertNotEmitted(watcher.save_ready):
        for _ in range(8):
            with save.open("ab") as handle:
                handle.write(b"x" * 1000)
            qtbot.wait(_STABLE_MS // 3)
    with qtbot.waitSignal(watcher.save_ready, timeout=3000):
        pass
    watcher.stop()


def test_same_version_not_emitted_twice(qtbot: QtBot, tmp_path: Path) -> None:
    watcher = _watcher(qtbot, tmp_path)
    with qtbot.waitSignal(watcher.save_ready, timeout=3000):
        (tmp_path / "Roma.fm").write_bytes(b"v1")
    with qtbot.assertNotEmitted(watcher.save_ready, wait=_STABLE_MS * 3):
        pass
    watcher.stop()


def test_watch_a_single_file(qtbot: QtBot, tmp_path: Path) -> None:
    save = tmp_path / "Roma.fm"
    save.write_bytes(b"v1")
    watcher = _watcher(qtbot, save)
    with qtbot.waitSignal(watcher.save_ready, timeout=3000) as blocker:
        save.write_bytes(b"version two")
    assert blocker.args == [save]
    watcher.stop()
