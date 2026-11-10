"""Text normalisation shared by search and lookups."""

import unicodedata


def fold(text: str) -> str:
    """Lowercase and strip accents, so "unal celik" matches "Ünal Çelik"."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


_SMALL_WORDS = frozenset(
    {"a", "and", "at", "by", "for", "in", "into", "of", "on", "the", "to", "with"}
)


def humanize(name: str) -> str:
    """'off_the_ball' -> 'Off the Ball': field names and enum values as FM writes them."""
    words = name.split("_")
    return " ".join(
        w if i and w in _SMALL_WORDS else w[:1].upper() + w[1:] for i, w in enumerate(words)
    )
