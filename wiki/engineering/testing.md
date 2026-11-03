---
title: Testing
updated: 2026-11-03
sources:
  - tests/
  - tests/conftest.py
  - tests/factories.py
  - .github/workflows/ci.yml
source_commit: 2025c37
confidence: high
---

# Testing

| Livello | Dove | Dati |
| --- | --- | --- |
| Dominio e applicazione | `tests/domain`, `tests/application` | factory sintetiche (`tests/factories.py`), fake in memoria (`tests/application/fakes.py`) |
| Adattatori | `tests/adapters` | `tmp_path`; fmsave sostituito da `tests/adapters/fake_fmsave.py` |
| CLI | `tests/cli`, `tests/test_smoke.py` | app vera con sorgente finta |
| Integrazione | `tests/integration` (marker `real_save`) | save reale da `FMXRAY_TEST_SAVE` o `local/saves/**/*.fm`; saltato se assente |

- CI (`.github/workflows/ci.yml`): Linux e Windows; ruff, mypy, lint-imports, pytest; fallisce se un `*.fm`/`*.fmf` è tracciato. In CI il test reale è sempre saltato.
- Con il save presente la suite intera dura ~30 s (la lettura di fmsave ne prende ~25).
- Nessun save o dato di gioco nel repo (D1).
