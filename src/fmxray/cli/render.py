"""Pure functions that turn use-case results into terminal text."""

from collections.abc import Mapping, Sequence

from fmxray.application.import_save import ImportResult, ImportStatus
from fmxray.application.show_player import PlayerMatch
from fmxray.domain.fields import PLAYER_CATALOG, FieldGroup
from fmxray.domain.snapshot import SnapshotMeta


def import_result(result: ImportResult) -> str:
    meta = result.meta
    if result.status is ImportStatus.ALREADY_IMPORTED:
        return f"already imported: {meta.snapshot_id}"
    return f"imported {meta.snapshot_id} ({meta.row_count} players, game date {meta.game_date})"


def snapshots(metas: Sequence[SnapshotMeta]) -> str:
    if not metas:
        return "no snapshots"
    header = f"{'snapshot':36}  {'career':>6}  {'game date':10}  {'game':4}  {'build':16}  rows"
    lines = [
        f"{m.snapshot_id:36}  {m.career_id:>6}  {m.game_date!s:10}  {m.game:4}  "
        f"{m.build:16}  {m.row_count}"
        for m in metas
    ]
    return "\n".join([header, *lines])


def matches(found: Sequence[PlayerMatch]) -> str:
    lines = [f"{'uid':>12}  {'name':30}  {'club':30}  age"]
    lines += [f"{m.uid:>12}  {m.name:30}  {m.club_name or '-':30}  {m.age}" for m in found]
    return "\n".join(lines)


def player_details(meta: SnapshotMeta, values: Mapping[str, object]) -> str:
    lines = [
        f"{values.get('name')} (uid {values.get('uid')}) — snapshot {meta.snapshot_id}, "
        f"{meta.game} {meta.build}, game date {meta.game_date}"
    ]
    for group in FieldGroup:
        specs = PLAYER_CATALOG.in_group(group)
        if not specs:
            continue
        lines.append(f"\n{group.name}")
        for spec in specs:
            provenance = meta.provenance.get(spec.name, "-")
            lines.append(f"  {spec.name:30} {values.get(spec.name)!s:30} [{provenance}]")
    return "\n".join(lines)
