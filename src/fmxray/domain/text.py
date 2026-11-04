"""Text normalisation shared by search and lookups."""

import unicodedata


def fold(text: str) -> str:
    """Lowercase and strip accents, so "unal celik" matches "Ünal Çelik"."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()
