# FM X-Ray

Personal, read-only scouting tool for Football Manager 27 (FM26 where the
fmsave library allows): reads a career save and shows the whole player database,
including CA, PA and hidden attributes.

Status: command line ready (import, search, saved searches, CSV export); desktop
UI in progress. Project wiki (Italian): [wiki/index.md](wiki/index.md).

```
uv sync
uv run fmxray import "local/saves/fm27/Roma.fm" --career Roma
uv run fmxray search "age<22 pa>180" --career Roma
```

Unofficial fan project, not affiliated with Sports Interactive or SEGA. This
repository contains code only: no game data, no save files.
