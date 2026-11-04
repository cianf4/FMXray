# SP2 — Motore di ricerca: design

> Sottoprogetto 2 della [spec madre](2026-11-03-fm-x-ray-design.md) (§7, §12). Decisioni prese con l'utente il 2026-11-04 (risposte 1–13 del brainstorming, tutte come proposte). Dopo l'approvazione: `superpowers:writing-plans` → `docs/superpowers/plans/2026-11-04-sp2-ricerca.md` → `superpowers:executing-plans` con TDD.

## Intento

Poter cercare nel database dei giocatori con filtri combinabili su qualunque campo, compresi CA, PA e hidden: per esempio "età < 22 e PA > 180". Le ricerche si possono salvare, e una ricerca salvata dice quali giocatori sono **nuovi** rispetto allo snapshot precedente. Tutto da terminale e coperto da test; l'interfaccia grafica (SP3) userà gli stessi casi d'uso.

## Obiettivi

1. Albero di filtri nel dominio (Composite/Specification), serializzabile in JSON con versione e compilato in espressioni Polars.
2. Barra di ricerca a testo con sintassi compatta, alias corti ed errori leggibili.
3. Due campi calcolati: `contract_left` (mesi di contratto rimasti alla data di gioco) e `free_agent`.
4. Caso d'uso di ricerca con ordinamento e limite.
5. Export CSV.
6. Ricerche salvate globali, con "nuovi risultati" calcolati per carriera.
7. Comandi `fmxray search` e `fmxray searches`.

## Non obiettivi (restano ad altri sottoprogetti)

- Interfaccia grafica, watcher della cartella (SP3). Storico, crescita, newgen (SP4). Rating per ruolo (SP5), proiezioni (SP6), asking price (SP7).
- Conversione dei soldi in euro (aspetta V4).

## Anti-obiettivi

- Una ricerca che dà risultati diversi a seconda che arrivi dal testo o dall'albero JSON.
- Un nome di campo sbagliato che restituisce "zero risultati" invece di un errore.
- Un valore mancante trattato come zero (es. un giocatore senza valore che passa `transfer_value<1000000`).
- Una ricerca salvata che smette di funzionare quando cambia la sintassi del testo.

## Vincoli

