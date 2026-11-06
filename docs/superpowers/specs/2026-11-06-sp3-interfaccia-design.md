# SP3 — Interfaccia della Fase 1: design

> Sottoprogetto 3 della [spec madre](2026-11-03-fm-x-ray-design.md) (§6, §8, §12). Decisioni prese con l'utente il 2026-11-06 (domande a scelta multipla e wireframe nel visual companion). Dopo l'approvazione: `superpowers:writing-plans` → `docs/superpowers/plans/2026-11-06-sp3-interfaccia.md` → `superpowers:executing-plans` con TDD.

## Intento

Un'app desktop da tenere sul secondo schermo mentre FM è aperto: si scelgono i filtri **con il mouse**, senza imparare nessuna sintassi, si vede la tabella dei giocatori e, con un click, la scheda completa. Quando FM salva, l'app si aggiorna da sola. SP3 fissa **struttura e funzionamento**; l'aspetto grafico ha un sottoprogetto suo (SP3b) subito dopo.

## Obiettivi

1. Finestra principale: barra della carriera, filtri rapidi, barra a testo facoltativa, colonna delle ricerche salvate e delle viste, tabella, scheda del giocatore a lato.
2. Popup "All filters" con sottoschede a blocchi (stile FMRTE) da cui si può filtrare **qualunque campo** del catalogo.
3. Ruoli scelti su un campo disegnato, con un livello per ogni posizione.
4. Tabella su 126.427+ righe fluida, con viste di colonne pronte e personalizzabili.
5. Segni discreti per i dati non confermati.
6. Aggiornamento automatico quando FM salva, più importazione manuale.
7. Tema scuro neutro costruito su token, pronto per essere sostituito in SP3b.

## Non obiettivi

- Design grafico definitivo (colori, font, icone, rifinitura): **SP3b**, con tre proposte (di Claude, con la skill impeccable, con la skill taste-skill).
- Storico, crescita, newgen, watchlist (SP4); rating per ruolo (SP5); proiezioni (SP6); asking price (SP7); eseguibili (SP8).
- Filtri con alberi annidati AND/OR/NOT dalla UI: restano possibili dalla barra a testo.
- Conversione dei soldi in euro (aspetta V4).

## Anti-obiettivi

- Costringere l'utente a scrivere la sintassi per fare una ricerca qualsiasi.
- Un campo del catalogo che non si può filtrare dalla UI.
- UI che si blocca durante un import, un filtro o un ordinamento.
- Logica (filtri, viste, import) dentro i widget: deve essere testabile senza aprire finestre.
- L'aspetto "sito web in React" (D10).
- Una tabella che appare tutta attenuata perché su FM27 ogni campo è "non confermato".

## Vincoli

