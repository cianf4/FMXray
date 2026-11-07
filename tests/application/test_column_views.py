from fmxray.application.column_views import BUILTIN_VIEWS
from fmxray.domain.fields import HIDDEN_ATTRIBUTES, PERSONALITY
from fmxray.domain.search.parser import SEARCH_SCHEMA


def test_builtin_views_use_known_fields() -> None:
    names = [view.name for view in BUILTIN_VIEWS]
    assert names == [
        "General", "Technical", "Mental", "Physical", "Goalkeeping", "Hidden", "Contract",
        "Hidden by FM",
    ]  # fmt: skip
    for view in BUILTIN_VIEWS:
        assert view.columns[0] == "name"
        assert set(view.columns) <= set(SEARCH_SCHEMA.names())


def test_hidden_by_fm_view() -> None:
    view = next(v for v in BUILTIN_VIEWS if v.name == "Hidden by FM")
    assert view.columns[:5] == ("name", "age", "club_name", "ca", "pa")
    assert set(HIDDEN_ATTRIBUTES) | set(PERSONALITY) <= set(view.columns)
    assert "finishing" not in view.columns
