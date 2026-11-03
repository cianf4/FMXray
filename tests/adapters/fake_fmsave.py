"""A stand-in for the fmsave module with the same shape, so adapter tests need no save."""

import warnings
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

from fmxray.adapters.fmsave_source.mapping import COLUMN_MAP


class FmsaveError(Exception):
    pass


class UnsupportedGameError(FmsaveError):
    pass


class CorruptSaveError(FmsaveError):
    pass


class NotAFmSaveError(FmsaveError):
    pass


class ReaderCheckError(FmsaveError):
    pass


class UnknownBuildWarning(UserWarning):
    pass


class Player:
    pass


def flat_columns(rows: int = 2) -> dict[str, list[Any]]:
    """Flat fmsave columns (as `Table.to_columns()` returns them) for `rows` players."""
    columns: dict[str, list[Any]] = {}
    for flat in COLUMN_MAP.values():
        if flat in ("birth_date", "contract_start", "contract_end", "loan_end"):
            value: Any = date(2000, 1, 1)
        elif flat in ("name", "full_name", "club_name", "loan_parent_club_name"):
            value = "Paulo Dybala"
        elif flat in ("transfer_value_state", "contract_squad_status"):
            value = "ok"
        elif flat in ("second_nation_ids", "natural_positions", "accomplished_positions", "traits"):
            value = ()
        elif flat == "on_loan":
            value = False
        else:
            value = 10
        columns[flat] = [value] * rows
    columns["ability_current"] = [150, 120][:rows] + [100] * max(0, rows - 2)
    columns["contract_clauses"] = [()] * rows
    columns["contract_unknown_e2"] = [7] * rows  # extra fmsave column we must drop
    return columns


def make_fake_module(
    game: str = "FM27",
    columns: dict[str, list[Any]] | None = None,
    open_error: Exception | None = None,
    warn: str | None = None,
    statuses: dict[str, str] | None = None,
) -> ModuleType:
    module = ModuleType("fake_fmsave")
    data = columns if columns is not None else flat_columns()

    @contextmanager
    def open_(path: Path) -> Iterator[SimpleNamespace]:
        if open_error is not None:
            raise open_error
        if warn is not None:
            warnings.warn(warn, UnknownBuildWarning, stacklevel=2)
        info = SimpleNamespace(
            game=game,
            build="27.0.0+2493426",
            known_build=False,
            db_version="27.0.0+0",
            game_date=date(2026, 9, 12),
        )
        table = SimpleNamespace(to_columns=lambda: data)
        yield SimpleNamespace(info=info, players=lambda: table)

    def field_status(model_class: type, field_name: str) -> str:
        return (statuses or {}).get(field_name, "unconfirmed")

    module.__dict__.update(
        open=open_,
        field_status=field_status,
        Player=Player,
        UnsupportedGameError=UnsupportedGameError,
        CorruptSaveError=CorruptSaveError,
        NotAFmSaveError=NotAFmSaveError,
        ReaderCheckError=ReaderCheckError,
        UnknownBuildWarning=UnknownBuildWarning,
        __version__="0.9.3",
    )
    return module
