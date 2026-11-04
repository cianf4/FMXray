"""Short names for fields, in the spirit of the in-game attribute abbreviations."""

import difflib
from collections.abc import Collection, Mapping

from fmxray.domain.search.errors import UnknownFieldError

ALIASES: Mapping[str, str] = {
    # Fixed by the spec.
    "acc": "acceleration", "pac": "pace", "det": "determination", "inj": "injury_proneness",
    "cons": "consistency", "imp": "important_matches", "prof": "professionalism",
    "amb": "ambition", "value": "transfer_value", "wage": "contract_wage",
    "club": "club_name",
    # Technical.
    "cor": "corners", "cro": "crossing", "dri": "dribbling", "fin": "finishing",
    "fir": "first_touch", "fre": "free_kick_taking", "hea": "heading", "lon": "long_shots",
    "lth": "long_throws", "mar": "marking", "pas": "passing", "pen": "penalty_taking",
    "tck": "tackling", "tec": "technique",
    # Mental.
    "agg": "aggression", "ant": "anticipation", "bra": "bravery", "cmp": "composure",
    "cnt": "concentration", "dec": "decisions", "fla": "flair", "ldr": "leadership",
    "otb": "off_the_ball", "tea": "teamwork", "vis": "vision", "wor": "work_rate",
    # Physical.
    "agi": "agility", "bal": "balance", "jum": "jumping_reach", "nat": "natural_fitness",
    "sta": "stamina", "str": "strength",
    # Goalkeeping.
    "aer": "aerial_reach", "cmd": "command_of_area", "com": "communication",
    "ecc": "eccentricity", "han": "handling", "kic": "kicking", "one": "one_on_ones",
    "pun": "punching", "ref": "reflexes", "rus": "rushing_out", "thr": "throwing",
    # Hidden.
    "dirt": "dirtiness", "vers": "versatility",
}  # fmt: skip


def resolve_field(name: str, known: Collection[str], position: int | None = None) -> str:
    """Return the canonical field for a user-typed name, or raise with suggestions."""
    lowered = name.lower()
    field = ALIASES.get(lowered, lowered)
    if field in known:
        return field
    candidates = [*known, *ALIASES]
    suggestions = tuple(difflib.get_close_matches(lowered, candidates, n=3))
    raise UnknownFieldError(name, suggestions, position)