- Valgono i Global Constraints di SP1 e SP2 (Python 3.14, versioni bloccate, installazioni e commit li lancia l'utente, niente segnaposti nei comandi, niente attribuzioni a Claude).
- **PySide6 + Qt Widgets** (D10); dipendenze nuove: `PySide6` e `pytest-qt` (verifiche sotto).
- Interfaccia in **inglese**, testi passati da `tr()` (D21). I nomi in italiano del wireframe sono solo descrittivi.
- `domain` e `application` non importano Qt; `ui` importa `application`, `domain`, PySide6, mai gli adattatori (contratto nuovo in import-linter).
- Linux e Windows; la CI esegue i test Qt anche su Linux senza schermo.
- Il filtro usa il motore di SP2 (albero `Spec` → Polars): nessun secondo motore.

## Decisioni

### Finestra principale (utente: layout, colonna A)

Dall'alto in basso:
1. **Barra della carriera:** carriera (menu), snapshot (di default l'ultimo; menu per scegliere un precedente), numero di giocatori, stato dell'aggiornamento automatico ("updated 2 min ago"), pulsante "Import…".
2. **Filtri rapidi:** età min–max, CA min, PA min, ruoli (menu con le posizioni), testo su nome o club; pulsanti "All filters… (N active)", "Save search", "Export CSV".
3. **Barra a testo** facoltativa (utente: "sì, facoltativa e sincronizzata"), vedi sotto.
4. **Corpo** in tre parti:
   - colonna sinistra con le **ricerche salvate** (con il numero dei nuovi, es. `+3`) e le **viste di colonne**;
   - **tabella** al centro, con il segno dei nuovi giocatori rispetto allo snapshot precedente quando è attiva una ricerca salvata, ordinamento cliccando l'intestazione, riga finale `N of TOTAL players`;
   - **scheda** del giocatore selezionato a destra.

### Popup "All filters" (utente: sottoschede a blocchi, stile FMRTE)

Finestra a parte (non modale), i risultati si aggiornano mentre si cambia un valore. Sottoschede:

| Scheda | Contenuto |
| --- | --- |
| General | età, data di nascita, altezza, nazione e seconde nazionalità, club, in prestito, CA, PA, reputazioni |
| Positions | campo cliccabile (vedi sotto) e piedi |
| Attributes | blocchi Technical, Mental, Physical, Goalkeeping; un cursore min–max (1–20) per ogni attributo |
| Hidden & personality | i 5 attributi hidden e gli 8 di personalità, stessi cursori |
| Contract & value | valore, stipendio, scadenza e mesi rimasti (`contract_left`), stato in rosa, svincolato, clausole |
| Traits | elenco dei tratti con caselle; "any" o "all" |

**Ogni campo del catalogo e ogni campo calcolato deve comparire in almeno una scheda** (test che lo verifica sul catalogo). Pulsanti "Reset" (per scheda e globale) e "Close"; in fondo `N active filters · M players`.

### Ruoli (utente: campo cliccabile + livello)

Un campo disegnato con le 15 posizioni. Per ogni posizione scelta: "natural" (≥ 18), "accomplished" (≥ 15) o una soglia scelta (1–20). Più posizioni si combinano con "any" (di default) o "all".

### Logica dei filtri (utente: tutti in AND, "any/all" nei gruppi)

Ogni filtro impostato restringe (and). Dentro un gruppo naturale (posizioni, nazioni, tratti) si sceglie "any" o "all". Un cursore lasciato agli estremi non è un filtro.

### Barra a testo (utente: facoltativa e sincronizzata)

- Mostra sempre il filtro corrente come testo: chi guarda impara la sintassi senza doverla studiare.
- Si può scrivere: se il testo è rappresentabile dai controlli della UI, i controlli si allineano; se non lo è (es. un `or` tra campi diversi), i controlli mostrano "advanced filter from the text bar" e restano bloccati finché non si azzera o si torna a un filtro semplice. *(design)*
- Serve una funzione nuova nel dominio, `to_text(spec)`, inversa di `parse`, con la proprietà `parse(to_text(s)) == s` verificata con Hypothesis.

### Tabella e viste di colonne (utente: viste pronte + personalizzabili)

- Viste pronte: General, Technical, Mental, Physical, Goalkeeping, Hidden, Contract, e **Hidden by FM** con CA, PA, hidden e personalità: è quella che serve nei save con il mascheramento degli attributi disattivato (utente). fmsave non dice se un save ha il mascheramento attivo (verificato su fmsave 0.9.3), quindi niente rilevamento automatico.
- Si possono aggiungere e togliere colonne e salvare una vista propria con un nome.
- Modello `QAbstractTableModel` sopra il DataFrame Polars: la vista chiede solo le righe visibili; ordinamento e filtro li fa Polars (spec madre §8).
- Valori mancanti mostrati come `-`, in fondo all'ordinamento (come SP2).

### Scheda del giocatore (utente: testata + schede interne)

- Testata: nome con pulsante "copy name" (negli appunti, per la ricerca di FM), età, club, ruoli, CA e PA.
- Schede: **Attributes** (tre colonne come in FM, colorate per fascia), **Hidden** (hidden e personalità), **Contract** (contratto, valore, clausole, prestito), **Positions** (il campo con i voti per posizione).

### Affidabilità (utente: segno discreto + legenda)

- Icona piccola sulle intestazioni e sui gruppi i cui campi hanno provenienza `unconfirmed`, con un tooltip che spiega; i valori restano leggibili. Quando V1 confermerà dei campi, i segni spariranno da soli (dipendono solo dalla provenienza nello snapshot).
- `estimate` (SP7) avrà uno stile più evidente: il token è previsto già ora.

### Aggiornamento automatico (utente: automatico + pulsante)

- Ogni carriera può essere associata a una **cartella dei save** (o a un file); la scelta si salva nel catalogo.
- Un watcher sulla cartella vede i save nuovi o modificati, aspetta che la dimensione del file resti uguale per qualche secondo, poi importa con `ImportSave` **in un thread separato**; al termine la tabella si ricarica mantenendo filtri, ordinamento e selezione.
- Errori di import mostrati senza bloccare la UI; uno snapshot illeggibile non tocca quelli precedenti (già garantito da SP1).
- Al primo avvio, se non ci sono carriere, l'app propone di sceglierne la cartella; dove possibile propone la cartella standard dei save di FM27 su Windows e su Linux con Proton. *(design)*

### Tema (utente: scuro stile FM; design grafico in SP3b)

Tema scuro neutro, con colori, spaziature, font e fasce di colore degli attributi raccolti in **token** in un solo punto. SP3b cambierà solo i token e il foglio di stile, non i widget.

### Architettura *(design)*

- Nuovo pacchetto `fmxray.ui` (widget, modelli Qt, worker, tema) e entrypoint `fmxray-gui` che chiama solo `bootstrap`.
- Lo stato dei filtri della UI (`FilterState`: valori di cursori, posizioni, caselle) vive fuori dai widget, in Python puro, e si converte in `Spec` e da `Spec`: testabile senza Qt.
- Le viste di colonne e l'associazione carriera → cartella hanno porte in `application` e tabelle nuove nel catalogo SQLite (migrazione 3). Posizione e dimensione delle finestre in `QSettings`.
- `App` (oggi in `cli/commands.py`) si sposta in `application`, così `cli` e `ui` usano la stessa composizione di `bootstrap`.

## Da verificare nel piano (documentazione, niente API indovinate)

- PySide6 6.12.0 su Python 3.14: PyPI lo dichiara (classifier 3.14, wheel abi3 da cp310).
- pytest-qt 4.5.0 su Python 3.14: PyPI dichiara fino alla 3.13 (pacchetto puro Python): provarlo prima di contarci.
- Test Qt in CI su Linux senza schermo (`QT_QPA_PLATFORM=offscreen` o equivalente) e su Windows.
- `QFileSystemWatcher` con file scritti a pezzi su Windows e su Linux (cartella di Proton).
- Cartella standard dei save di FM27 su Windows (su Linux con Proton è nota dal save dell'utente).

### Scelte di Claude da controllare

- **Nazioni per codice:** il save dà solo `nation_id`; in SP3 il filtro sulle nazioni mostra i codici, i nomi arrivano con la mappa `database_id → nome` (idea già nella spec madre, da collocare in un SP successivo).
- **"Export CSV"** esporta tutte le righe che soddisfano il filtro corrente, con le colonne della vista attiva.
- **Watcher:** si sorveglia solo la cartella della carriera aperta.
- **Mappa del popup:** la tabella delle sottoschede qui sopra è mia (l'utente ha fissato la struttura a schede e blocchi).

## Lasciato a chi costruisce

- Nomi delle classi e dei segnali Qt, divisione in moduli dentro `ui`.
- Ritardo esatto prima di applicare un filtro mentre si trascina un cursore, e tempo di stabilità del file prima dell'import.
- Disposizione interna dei blocchi in ogni scheda del popup.

## Criteri di successo

1. Con il save reale dell'utente, l'app mostra tutti i giocatori e risponde a filtri e ordinamenti senza blocchi percepibili, su Linux e su Windows.
2. Età < 22 e PA > 180 impostati **dai controlli** restituiscono gli stessi giocatori del test di integrazione di SP2.
3. Quando FM salva nella cartella associata, la tabella si aggiorna senza azioni dell'utente.
4. Ogni campo del catalogo e ogni campo calcolato è filtrabile dal popup (test sul catalogo).
5. Barra a testo e controlli restano allineati; `parse(to_text(s)) == s` (Hypothesis).
6. I campi `unconfirmed` sono riconoscibili; con nessun campo `unconfirmed` i segni spariscono.
7. ruff, mypy, lint-imports (con il contratto di `ui`) e CI verdi su Linux e Windows; wiki aggiornata.
