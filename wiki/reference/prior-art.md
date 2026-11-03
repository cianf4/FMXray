---
title: Tool esistenti e fonti di riferimento
updated: 2026-10-31
sources:
  - https://rhiever.github.io/fmsave/app/
  - https://github.com/mavarobli/FMSuperScout
  - https://www.fmscout.com/a-fm-genie-scout-26.html
  - https://fm-arena.com/thread/19725-bug-in-fm-genie-scout-rating-calculation-is-wrong/
  - https://fm-arena.com/table/26-player-attributes-testing/
  - https://www.fmscout.com/a-guide-to-current-ability-in-football-manager.html
  - https://github.com/lastrider04/FM26-Analyst
  - https://github.com/poi82999/fm26rte
  - brainstorming 2026-10-31
source_commit: unknown
confidence: medium
---

# Tool esistenti e fonti di riferimento

Controllato il 2026-10-31. Serve a capire in cosa FM X-Ray si distingue e cosa
possiamo imparare. **Non si copia codice** da progetti con licenza copyleft o
assente (K11 in [rischi](../project/risks.md)).

## Tool

| Tool | Come legge i dati | Cosa offre | Piattaforma | Licenza |
| --- | --- | --- | --- | --- |
| [fmsave web app](https://rhiever.github.io/fmsave/app/) | save, nel browser | tutti i giocatori, CA/PA, hidden, percentili per ruolo, filtri, shortlist, CSV | browser | MIT (fmsave) |
| [FMSuperScout](https://github.com/mavarobli/FMSuperScout) | RAM, plugin BepInEx 6 IL2CPP (C#), dump con F9 | web app Node locale; 19 ruoli; "meta score" pesato su FM-Arena; proiezione attributi verso la PA; crescita CA tra dump; radar newgen; stima asking price; filtri per attributo con preset; confronto; analisi rosa | Windows (Steam, Epic, Game Pass beta) | non trovata (LICENSE in 404) |
| [Genie Scout 26](https://www.fmscout.com/a-fm-genie-scout-26.html) | RAM | ricerca, CA/PA, hidden, rating per ruolo, progress rate; edizione "g": ricerca per rating, probabilità di sviluppo, giocatori simili; valore di vendita stimato | Windows | closed source; EULA vieta l'export oltre nome, club, età |
| [FM26-Analyst](https://github.com/lastrider04/FM26-Analyst) | RAM, lettore esterno in Python | storico partite, CA nel tempo, punteggi per ruolo, coach AI | Windows, build `FM26.fm26-rel-prod.2329565` | GPL-3.0 |
| [fm26rte](https://github.com/poi82999/fm26rte) | RAM, editor esterno (Rust + Tauri + React) basato su cheat table e analisi IL2CPP | editor runtime | Windows (admin) | nessuna |
| FM Live Editor | RAM | editor runtime a pagamento | Windows | commerciale |

Segnalati dall'utente, non ancora verificati: `ryanreo/football-manager-mcp`
(plugin BepInEx che parla con un'app esterna tramite named pipe) e
`torojoh/FM26-Camera-Mod` (guida all'installazione di BepInEx per FM26).

## Come lavora FMSuperScout (utile per la Fase 2)

- **Snapshot:** ogni dump è un file JSON in `%LOCALAPPDATA%\FMSuperScout\`; dal
  confronto tra dump nascono crescita della CA e radar dei newgen.
- **Proiezione:** ogni attributo scalato verso la PA (la CA è una somma pesata
  lineare, quindi il profilo si conserva), poi corretto per età e tipo; limite 20.
- **Asking price:** parte dal valore di mercato e corregge per durata del
  contratto, stato di mercato, età, potenziale, reputazione del club. Dichiarata
  come stima.
- **Valore mancante:** modello log-lineare calibrato sui giocatori che hanno un
  valore, mostrato come intervallo.
- Prestazioni dichiarate: circa 45k persone in ~10 s, circa 635k in ~17 s.

## Rating e pesi

- **FM-Arena** ([tabella](https://fm-arena.com/table/26-player-attributes-testing/)):
  alza (o abbassa) un attributo di 5 a tutta la squadra e misura punti, gol fatti
  e subiti su 2400 partite, contro una base di 60 punti. In cima: +5 Pace (80.5),
  +5 Acceleration (80.4), +4 a tutti i tecnici (75.2), +4 a tutti i mentali
  (72.4), +5 Jumping Reach (71.6), +5 Dribbling (69.8). È un valore **per
  attributo**, non per ruolo. Il titolo della pagina sembra riferirsi ancora a
  FM24: da verificare.
- Secondo commenti su FM-Arena, hidden e personalità **non costano CA**.
- **Formula della CA** ([FMScout](https://www.fmscout.com/a-guide-to-current-ability-in-football-manager.html)):
  media pesata degli attributi con pesi per posizione, visibili nell'editor
  pre-partita dal FM21; aggression, determination, flair e natural fitness non
  contano; costo extra sopra ~17; i pesi cambiano tra versioni.
- **Bug dei rating di Genie Scout** ([thread](https://fm-arena.com/thread/19725-bug-in-fm-genie-scout-rating-calculation-is-wrong/)):
  ipotesi di coefficienti nascosti per attributo e bonus per l'altezza (+50 tra
  180 e 190 cm, +100 sopra 190). La prova è codice di GS2011, quindi è debole.

## Cosa ne ricaviamo

- Fase 1 da sola si sovrappone alla web app di fmsave: il nostro valore sta in
  persistenza, snapshot, pesi modificabili, proiezioni e libertà di export.
- FMSuperScout è il riferimento funzionale per la Fase 2 e, per l'approccio,
  per la Fase 3.
- I pesi della CA dell'editor ufficiale di FM26 sono la base più solida per la
  proiezione.
