"""A player's six areas of play, each the mean of its visible attributes (1-20).

The groupings are this tool's own reading of FM attributes; the result is a derived
value, not something the game stores.
"""

from collections.abc import Mapping
from dataclasses import dataclass

type Areas = tuple[tuple[str, tuple[str, ...]], ...]

OUTFIELD_AREAS: Areas = (
    ("Attack", ("finishing", "off_the_ball", "long_shots", "heading")),
    ("Technique", ("first_touch", "technique", "dribbling", "passing")),
    ("Creativity", ("vision", "flair", "decisions", "crossing")),
    ("Defence", ("marking", "tackling", "positioning", "anticipation")),
    ("Physical", ("pace", "acceleration", "strength", "stamina", "agility", "balance")),
    ("Mental", ("determination", "work_rate", "teamwork", "concentration", "composure",
                "bravery")),
)  # fmt: skip

GOALKEEPER_AREAS: Areas = (
    ("Shot stopping", ("reflexes", "handling", "one_on_ones")),
    ("Aerial", ("aerial_reach", "command_of_area", "punching", "jumping_reach")),
    ("Sweeping", ("rushing_out", "anticipation", "acceleration")),
    ("Distribution", ("kicking", "throwing", "passing", "first_touch")),
    ("Physical", ("agility", "strength", "balance", "stamina")),
    ("Mental", ("concentration", "composure", "decisions", "positioning", "communication")),
)


@dataclass(frozen=True)
class Area:
    name: str
    value: float | None  # None when none of its attributes is known


def is_goalkeeper(values: Mapping[str, object]) -> bool:
    positions = values.get("natural_positions")
    return isinstance(positions, list) and "GK" in positions


def profile(values: Mapping[str, object]) -> tuple[Area, ...]:
    areas = GOALKEEPER_AREAS if is_goalkeeper(values) else OUTFIELD_AREAS
    result = []
    for name, attributes in areas:
        known = [v for a in attributes if isinstance(v := values.get(a), int)]
        result.append(Area(name, round(sum(known) / len(known), 1) if known else None))
    return tuple(result)
