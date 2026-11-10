from typing import Any

from pytestqt.qtbot import QtBot

from fmxray.domain.fields import ATTRIBUTES, PERSONALITY, Provenance
from fmxray.domain.text import humanize
from fmxray.ui.card_model import CardModel
from fmxray.ui.theme import TOKENS
from tests.factories import make_meta, make_player_frame


def _get(model: CardModel, name: str) -> Any:
    """Reads the Qt property, exactly as QML sees it."""
    return model.property(name)


def _model(**overrides: list[Any]) -> CardModel:
    model = CardModel()
    model.set_player(make_meta(), make_player_frame(1, **overrides).to_dicts()[0])
    return model


def test_header(qtbot: QtBot) -> None:
    model = _model(ca=[131], pa=[188])
    assert (_get(model, "ca"), _get(model, "pa")) == ("131", "188")
    assert _get(model, "growth") == "room to grow 57"
    assert _get(model, "caFraction") == 0.655
    assert _get(model, "paFraction") == 0.94
    assert not _get(model, "empty")


def test_initials(qtbot: QtBot) -> None:
    assert _get(_model(name=["Ünal Çelik"]), "initials") == "ÜÇ"
    assert _get(_model(name=[None]), "initials") == ""
    assert _get(_model(name=[None]), "name") == "-"


def test_areas_from_profile(qtbot: QtBot) -> None:
    areas = _get(_model(finishing=[16]), "areas")
    assert len(areas) == 6
    assert areas[0]["name"] == "Attack"
    label = areas[0]["label"]
    assert isinstance(label, str) and "." in label


def test_empty_player_areas(qtbot: QtBot) -> None:
    model = _model(**{name: [None] for name in ATTRIBUTES})
    assert all(area["value"] == 0 and area["label"] == "-" for area in _get(model, "areas"))


def test_tabs_cover_all_fields(qtbot: QtBot) -> None:
    labels = {
        row["label"]
        for tab in _get(_model(), "tabs")
        for group in tab["groups"]
        for row in group["rows"]
    }
    for name in (*ATTRIBUTES, *PERSONALITY):
        assert humanize(name) in labels, name
    assert [tab["title"] for tab in _get(_model(), "tabs")] == [
        "Attributes",
        "Hidden",
        "Contract",
        "Positions",
    ]


def test_band_colours(qtbot: QtBot) -> None:
    rows = {
        row["label"]: row
        for tab in _get(_model(finishing=[3]), "tabs")
        for group in tab["groups"]
        for row in group["rows"]
    }
    assert rows["Finishing"]["color"] == TOKENS["band_1"]
    assert rows["Contract Squad Status"]["color"] == TOKENS["value"]  # text values stand apart too
    assert rows["Finishing"]["value"] == "3"


def test_unconfirmed_flag(qtbot: QtBot) -> None:
    model = CardModel()
    values = make_player_frame(1).to_dicts()[0]
    model.set_player(make_meta(), values)
    assert _get(model, "unconfirmed")
    verified = {name: Provenance.VERIFIED for name in make_meta().provenance}
    model.set_player(make_meta(provenance=verified), values)
    assert not _get(model, "unconfirmed")


def test_clear(qtbot: QtBot) -> None:
    model = _model()
    with qtbot.waitSignal(model.changed):
        model.clear()
    assert _get(model, "empty") and _get(model, "name") == ""


def test_positions(qtbot: QtBot) -> None:
    positions = _get(_model(), "positions")
    assert len(positions) == 15
    striker = next(p for p in positions if p["label"] == "ST")
    assert striker["row"] == 0
