from datetime import UTC, datetime
from pathlib import Path

import pytest

from fmxray.application.errors import UnreadableSaveError
from fmxray.application.import_save import ImportSave, ImportStatus
from tests.application.fakes import (
    FakeSaveSource,
    InMemoryCatalogStore,
    InMemorySnapshotStore,
    make_reading,
)

NOW = datetime(2026, 11, 3, 12, 0, tzinfo=UTC)


def _save(directory: Path, name: str = "Roma.fm", content: bytes = b"save-v1") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_bytes(content)
    return path


def _use_case(
    tmp_path: Path,
    source: FakeSaveSource | None = None,
    catalog: InMemoryCatalogStore | None = None,
) -> tuple[ImportSave, FakeSaveSource, InMemorySnapshotStore, InMemoryCatalogStore]:
    source = source or FakeSaveSource(make_reading())
    store = InMemorySnapshotStore()
    catalog = catalog or InMemoryCatalogStore()
    workdir = tmp_path / "work"
    workdir.mkdir(parents=True)
    return ImportSave(source, store, catalog, workdir, lambda: NOW), source, store, catalog


def test_imports_new_save(tmp_path: Path) -> None:
    use_case, _, store, catalog = _use_case(tmp_path)
    result = use_case.execute(_save(tmp_path / "saves"), "Roma")
    assert result.status is ImportStatus.IMPORTED
    assert result.meta.row_count == 3
    assert result.meta.game == "FM27"
    assert result.meta.imported_at == NOW
    assert len(store.frames) == 1
    assert catalog.snapshots == [result.meta]


def test_same_save_twice_is_already_imported(tmp_path: Path) -> None:
    use_case, source, _, _ = _use_case(tmp_path)
    save = _save(tmp_path / "saves")
    first = use_case.execute(save, "Roma")
    second = use_case.execute(save, "Roma")
    assert second.status is ImportStatus.ALREADY_IMPORTED
    assert second.meta == first.meta
    assert len(source.paths) == 1


def test_reads_and_hashes_the_copy_not_the_original(tmp_path: Path) -> None:
    use_case, source, store, _ = _use_case(tmp_path)
    save = _save(tmp_path / "saves")
    first = use_case.execute(save, "Roma")
    assert source.paths[0] != save
    save.write_bytes(b"save-v2")
    second = use_case.execute(save, "Roma")
    assert second.status is ImportStatus.IMPORTED
    assert second.meta.source_sha256 != first.meta.source_sha256
    assert len(store.frames) == 2


def test_path_with_spaces_and_parentheses(tmp_path: Path) -> None:
    use_case, _, _, _ = _use_case(tmp_path)
    save = _save(tmp_path / "Proton dir", "Roma 2 (v02).fm")
    assert use_case.execute(save, "Roma").status is ImportStatus.IMPORTED


def test_catalog_failure_removes_written_snapshot(tmp_path: Path) -> None:
    use_case, _, store, _ = _use_case(tmp_path, catalog=InMemoryCatalogStore(fail_on_add=True))
    with pytest.raises(RuntimeError):
        use_case.execute(_save(tmp_path / "saves"), "Roma")
    assert store.frames == {}


def test_source_error_writes_nothing(tmp_path: Path) -> None:
    source = FakeSaveSource(UnreadableSaveError("damaged"))
    use_case, _, store, catalog = _use_case(tmp_path, source=source)
    with pytest.raises(UnreadableSaveError):
        use_case.execute(_save(tmp_path / "saves"), "Roma")
    assert store.frames == {}
    assert catalog.snapshots == []


def test_temporary_copy_is_removed(tmp_path: Path) -> None:
    use_case, _, _, _ = _use_case(tmp_path)
    use_case.execute(_save(tmp_path / "saves"), "Roma")
    failing, _, _, _ = _use_case(
        tmp_path / "second", source=FakeSaveSource(UnreadableSaveError("x"))
    )
    with pytest.raises(UnreadableSaveError):
        failing.execute(_save(tmp_path / "saves2"), "Roma")
    assert list((tmp_path / "work").iterdir()) == []
    assert list((tmp_path / "second" / "work").iterdir()) == []
