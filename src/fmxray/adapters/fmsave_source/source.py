"""SaveSource backed by fmsave. The only module in FM X-Ray that talks to fmsave."""

import importlib
import warnings
from pathlib import Path
from types import ModuleType
from typing import Any

from fmxray.adapters.fmsave_source.mapping import FIELD_PATHS, to_frame
from fmxray.application.errors import UnreadableSaveError, UnsupportedSaveError
from fmxray.application.ports import SaveReading
from fmxray.domain.fields import PLAYER_CATALOG, RELEASE_CLAUSES, Provenance

# fmsave's own status labels describe FM26; on FM27 every field is unconfirmed.
_LABELLED_GAMES = frozenset({"FM26"})


class FmsaveSaveSource:
    def __init__(self, module: ModuleType | None = None) -> None:
        self._fm: Any = module if module is not None else importlib.import_module("fmsave")

    def read(self, path: Path) -> SaveReading:
        fm = self._fm
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                with fm.open(path) as save:
                    info = save.info
                    columns = save.players().to_columns()
        except fm.UnsupportedGameError as error:
            raise UnsupportedSaveError(str(error)) from error
        except fm.FmsaveError as error:
            # Corrupt, not a save, layout check failed, changed while reading, ...
            raise UnreadableSaveError(str(error)) from error

        return SaveReading(
            game=info.game,
            build=info.build,
            known_build=info.known_build,
            db_version=info.db_version,
            game_date=info.game_date,
            reader_version=fm.__version__,
            warnings=tuple(str(w.message) for w in caught),
            provenance=self._provenance(info.game),
            frame=to_frame(columns),
        )

    def _provenance(self, game: str) -> dict[str, Provenance]:
        provenance: dict[str, Provenance] = {}
        for name in PLAYER_CATALOG.names():
            if name in RELEASE_CLAUSES:
                provenance[name] = Provenance.DERIVED
            elif game in _LABELLED_GAMES:
                provenance[name] = Provenance(
                    self._fm.field_status(self._fm.Player, FIELD_PATHS[name])
                )
            else:
                provenance[name] = Provenance.UNCONFIRMED
        return provenance
