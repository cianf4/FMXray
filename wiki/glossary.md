---
title: Glossario
updated: 2026-10-31
sources:
  - wiki/reference/fmsave.md
  - wiki/reference/prior-art.md
  - brainstorming 2026-10-31
source_commit: unknown
confidence: medium
---

# Glossario

| Termine | Significato |
| --- | --- |
| CA (current ability) | abilità attuale, 1–200; media pesata degli attributi con pesi per posizione |
| PA (potential ability) | tetto massimo della CA; in fmsave `ability.potential` più `potential_range_code` |
| Attributi hidden | non visibili nel gioco: dirtiness, consistency, important matches, injury proneness, versatility, più gli 8 di personalità |
| Attributi di personalità | adaptability, ambition, controversy, loyalty, pressure, professionalism, sportsmanship, temperament |
| Raw attributes | attributi in scala 1–100 come li salva il gioco; l'interfaccia mostra 1–20 |
| Newgen (regen) | giocatore generato dal gioco durante la carriera; nessun flag diretto nel save |
| `uid` | ID di fmsave per i join dentro un save; cambia tra carriere |
| `unique_id` | Unique ID del database del gioco, stabile tra carriere dallo stesso database; può essere `None` |
| `database_id` | ID di competizioni e nazioni per collegare nomi forniti da fuori |
| Field status | `verified` o `unconfirmed`: se fmsave ha verificato il significato di un campo sul gioco |
| Coverage | quota di valori non `None` in una colonna di una `Table` di fmsave |
| Transfer value | valore di trasferimento salvato dal gioco (unità interna) |
| Asking price | prezzo richiesto dal club; non è nel save, si può solo stimare |
| Progress rate | velocità di crescita della CA nel tempo, calcolata tra snapshot |
| `.grf` | file di pesi per ruolo di Genie Scout |
| IL2CPP | modo in cui Unity compila il codice C# in nativo; FM26 lo usa |
| BepInEx | mod loader per giochi Unity; su IL2CPP genera gli interop assemblies (binding C# alle classi del gioco) |
| Proton | layer di compatibilità di Steam per far girare giochi Windows su Linux |
| SP | sottoprogetto: ognuno ha spec, piano e implementazione |
| Spec madre | documento che fissa stack, confini e ordine dei sottoprogetti |