- Valgono i Global Constraints di SP1 (Python 3.14, versioni bloccate, l'utente lancia installazioni e commit, niente segnaposti, niente attribuzioni a Claude).
- **Nessuna dipendenza nuova:** parser scritto a mano, stdlib (`difflib` per i suggerimenti) e Polars.
- Il dominio di ricerca non importa Qt, fmsave, SQLite.
- Obiettivo di prestazioni: una ricerca su 126.427 righe in **meno di 200 ms**, escluso il caricamento dello snapshot.

## Decisioni

### Sintassi del testo (utente: 1–4, 11)

- Termini separati da spazio = **and**. Parole chiave `and`, `or`, `not` (senza maiuscole/minuscole) e parentesi. Precedenza: `not` > `and` > `or`.
- Confronti: `campo<valore`, `<=`, `>`, `>=`, `=`, `!=`; spazi intorno all'operatore permessi (`age < 22`).
- Forme con `:`:
  - `pos:dc` → valutazione nella posizione **≥ 15**; `natural:dc` → **≥ 18**;
  - `club:roma`, `name:dybala` → testo contenuto, senza maiuscole e accenti;
  - `trait:dictates_tempo` → la lista dei tratti contiene il valore;
  - `campo:none` → il valore manca.
- Valori: interi, decimali, date ISO (`2027-06-30`), testo tra virgolette (`club:"A.S. Roma"`), `true`/`false`.
- Attributi nella scala 1–20; scala 1–100 con il nome esplicito `<attributo>_raw`.
- Alias: una tabella unica nel dominio (es. `acc`→`acceleration`, `pac`→`pace`, `det`→`determination`, `inj`→`injury_proneness`, `cons`→`consistency`, `imp`→`important_matches`, `prof`→`professionalism`, `amb`→`ambition`, `value`→`transfer_value`, `wage`→`contract_wage`).
- Nome sconosciuto → errore con posizione e suggerimento (`difflib.get_close_matches`).
- Un confronto su un valore mancante **esclude** la riga.

### Soldi (utente: 5)

I filtri su valore, stipendio e clausole usano l'unità interna del save. Il comando `search` stampa un avviso quando la ricerca tocca un campo `money_internal`.

### Campi calcolati (utente: 7)

Calcolati al momento della ricerca, non salvati nello snapshot. Provenienza `derived`.
- `contract_left`: mesi interi tra `game_date` dello snapshot e `contract_end` (arrotondati per difetto); vuoto se manca uno dei due.
- `free_agent`: `club_uid` vuoto.

### Ricerche salvate (utente: 6; design: 13)

- Globali (non legate a una carriera), nome univoco.
- Si salvano il testo scritto e l'albero in JSON con `"version": 1`; all'esecuzione si usa l'albero.
- "Nuovi risultati": giocatori (per `uid`) che soddisfano la ricerca nell'ultimo snapshot della carriera e non nel precedente. Con un solo snapshot, nessuno è "nuovo". *(Dipende da V5: se `uid` non fosse stabile tra save della stessa carriera, si passerà a `unique_id`; il confronto sta in un solo punto del codice.)*
- Storage: SQLite, migrazione alla versione 2 con la tabella `saved_searches`.

### Export CSV (utente: 8)

Tutte le colonne di default (catalogo + calcolate), `--columns` per scegliere. UTF-8 con BOM, separatore virgola. Le liste (ruoli, tratti) diventano testo separato da `|`.

### Comandi (design: 9)

| Comando | Effetto |
| --- | --- |
| `fmxray search QUERY --career NOME [--sort campo:desc,campo] [--limit N] [--csv FILE] [--columns a,b,c]` | stampa i risultati (default: ordinati per `ca` decrescente, primi 50) o li esporta |
| `fmxray searches save NOME QUERY` | salva (o sovrascrive con `--replace`) |
| `fmxray searches list` | elenca nome e testo |
| `fmxray searches run NOME --career NOME [...]` | come `search`, con i nuovi risultati marcati |
| `fmxray searches delete NOME` | cancella |

### Architettura (design: 10)

Nuovo pacchetto `fmxray.domain.search` (Python puro + Polars):
- `spec.py`: nodi dell'albero (dataclass immutabili) e (de)serializzazione JSON;
- `compile.py`: visitor che produce un `pl.Expr`;
- `parser.py`: tokenizer + discesa ricorsiva;
- `aliases.py`: alias e risoluzione dei nomi;
- `derived.py`: campi calcolati.

Casi d'uso in `fmxray.application.search` e porta `SavedSearchStore`; adattatore SQLite nello stesso `sqlite_catalog`.

## Lasciato a chi costruisce

- Nomi interni dei nodi e dei token; formato esatto della tabella stampata.
- Elenco completo degli alias oltre a quelli fissati sopra.

## Criteri di successo

1. `uv run fmxray search "age<22 pa>180" --career Roma` sul save reale restituisce gli stessi giocatori di un filtro Polars scritto a mano (test di integrazione).
2. Ogni ricerca dà lo stesso risultato dal testo e dall'albero JSON (test con Hypothesis).
3. `fmxray search "finishng>15" --career Roma` termina con errore e suggerisce `finishing`.
4. Ricerca su 126k righe sintetiche sotto i 200 ms (test di prestazioni).
5. `searches run` segna come nuovi solo i giocatori entrati nel filtro rispetto allo snapshot precedente.
6. Il CSV si apre in Excel e LibreOffice con gli accenti corretti.
7. ruff, mypy, lint-imports e CI verdi; wiki aggiornata (modulo `search`).
