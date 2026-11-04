---
title: Decisioni
updated: 2026-11-03
sources:
  - docs/superpowers/specs/2026-11-03-fm-x-ray-design.md
  - https://github.com/rhiever/fmsave
  - https://rhiever.github.io/fmsave/changelog.html
source_commit: unknown
confidence: medium
---

# Decisioni

Prese dall'utente durante il brainstorming (2026-10-31 → 2026-11-03). Dettagli nella
[spec madre](../../docs/superpowers/specs/2026-11-03-fm-x-ray-design.md).

| ID | Decisione | Perché | Fonte |
| --- | --- | --- | --- |
| D1 | Uso personale, single player, **sola lettura**: niente editing, niente overlay nel gioco. Si distribuisce solo codice, mai dati SI/SEGA | perimetro voluto dall'utente; i dati del gioco non sono nostri | brainstorming |
| D2 | Fonte dati delle Fasi 1 e 2 = **fmsave** (MIT), **versione bloccata**, aggiornata solo dopo aver letto il changelog | partire subito su un parser che già funziona | brainstorming, [fmsave](../reference/fmsave.md) |
| D3 | **Un solo modulo adattatore** parla con fmsave e traduce i suoi record nel nostro modello; nessun altro modulo importa fmsave | isolarsi dai cambi di API (26 release in 6 settimane); poter sostituire la fonte (copia nostra di fmsave o lettura da RAM) | brainstorming |
| D4 | **Niente parser del save scritto da noi** | formato binario compresso, non documentato, cambia tra build: costo e manutenzione troppo alti | brainstorming, [fmsave](../reference/fmsave.md) |
| D5 | Contributi a fmsave **solo tramite issue**, con prove verificate nel gioco, mai allegando save | il maintainer non fa merge di PR esterne e dà credito a chi apre la issue | [README fmsave](https://github.com/rhiever/fmsave) |
| D6 | **Fase 3** (lettura dalla RAM con plugin BepInEx 6 IL2CPP) solo dopo, come seconda fonte degli stessi dati, per **Windows e Linux via Proton**. Niente reverse engineering manuale di offset | robustezza agli aggiornamenti; serve anche a verificare i campi che fmsave segna come non confermati | brainstorming, [prior art](../reference/prior-art.md) |
| D7 | ~~FM26 obiettivo principale~~ → **FM27 obiettivo principale** (2026-11-03), build di riferimento `27.0.0+2493426`; FM26 nei limiti di fmsave | l'utente ha installato e gioca solo FM27; fmsave 0.9.3 legge `players()` del suo save | brainstorming, [verifiche](../reference/fmsave.md) |
| D8 | Processo: skill superpowers **inline, senza multi-agente**: brainstorming → spec madre → per ogni SP spec → piano → esecuzione con TDD. Documentazione in italiano, codice in inglese; i commit li fa l'utente | stesso schema che funziona in Quizard | brainstorming |
| D9 | Qualità del codice da senior: design pattern dove servono, estendibilità, SOLID/GRASP, niente astrazioni inutili | richiesta esplicita dell'utente | brainstorming |
| D10 | **App desktop** per Linux e Windows in **PySide6 + Qt Widgets**, pensata per stare sul secondo schermo mentre FM è aperto sul primo | l'utente non vuole l'aspetto da sito web; la tabella model/view di Qt disegna solo le righe visibili (600k giocatori); un solo linguaggio e un solo processo | brainstorming |
| D11 | **Logica separata dalla UI:** lettura, storage, filtri, rating e proiezioni in moduli Python che non importano Qt; la UI è uno strato sostituibile (QML o web in futuro). Mockup e stile grafico si decidono nel sottoprogetto dell'interfaccia | testabilità senza finestre; Qt Widgets ha uno stile meno flessibile del web | brainstorming |
| D12 | Storico per tutti i giocatori, **sfoltito**: ultimi 30 giorni di gioco completi, poi uno al mese, poi uno a stagione; il primo snapshot della carriera non si cancella | curva fitta sul recente senza GB di dati | spec madre §5 |
| D13 | Storage: **Parquet** per snapshot + **Polars** per le query + **SQLite** per lo stato dell'utente; DuckDB e delta solo se servono | snapshot immutabili = file; filtri in ms su 600k righe | spec madre §5 |
| D14 | Pesi dei ruoli in **TOML** (`tomllib` in lettura, `tomlkit` dall'editor), pesi tutti visibili | editabile a mano, commenti, stdlib | spec madre §9 |
| D15 | Test su tre livelli: factory sintetiche, adattatore con oggetti finti, integrazione su save in `local/` saltata se assente | niente dati di gioco nel repo | spec madre §11 |
| D16 | uv, **Python 3.14** (deciso in SP1: tutte le dipendenze la supportano), Ruff, mypy strict, pytest, pytest-qt, Hypothesis; CI GitHub Actions Linux + Windows | qualità e due sistemi operativi | spec madre §11 |
| D17 | Architettura esagonale (domain, application, adapters, ui, cli, bootstrap) con regole di import verificate in CI; Strategy, Repository, Specification, Observer | sostituibilità di fonti, storage e UI | spec madre §3 |
| D18 | Newgen: confronto con il primo snapshot della carriera, più save del giorno 1 opzionale | nessun flag diretto nel save | spec madre §9 |
| D19 | Distribuzione: `uv run` fino a SP8, poi PyInstaller | uso personale | spec madre §11 |
| D20 | Ordine dei sottoprogetti SP1–SP9 della spec madre §12 | | spec madre §12 |
| D21 | Interfaccia in **inglese**, testi pronti per la traduzione (`tr()`) | scelta dell'utente | spec madre §8 |
| D22 | Repository **pubblico** su GitHub, licenza **MIT** | scelta dell'utente | spec madre §11 |

## Ancora da decidere

Niente: tutti i temi della spec madre sono chiusi.
