"""Domain errors."""


class SchemaMismatchError(ValueError):
    """A DataFrame does not match the columns and types of a FieldCatalog."""
