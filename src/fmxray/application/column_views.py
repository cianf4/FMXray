"""Named sets of table columns: ready-made ones plus the user's own."""

from dataclasses import dataclass

from fmxray.domain.fields import HIDDEN_ATTRIBUTES, PERSONALITY, PLAYER_CATALOG, FieldGroup


@dataclass(frozen=True)
class ColumnView:
    name: str
    columns: tuple[str, ...]


def _group(group: FieldGroup) -> tuple[str, ...]:
    return tuple(s.name for s in PLAYER_CATALOG.in_group(group) if not s.name.endswith("_raw"))


_BASE = ("name", "age", "club_name", "ca", "pa")

BUILTIN_VIEWS: tuple[ColumnView, ...] = (
    ColumnView("General", (*_BASE, "natural_positions", "transfer_value", "contract_end")),
    ColumnView("Technical", _BASE + _group(FieldGroup.TECHNICAL)),
    ColumnView("Mental", _BASE + _group(FieldGroup.MENTAL)),
    ColumnView("Physical", _BASE + _group(FieldGroup.PHYSICAL)),
    ColumnView("Goalkeeping", _BASE + _group(FieldGroup.GOALKEEPING)),
    ColumnView("Hidden", ("name", *HIDDEN_ATTRIBUTES, *PERSONALITY)),
    ColumnView("Contract", (
        "name", "club_name", "contract_wage", "contract_start", "contract_end", "contract_left",
        "contract_squad_status", "transfer_value", "release_fee_min", "on_loan", "loan_end",
    )),
    # For saves where FM shows every attribute: only what the game never shows.
    ColumnView("Hidden by FM", (*_BASE, *HIDDEN_ATTRIBUTES, *PERSONALITY)),
)  # fmt: skip
