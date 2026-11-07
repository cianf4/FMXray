"""Runs imports on a worker thread so the window never freezes."""

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from fmxray.application.import_save import ImportSave


class _Bridge(QObject):
    done = Signal(object)
    failed = Signal(str)


class _Job(QRunnable):
    def __init__(self, factory: Callable[[], ImportSave], path: Path, career: str) -> None:
        super().__init__()
        self._factory, self._path, self._career = factory, path, career
        self.bridge = _Bridge()

    def run(self) -> None:
        try:
            # The use case is built here: its SQLite connection belongs to this thread.
            result = self._factory().execute(self._path, self._career)
        except Exception as error:
            self.bridge.failed.emit(str(error) or type(error).__name__)
        else:
            self.bridge.done.emit(result)


class ImportRunner(QObject):
    imported = Signal(object)  # ImportResult
    failed = Signal(str)

    def __init__(self, factory: Callable[[], ImportSave], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._factory = factory
        self._running: _Job | None = None
        self._queued: tuple[Path, str] | None = None  # only the newest waiting import is kept

    @property
    def busy(self) -> bool:
        return self._running is not None

    def start(self, path: Path, career: str) -> None:
        if self._running is not None:
            self._queued = (path, career)
            return
        job = _Job(self._factory, path, career)
        job.setAutoDelete(False)
        job.bridge.done.connect(self._finished_ok)
        job.bridge.failed.connect(self._finished_failed)
        self._running = job
        QThreadPool.globalInstance().start(job)

    def _finished_ok(self, result: object) -> None:
        self._next()
        self.imported.emit(result)

    def _finished_failed(self, message: str) -> None:
        self._next()
        self.failed.emit(message)

    def _next(self) -> None:
        self._running = None
        if self._queued is not None:
            path, career = self._queued
            self._queued = None
            self.start(path, career)
