---
title: FM X-Ray - scheda di progetto
updated: 2026-10-31
sources:
  - wiki/project-docs/project-brief.md
  - wiki/project/decisions.md
  - wiki/project/status.md
  - wiki/project/roadmap.md
source_commit: unknown
confidence: medium
---

# FM X-Ray

**Cos'è:** uno scouting tool per Football Manager 26 (poi FM27) che legge un
salvataggio e mostra tutto il database giocatori, compresi CA, PA e hidden. Uso
personale, single player, sola lettura.

**Perché esiste:** l'utente non vuole più dipendere da tool esterni (closed
source, solo Windows, legati alla memoria del gioco) per vedere i dati nascosti.

**Stato:** brainstorming in corso (2026-10-31), nessun codice.

**Aree tecniche:** Python 3.12+, libreria fmsave per leggere i save; più avanti
un plugin C# BepInEx per leggere la RAM. UI, storage e forma dell'app da
decidere.

**Prossimi passi:** chiudere le scelte aperte, scrivere la spec madre,
verificare i dati su un save reale, poi il primo sottoprogetto.

**Decisioni da ricordare:**
- fmsave con versione bloccata, dietro un solo modulo adattatore;
- niente parser del save scritto da noi;
- lettura dalla RAM solo dopo, per Windows e Linux (Proton);
- FM26 prima di FM27.

**Link:** [decisioni](project/decisions.md) · [requisiti](project/requirements.md) ·
[rischi](project/risks.md) · [roadmap](project/roadmap.md) ·
[architettura](engineering/architecture.md) · [fmsave](reference/fmsave.md) ·
[prior art](reference/prior-art.md)

## Personal Wiki Export

- **Progetto:** FM X-Ray - scouting tool per Football Manager 26/27 basato sui file di salvataggio.
- **Stato:** brainstorming, nessun codice (2026-10-31).
- **Ruolo nella vita/lavoro dell'utente:** progetto personale per le proprie carriere single player.
- **Motivazione personale:** non dipendere da tool esterni per i dati nascosti del gioco. Altro: Da confermare.
- **Tecnologie e competenze:** Python, lettura di formati binari tramite libreria (fmsave), analisi dati su 50k–600k record, in prospettiva C# e modding Unity IL2CPP (BepInEx).
- **Prossimi passi:** spec madre, verifiche su un save reale, primo sottoprogetto.
- **Note a lungo termine:** fmsave cambia spesso e ha un solo maintainer; FM27 esce il 2026-11-10; contributi a fmsave solo via issue.
