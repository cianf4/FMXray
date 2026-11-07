from pathlib import Path

from fmxray.application.save_folders import default_save_folders

_FM27 = Path("Sports Interactive", "Football Manager 27")
_PROTON = Path("steamapps/compatdata/4530370/pfx/drive_c/users/steamuser/AppData/Local")


def test_finds_existing_proton_and_windows_folders(tmp_path: Path) -> None:
    home = tmp_path / "home"
    proton = home / ".steam" / "debian-installation" / _PROTON / _FM27 / "cloud" / "games"
    local_appdata = tmp_path / "AppData" / "Local"
    windows = local_appdata / _FM27 / "games"
    for folder in (proton, windows):
        folder.mkdir(parents=True)
    found = default_save_folders({"LOCALAPPDATA": str(local_appdata)}, home)
    assert found == [windows, proton]


def test_missing_folders_skipped(tmp_path: Path) -> None:
    assert default_save_folders({}, tmp_path) == []
