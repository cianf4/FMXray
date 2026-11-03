---
title: Moduli cli e bootstrap
updated: 2026-11-03
sources:
  - src/fmxray/cli/commands.py
  - src/fmxray/cli/render.py
  - src/fmxray/bootstrap.py
  - tests/cli/test_commands.py
  - tests/test_smoke.py
source_commit: 2025c37
confidence: high
---

# Moduli cli e bootstrap

## Purpose
`bootstrap` è la composition root (costruisce adattatori e casi d'uso); `cli` analizza gli argomenti e chiama i casi d'uso. `cli` non importa adattatori né `bootstrap` (contratto 3), quindi `App` è definita in `cli/commands.py`.

## Public interface
| Comando | Effetto |
| --- | --- |
| `fmxray import SAVE --career NOME` | importa; stampa `imported …` o `already imported: …` |
| `fmxray snapshots [--career NOME]` | elenca gli snapshot (id carriera, data di gioco, build, righe) |
| `fmxray show QUERY --career NOME [--uid UID] [--snapshot ID]` | 1 risultato: tutti i campi per gruppo con provenienza; più risultati: elenco con uid (exit 2); nessuno: exit 1 |
| `--data-dir`, `FMXRAY_DATA_DIR` | cartella dati; default `platformdirs.user_data_dir("fmxray")` (su Linux `~/.local/share/fmxray`) |

Errori applicativi e di I/O: messaggio su stderr, exit 1.

## Verification
`uv run pytest tests/cli tests/test_smoke.py`
