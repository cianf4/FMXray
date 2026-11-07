"""Where FM27 usually keeps its saves, on Windows and on Linux under Proton."""

from collections.abc import Mapping
from pathlib import Path

_FM27 = Path("Sports Interactive", "Football Manager 27")
_SAVE_DIRS = (Path("games"), Path("cloud", "games"))
STEAM_APP_ID = "4530370"  # Football Manager 27
_PROTON_LOCAL = Path(
    "steamapps", "compatdata", STEAM_APP_ID, "pfx", "drive_c", "users", "steamuser",
    "AppData", "Local",
)  # fmt: skip
_STEAM_ROOTS = (
    Path(".steam", "debian-installation"),
    Path(".steam", "steam"),
    Path(".local", "share", "Steam"),
)


def default_save_folders(env: Mapping[str, str], home: Path) -> list[Path]:
    """Existing save folders, Windows first; the Windows location is not verified yet."""
    bases: list[Path] = []
    if env.get("LOCALAPPDATA"):
        bases.append(Path(env["LOCALAPPDATA"]) / _FM27)
    bases += [home / root / _PROTON_LOCAL / _FM27 for root in _STEAM_ROOTS]
    candidates = (base / sub for base in bases for sub in _SAVE_DIRS)
    return [folder for folder in candidates if folder.is_dir()]
