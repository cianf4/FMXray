---
title: Mappa delle modifiche
updated: 2026-11-03
sources:
  - src/fmxray
source_commit: 2025c37
confidence: high
---

# Mappa delle modifiche

| Se devi… | Parti da |
| --- | --- |
| aggiungere/rinominare una colonna giocatore | `domain/fields.py` + `adapters/fmsave_source/mapping.py` |
| cambiare come si legge il save / aggiornare fmsave | `adapters/fmsave_source/` + `pyproject.toml` |
| cambiare dove/come si salvano gli snapshot | `adapters/parquet_store/store.py` |
| cambiare lo schema del catalogo | nuova voce in `adapters/sqlite_catalog/schema.py` `MIGRATIONS` |
| cambiare il flusso di import | `application/import_save.py` |
| aggiungere un comando | `cli/commands.py` + `cli/render.py` (+ caso d'uso in `application/`) |
| collegare un nuovo adattatore | `bootstrap.py` |
