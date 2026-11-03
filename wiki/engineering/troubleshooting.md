---
title: Troubleshooting
updated: 2026-10-31
sources:
  - https://github.com/rhiever/fmsave
  - https://rhiever.github.io/fmsave/guides/trust.html
source_commit: unknown
confidence: low
---

# Troubleshooting

Nessun problema osservato nel nostro codice (non esiste ancora). Problemi
documentati da fmsave:

| Sintomo | Causa | Cosa fare |
| --- | --- | --- |
| Lettura fallita o incoerente col gioco aperto | il gioco sta scrivendo il save | copiare il save e leggere la copia |
| Save FM27 rifiutato | build diversa da `27.0.0+2486695` o layout non registrato | aspettare il supporto in fmsave |
| Save FM27 molto grande rifiutato | limite di decompressione (256 MiB per frame, 512 MiB totali) | nessuna soluzione lato nostro |
| Valori `None` | dato assente, join non risolto o decodifica fallita | controllare `table.coverage` e la validazione |
