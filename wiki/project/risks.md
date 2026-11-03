---
title: Rischi
updated: 2026-10-31
sources:
  - brainstorming 2026-10-31
  - https://rhiever.github.io/fmsave/changelog.html
  - https://rhiever.github.io/fmsave/guides/trust.html
  - https://rhiever.github.io/fmsave/reference/records.html
  - https://fm-arena.com/table/26-player-attributes-testing/
source_commit: unknown
confidence: medium
---

# Rischi

| ID | Rischio | Impatto | Evidenza | Mitigazione | Stato |
| --- | --- | --- | --- | --- | --- |
| K1 | API di fmsave instabile | alto | 26 release dal 2026-09-18 al 2026-10-30; cambi di colonne in 0.7.0 e 0.9.0 ([changelog](https://rhiever.github.io/fmsave/changelog.html)) | versione bloccata + adattatore unico (D2, D3) | aperto |
| K2 | Un solo maintainer, PR esterne non accettate | medio | README di fmsave | licenza MIT: possiamo tenerne una copia nostra | aperto |
| K3 | Campi "non confermati" con significato dubbio | medio | `fmsave.field_status(...)`; es. `contract.wage` è unconfirmed ([trust](https://rhiever.github.io/fmsave/guides/trust.html)) | controllare ogni campo usato; segnalarli nella UI; verificarli nel gioco | aperto |
| K4 | FM27: una sola build supportata, tutti i campi non confermati, limite di decompressione 256 MiB per frame e 512 MiB totali | medio | trust guide | FM26 come obiettivo principale (D7) | aperto |
| K5 | Soldi nell'unità interna del save | medio | `transfer_value`, `wage` e `Clause.value` non convertiti ([records](https://rhiever.github.io/fmsave/reference/records.html)) | conversione calibrata su valori visti nel gioco (V4) | aperto |
| K6 | Pesi per ruolo: FM-Arena misura il valore di un attributo per tutta la squadra, non per ruolo; la pagina della tabella potrebbe riferirsi ancora a FM24 | medio | [tabella FM-Arena](https://fm-arena.com/table/26-player-attributes-testing/) | pesi derivati da noi e modificabili dall'utente (R7) | aperto |
| K7 | La proiezione è una stima; la CA non è lineare sopra ~17 | medio | [guida CA di FMScout](https://www.fmscout.com/a-guide-to-current-ability-in-football-manager.html) | etichettare come stima; pesi della CA dall'editor ufficiale di FM26 | aperto |
| K8 | Lettura dalla RAM legata al gioco: si rompe con gli aggiornamenti; BepInEx sotto Proton non verificato per FM26 | medio | [prior art](../reference/prior-art.md) | Fase 3 opzionale e successiva (D6) | aperto |
| K9 | Dati di SI/SEGA nel repo o nelle issue | alto | D1; README di fmsave chiede di non allegare save | fixture sintetiche; niente save nel repo | aperto |
| K10 | Identità dei giocatori: `uid` cambia tra carriere, `unique_id` può essere `None`, le persone create in partita possono riusare ID di persone cancellate | medio | [records](https://rhiever.github.io/fmsave/reference/records.html), brainstorming | `uid` solo dentro un save, `unique_id` tra carriere, gestire `None` e collisioni | aperto |
| K11 | Licenze dei progetti di riferimento: FM26-Analyst GPL-3.0, fm26rte senza licenza, licenza di FMSuperScout non trovata | medio | [prior art](../reference/prior-art.md) | studiarli senza copiare codice finché la licenza non è chiara | aperto |
