---
title: Requisiti
updated: 2026-10-31
sources:
  - brainstorming 2026-10-31
source_commit: unknown
confidence: medium
---

# Requisiti

Dal brief dell'utente del 2026-10-31. Lo stato è "proposto" finché la spec madre
non li fissa.

## Funzionali

| ID | Requisito | Fase | Stato |
| --- | --- | --- | --- |
| R1 | Leggere un save `.fm` di FM26 da disco e mostrare tutti i giocatori del database | 1 | proposto |
| R2 | Ricerca con filtri combinabili, anche su CA, PA e hidden (es. età < 22 **e** PA > 180) | 1 | proposto |
| R3 | Tabella ordinabile | 1 | proposto |
| R4 | Scheda giocatore con tutti i dati disponibili (attributi, hidden, personalità, CA/PA, contratto, valore, tratti, ruoli) | 1 | proposto |
| R5 | Export CSV | 1 | proposto |
| R6 | Rilevare i newgen in modo dedotto: (a) `unique_id` assenti in un save di riferimento creato al giorno 1 con lo stesso database; (b) persone nuove tra snapshot successivi della stessa carriera | 1–2 | proposto |
| R7 | Rating per ruolo come media pesata normalizzata, stesso schema dei `.grf` di Genie Scout; pesi in un file modificabile dall'utente, con valori di partenza dai test di FM-Arena | 2 | proposto |
| R8 | Proiezione degli attributi futuri: scalare verso la PA preservando il profilo, poi correggere per età e tipo (fisici calano, mentali e tecnici crescono più a lungo), limite 20. Da qui il rating futuro per ruolo | 2 | proposto |
| R9 | Snapshot nel tempo: salvare ogni lettura per avere crescita della CA, progress rate e newgen | 2 | proposto |
| R10 | Asking price **stimato** (da valore, contratto, stato di mercato, età, reputazione), marcato chiaramente come stima | 2 | proposto, opzionale |
| R11 | Lettura dalla RAM col gioco aperto, solo se il save non basta | 3 | opzionale |

## Verifiche iniziali su un save reale (prima di fissare la Fase 1)

| ID | Domanda | Note dalla documentazione |
| --- | --- | --- |
| V1 | Quali hidden ci sono davvero | fmsave dichiara 5 hidden tra i 52 attributi e 8 di personalità: vedi [fmsave](../reference/fmsave.md) |
| V2 | Le clausole rescissorie sono esposte? | sì sulla carta, come `Clause` in `contract.clauses`, valore in unità interna |
| V3 | Tempi di lettura su un save grande | non documentati: decide la strategia di cache |
| V4 | Conversione dell'unità monetaria interna nella valuta mostrata | da calibrare confrontando con i valori nel gioco |

Stato al 2026-11-03: V2, V3, V6 fatte (vedi [fmsave](../reference/fmsave.md)); V1 e V4 rimandate dall'utente a dopo l'uscita di FM27, con confronto anche verso un tool esterno; V5 e V7 spostate in SP4.

## Non funzionali

| ID | Requisito | Fonte |
| --- | --- | --- |
| N1 | Sola lettura, nessuna rete, nessun dato del gioco nel repo | D1 in [decisioni](decisions.md) |
| N2 | Python 3.12+ (vincolo di fmsave) | [fmsave](../reference/fmsave.md) |
| N3 | Prestazioni accettabili con 50k–600k giocatori | brainstorming |
| N4 | Gira su Windows e Linux | brainstorming |
| N5 | Ogni campo con stato "non confermato" in fmsave è riconoscibile come tale | ipotesi proposta in chat, da confermare nella spec |
| N6 | Codice estendibile e manutenibile (pattern, SOLID/GRASP) | D9 in [decisioni](decisions.md) |
