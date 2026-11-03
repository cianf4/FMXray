"""Command-line interface: parses arguments and calls use cases."""

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from fmxray.application.errors import CareerNotFoundError, FmxrayError
from fmxray.application.import_save import ImportSave
from fmxray.application.ports import CatalogStore
from fmxray.application.show_player import ShowPlayer
from fmxray.cli import render


@dataclass(frozen=True)
class App:
    import_save: ImportSave
    show_player: ShowPlayer
    catalog: CatalogStore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fmxray", description="FM X-Ray scouting tool")
    parser.add_argument("--version", action="version", version=f"fmxray {version('fmxray')}")
    parser.add_argument("--data-dir", help="where snapshots and the catalog are stored")
    commands = parser.add_subparsers(dest="command", required=True)

    imp = commands.add_parser("import", help="import a save into a career")
    imp.add_argument("save", type=Path)
    imp.add_argument("--career", required=True)

    snaps = commands.add_parser("snapshots", help="list imported snapshots")
    snaps.add_argument("--career")

    show = commands.add_parser("show", help="print every field of a player")
    show.add_argument("query")
    show.add_argument("--career", required=True)
    show.add_argument("--uid", type=int)
    show.add_argument("--snapshot")
    return parser


def _show(app: App, args: argparse.Namespace) -> int:
    if args.uid is not None:
        print(render.player_details(*app.show_player.details(args.career, args.uid, args.snapshot)))
        return 0
    found = app.show_player.find(args.career, args.query, args.snapshot)
    if not found:
        print(f"no player matches {args.query!r}")
        return 1
    if len(found) > 1:
        print(render.matches(found))
        return 2
    print(render.player_details(*app.show_player.details(args.career, found[0].uid, args.snapshot)))
    return 0


def run(argv: Sequence[str], app_factory: Callable[[str | None], App]) -> int:
    args = _parser().parse_args(argv)
    app = app_factory(args.data_dir)
    try:
        if args.command == "import":
            print(render.import_result(app.import_save.execute(args.save, args.career)))
            return 0
        if args.command == "snapshots":
            career_id = None
            if args.career is not None:
                career_id = app.catalog.find_career(args.career)
                if career_id is None:
                    raise CareerNotFoundError(f"no career named {args.career!r}")
            print(render.snapshots(app.catalog.list_snapshots(career_id)))
            return 0
        return _show(app, args)
    except (FmxrayError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
