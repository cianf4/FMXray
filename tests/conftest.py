"""Shared pytest fixtures."""

import os
from pathlib import Path

import pytest

# Qt widgets run without a display (CI, Linux servers); set before any Qt import.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def real_save_path() -> Path:
    """A real FM save from FMXRAY_TEST_SAVE or local/saves; skips the test when absent."""
    configured = os.environ.get("FMXRAY_TEST_SAVE")
    if configured:
        return Path(configured)
    found = sorted((REPO_ROOT / "local" / "saves").rglob("*.fm"))
    if not found:
        pytest.skip("no real save: set FMXRAY_TEST_SAVE or put one in local/saves/")
    return found[0]
