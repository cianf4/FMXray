"""Composition root: builds adapters and use cases, then hands over to the CLI."""

from collections.abc import Sequence
from importlib.metadata import version


def main(argv: Sequence[str] | None = None) -> int:
    print(f"fmxray {version('fmxray')}")
    return 0
