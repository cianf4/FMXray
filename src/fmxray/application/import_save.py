"""Use case: import one save file into a career as a new snapshot."""

import hashlib
import shutil
import tempfile
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from fmxray.application.ports import CatalogStore, SaveSource, SnapshotStore
from fmxray.domain.snapshot import Snapshot, SnapshotMeta

SOURCE_KIND = "fmsave"


class ImportStatus(StrEnum):
    IMPORTED = "imported"
    ALREADY_IMPORTED = "already_imported"


@dataclass(frozen=True)
class ImportResult:
    status: ImportStatus
    meta: SnapshotMeta


class ImportSave:
    def __init__(
        self,
        source: SaveSource,
        store: SnapshotStore,
        catalog: CatalogStore,
        workdir: Path,
        clock: Callable[[], datetime],
    ) -> None:
        self._source = source
        self._store = store
        self._catalog = catalog
        self._workdir = workdir
        self._clock = clock

    def execute(self, save_path: Path, career_name: str) -> ImportResult:
        career_id = self._catalog.get_or_create_career(career_name)
        with tempfile.TemporaryDirectory(dir=self._workdir) as tmp:
            # Work on a copy: the game may rewrite the original while we read it.
            copy = Path(tmp) / save_path.name
            shutil.copyfile(save_path, copy)
            with copy.open("rb") as handle:
                sha256 = hashlib.file_digest(handle, "sha256").hexdigest()

            existing = self._catalog.find_by_sha256(career_id, sha256)
            if existing is not None:
                return ImportResult(ImportStatus.ALREADY_IMPORTED, existing)

            reading = self._source.read(copy)

        meta = SnapshotMeta(
            snapshot_id=str(uuid.uuid7()),
            career_id=career_id,
            game=reading.game,
            build=reading.build,
            known_build=reading.known_build,
            db_version=reading.db_version,
            game_date=reading.game_date,
            imported_at=self._clock(),
            source_sha256=sha256,
            source_kind=SOURCE_KIND,
            reader_version=reading.reader_version,
            row_count=reading.frame.height,
            provenance=reading.provenance,
            warnings=reading.warnings,
        )
        snapshot = Snapshot(meta, reading.frame)
        self._store.write(snapshot)
        try:
            self._catalog.add_snapshot(meta)
        except BaseException:
            self._store.delete(career_id, meta.snapshot_id)
            raise
        return ImportResult(ImportStatus.IMPORTED, meta)
