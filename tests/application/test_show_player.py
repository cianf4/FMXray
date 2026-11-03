import pytest

from fmxray.application.errors import CareerNotFoundError
from fmxray.application.show_player import ShowPlayer
from fmxray.domain.snapshot import Snapshot
from tests.application.fakes import InMemoryCatalogStore, InMemorySnapshotStore
from tests.factories import make_meta, make_player_frame


def _setup(*snapshot_ids: str) -> ShowPlayer:
    store, catalog = InMemorySnapshotStore(), InMemoryCatalogStore()
    career = catalog.get_or_create_career("Roma")
    for index, sid in enumerate(snapshot_ids):
        frame = make_player_frame(4, ca=[100 + index] * 4)
        frame = frame.with_columns(
            frame["name"].set(frame["uid"] == 1003, None)
        )  # incomplete record
        meta = make_meta(
            snapshot_id=sid, career_id=career, source_sha256=str(index) * 64, row_count=4
        )
        store.write(Snapshot(meta, frame))
        catalog.add_snapshot(meta)
    return ShowPlayer(store, catalog)


def test_find_ignores_case_and_accents() -> None:
    matches = _setup("s1").find("Roma", "unal celik")
    assert [m.name for m in matches] == ["Ünal Çelik"]


def test_find_returns_all_matches() -> None:
    matches = _setup("s1").find("Roma", "a")
    assert {m.uid for m in matches} == {1000, 1001, 1002}


def test_unknown_career_raises() -> None:
    with pytest.raises(CareerNotFoundError):
        _setup("s1").find("Lazio", "x")


def test_details_uses_latest_snapshot_by_default() -> None:
    meta, values = _setup("s1", "s2").details("Roma", 1001)
    assert meta.snapshot_id == "s2"
    assert values["ca"] == 101
