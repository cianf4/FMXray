"""Notices new or rewritten saves in a folder (or one file) once FM has finished writing."""

import time
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal

STABLE_FOR_MS = 3000  # a save is ready when its size and mtime stay the same this long
POLL_MS = 500

type _Version = tuple[int, int]  # size, mtime in ns


def _version(path: Path) -> _Version | None:
    try:
        stat = path.stat()
    except OSError:
        return None  # removed or being replaced
    return (stat.st_size, stat.st_mtime_ns)


class SaveFolderWatcher(QObject):
    save_ready = Signal(object)  # Path

    def __init__(
        self,
        stable_for_ms: int = STABLE_FOR_MS,
        poll_ms: int = POLL_MS,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._stable_for = stable_for_ms / 1000
        self._target: Path | None = None
        self._seen: dict[Path, _Version] = {}  # last version reported (or present at start)
        self._pending: dict[Path, tuple[_Version, float]] = {}  # version, first seen at
        # ponytail: polling a stat() per save is enough for one folder and behaves the same on
        # Windows, Linux and Proton; switch to QFileSystemWatcher if folders get huge.
        self._timer = QTimer(self)
        self._timer.setInterval(poll_ms)
        self._timer.timeout.connect(self._poll)

    @property
    def target(self) -> Path | None:
        return self._target

    def watch(self, path: Path) -> None:
        """Watch a folder of saves or a single save; saves already there are not reported."""
        self._target = path
        self._pending.clear()
        self._seen = {f: v for f in self._saves() if (v := _version(f)) is not None}
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self._target = None

    def _saves(self) -> list[Path]:
        if self._target is None:
            return []
        if self._target.is_dir():
            return sorted(self._target.glob("*.fm"))
        return [self._target]

    def _poll(self) -> None:
        now = time.monotonic()
        for save in self._saves():
            version = _version(save)
            if version is None or version == self._seen.get(save):
                self._pending.pop(save, None)
                continue
            pending = self._pending.get(save)
            if pending is None or pending[0] != version:
                self._pending[save] = (version, now)
            elif now - pending[1] >= self._stable_for:
                del self._pending[save]
                self._seen[save] = version
                self.save_ready.emit(save)
