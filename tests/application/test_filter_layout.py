from fmxray.application.filter_layout import (
    FILTER_TABS,
    ControlKind,
    control_kind,
    slider_bounds,
)
from fmxray.domain.search.parser import SEARCH_SCHEMA


def test_every_field_is_filterable() -> None:
    shown = [f for tab in FILTER_TABS for block in tab.blocks for f in block.fields]
    assert set(shown) == set(SEARCH_SCHEMA.names())
    assert len(shown) == len(set(shown))  # each field in exactly one place


def test_tab_titles() -> None:
    assert [t.title for t in FILTER_TABS] == [
        "General", "Positions", "Attributes", "Hidden & personality", "Contract & value", "Traits",
    ]  # fmt: skip


def test_slider_bounds() -> None:
    assert slider_bounds("finishing") == (1, 20)
    assert slider_bounds("finishing_raw") == (1, 100)
    assert slider_bounds("ca") == (1, 200)
    assert slider_bounds("transfer_value") is None


def test_control_kinds() -> None:
    assert control_kind("pos_dc") is ControlKind.POSITION
    assert control_kind("free_agent") is ControlKind.FLAG
    assert control_kind("club_name") is ControlKind.TEXT
    assert control_kind("traits") is ControlKind.CHOICE
    assert control_kind("nation_id") is ControlKind.CHOICE
    assert control_kind("contract_end") is ControlKind.RANGE
