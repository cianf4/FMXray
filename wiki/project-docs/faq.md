---
title: FAQ
updated: 2026-10-31
sources:
  - wiki/project/decisions.md
source_commit: unknown
confidence: medium
---

# FAQ

Risposte basate sulle decisioni prese, non ancora su codice.

**Modifica i salvataggi?** No: sola lettura (D1 in [decisioni](../project/decisions.md)).

**Legge la memoria del gioco?** Non nelle Fasi 1 e 2, che leggono solo il file
di salvataggio. La lettura dalla RAM è una Fase 3 opzionale (D6).

**Usa internet?** No (D1).

**Contiene dati di Football Manager?** No: si distribuisce solo codice (D1).

**Funziona con FM27?** Nei limiti di quanto supporta fmsave (D7).
