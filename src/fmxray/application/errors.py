"""Errors raised by use cases; adapters translate their own errors into these."""


class FmxrayError(Exception):
    """Base class for errors shown to the user."""


class UnreadableSaveError(FmxrayError):
    """The save is damaged, incomplete, or not laid out as expected."""


class UnsupportedSaveError(FmxrayError):
    """The save comes from a game or build the reader does not support."""


class CareerNotFoundError(FmxrayError):
    """No career with the given name exists."""


class SavedSearchExistsError(FmxrayError):
    """A saved search with that name already exists."""


class SavedSearchNotFoundError(FmxrayError):
    """No saved search with the given name exists."""
