"""Command-line interface: parses arguments and calls use cases."""

import argparse
import sys
from collections.abc import Callable, Sequence
from importlib.metadata import version
from pathlib import Path

from fmxray.application.app import App
from fmxray.application.errors import CareerNotFoundError, FmxrayError
from fmxray.application.export import export_csv
from fmxray.application.search import SearchResult
from fmxray.cli import render
from fmxray.domain.search.errors import SearchError
from fmxray.domain.search.parser import parse, parse_sort
from fmxray.domain.search.spec import Spec, fields_in

DEFAULT_LIMIT = 50
TABLE_COLUMNS = ("uid", "name", "age", "club_name", "ca", "pa", "natural_positions")
MONEY_NOTE = "note: money fields are in the save's internal unit (not euros yet)"


def _positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _add_result_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--career", required=True)
    parser.add_argument("--sort", default="", help="e.g. pa:desc,age (default: ca:desc)")
    parser.add_argument("--limit", type=_positive_int, default=DEFAULT_LIMIT)
    parser.add_argument("--csv", type=Path, help="write the results to this CSV file")
    parser.add_argument("--columns", help="CSV columns, comma separated (default: all)")


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

    search = commands.add_parser("search", help='search players, e.g. "age<22 pa>180"')
    search.add_argument("query")
    _add_result_options(search)
    search.add_argument("--snapshot")

    searches = commands.add_parser("searches", help="manage saved searches")
    actions = searches.add_subparsers(dest="action", required=True)
    save = actions.add_parser("save", help="save a search")
    save.add_argument("name")
    save.add_argument("query")
    save.add_argument("--replace", action="store_true")
    actions.add_parser("list", help="list saved searches")
    run_saved = actions.add_parser("run", help="run a saved search, marking new players")
    run_saved.add_argument("name")
    _add_result_options(run_saved)
    delete = actions.add_parser("delete", help="delete a saved search")
    delete.add_argument("name")
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


def _output(
    args: argparse.Namespace,
    result: SearchResult,
    spec: Spec,
    new_uids: frozenset[int] | None = None,
) -> int:
    if result.money_fields:
        print(MONEY_NOTE, file=sys.stderr)
    if args.csv is not None:
        columns = None if args.columns is None else [c.strip() for c in args.columns.split(",")]
        rows = export_csv(result.frame, args.csv, columns)
        print(f"wrote {rows} rows to {args.csv}")
        return 0
    used = sorted((fields_in(spec) | {k.field for k in parse_sort(args.sort)}) - set(TABLE_COLUMNS))
    print(render.search_results(result, [*TABLE_COLUMNS, *used], new_uids))
    return 0


def _search(app: App, args: argparse.Namespace) -> int:
    spec = parse(args.query)
    sort = parse_sort(args.sort)
    result = app.search_players.execute(args.career, spec, sort, args.limit, args.snapshot)
    return _output(args, result, spec)


def _searches(app: App, args: argparse.Namespace) -> int:
    if args.action == "save":
        app.save_search.execute(args.name, args.query, replace=args.replace)
        print(f"saved {args.name!r}")
    elif args.action == "list":
        print(render.saved_searches(app.saved_searches.list()))
    elif args.action == "run":
        sort = parse_sort(args.sort)
        outcome = app.run_saved_search.execute(args.name, args.career, sort, args.limit)
        return _output(args, outcome.result, outcome.search.spec, outcome.new_uids)
    elif not app.saved_searches.delete(args.name):
        print(f"error: no saved search named {args.name!r}", file=sys.stderr)
        return 1
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
        if args.command == "search":
            return _search(app, args)
        if args.command == "searches":
            return _searches(app, args)
        return _show(app, args)
    except (FmxrayError, SearchError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
