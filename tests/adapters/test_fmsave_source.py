from pathlib import Path

import pytest

from fmxray.adapters.fmsave_source import FmsaveSaveSource
from fmxray.adapters.fmsave_source.mapping import COLUMN_MAP, FIELD_PATHS
from fmxray.application.errors import UnreadableSaveError, UnsupportedSaveError
from fmxray.domain.fields import PLAYER_CATALOG, RELEASE_CLAUSES, Provenance
from fmxray.domain.snapshot import validate_frame
from tests.adapters import fake_fmsave
from tests.adapters.fake_fmsave import flat_columns, make_fake_module

SAVE = Path("Roma.fm")


def test_maps_columns_to_catalog_schema() -> None:
    reading = FmsaveSaveSource(make_fake_module()).read(SAVE)
    validate_frame(reading.frame, PLAYER_CATALOG)
    assert reading.frame["ca"].to_list() == [150, 120]
    assert reading.game == "FM27"
    assert reading.reader_version == "0.9.3"


def test_release_fee_from_clauses() -> None:
    columns = flat_columns()
    columns["contract_clauses"] = [
        ({"kind": "minimum_fee_release", "kind_code": 0, "parameter": None, "value": 50000000},),
        (),
    ]
    reading = FmsaveSaveSource(make_fake_module(columns=columns)).read(SAVE)
    assert reading.frame["release_fee_min"].to_list() == [50000000, None]


def test_fm27_fields_are_unconfirmed_and_release_fees_derived() -> None:
    reading = FmsaveSaveSource(make_fake_module(statuses={"ability.current": "verified"})).read(
        SAVE
    )
    for name in RELEASE_CLAUSES:
        assert reading.provenance[name] is Provenance.DERIVED
    assert reading.provenance["ca"] is Provenance.UNCONFIRMED
    assert set(reading.provenance) == set(PLAYER_CATALOG.names())


def test_fm26_uses_field_status() -> None:
    module = make_fake_module(game="FM26", statuses={"attributes.finishing": "verified"})
    reading = FmsaveSaveSource(module).read(SAVE)
    assert reading.provenance["finishing"] is Provenance.VERIFIED
    assert reading.provenance["ca"] is Provenance.UNCONFIRMED


def test_unknown_build_warning_is_recorded() -> None:
    reading = FmsaveSaveSource(make_fake_module(warn="unverified build")).read(SAVE)
    assert any("unverified build" in w for w in reading.warnings)


@pytest.mark.parametrize(
    ("raised", "expected"),
    [
        (fake_fmsave.UnsupportedGameError("fm25"), UnsupportedSaveError),
        (fake_fmsave.CorruptSaveError("damaged"), UnreadableSaveError),
        (fake_fmsave.NotAFmSaveError("not a save"), UnreadableSaveError),
        (fake_fmsave.ReaderCheckError("layout"), UnreadableSaveError),
        (fake_fmsave.FmsaveError("save changed while reading"), UnreadableSaveError),
    ],
)
def test_errors_are_translated(raised: Exception, expected: type[Exception]) -> None:
    with pytest.raises(expected, match=str(raised)):
        FmsaveSaveSource(make_fake_module(open_error=raised)).read(SAVE)


def test_every_catalog_column_is_mapped() -> None:
    assert set(COLUMN_MAP) | set(RELEASE_CLAUSES) == set(PLAYER_CATALOG.names())
    assert set(FIELD_PATHS) == set(COLUMN_MAP)


def test_field_paths_are_registered_in_fmsave() -> None:
    import fmsave

    for path in FIELD_PATHS.values():
        assert fmsave.field_status(fmsave.Player, path) in {"verified", "unconfirmed"}
