---
title: Mappa delle modifiche
updated: 2026-11-06
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
| aggiungere sintassi alla barra di ricerca | `domain/search/parser.py` (+ un nodo in `spec.py` e `compile.py` se serve) |
| aggiungere un alias o un campo calcolato | `domain/search/aliases.py`, `domain/search/derived.py` |
| aggiungere o spostare un filtro nel popup | `application/filter_layout.py` (`FILTER_TABS`, `control_kind`) |
| cambiare colori, font, spaziature | `ui/theme.py` (`TOKENS`) |
| aggiungere una vista di colonne pronta | `application/column_views.py` |
| cambiare il layout della finestra | `ui/main_window.py` |
| cambiare il formato JSON delle ricerche salvate | `domain/search/spec.py`: nuova `SPEC_VERSION` con conversione della vecchia |
