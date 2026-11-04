"""Errors of the search domain."""


class SearchError(ValueError):
    """Base class for search errors shown to the user."""


class UnknownFieldError(SearchError):
    def __init__(
        self, field: str, suggestions: tuple[str, ...] = (), position: int | None = None
    ) -> None:
        self.field = field
        self.suggestions = suggestions
        self.position = position
        where = "" if position is None else f" at character {position + 1}"
        hint = f"; did you mean: {', '.join(suggestions)}?" if suggestions else ""
        super().__init__(f"unknown field {field!r}{where}{hint}")


class QueryParseError(SearchError):
    def __init__(self, message: str, position: int) -> None:
        self.position = position
        super().__init__(f"{message} (at character {position + 1})")


class SpecFormatError(SearchError):
    """A stored filter tree cannot be read."""
