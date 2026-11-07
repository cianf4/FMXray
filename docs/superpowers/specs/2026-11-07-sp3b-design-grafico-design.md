# SP3b — Design grafico e riordino dello schermo: design

> Sottoprogetto 3b della [spec madre](2026-11-03-fm-x-ray-design.md) (§12, D24), dopo [SP3](2026-11-06-sp3-interfaccia-design.md). Decisioni prese con l'utente il 2026-11-07 (due blocchi di domande a scelta multipla). Dopo l'approvazione: `superpowers:writing-plans` → `docs/superpowers/plans/2026-11-07-sp3b-design-grafico.md` → `superpowers:executing-plans` con TDD.

## Intento

L'app di SP3 funziona e all'utente piace, ma a schermo c'è troppo insieme: la colonna a sinistra con ricerche salvate e viste occupa spazio, e la riga dei filtri sembra disordinata e non fa capire che il popup ne contiene moltissimi altri. SP3b mette ordine (cosa si vede subito, cosa resta a un click) e poi dà all'app il suo aspetto definitivo, scelto tra tre proposte.

## Obiettivi

1. Riordino della finestra: meno righe sopra la tabella, viste di colonne in un posto naturale, ricerche salvate in una barra laterale richiudibile, scheda compatta.
2. Tre proposte di stile della stessa schermata come mockup nel browser: una di Claude, una con la skill **impeccable**, una con la skill **taste-skill**; ognuna sceglie la propria direzione (utente: "decidi tu per proposta").
3. Lo stile scelto (o un mix indicato dall'utente) applicato ai token e al foglio di stile dell'app.
4. Densità della tabella **media** di default, con un'opzione **compatta** a un click.
5. Numeri leggibili a colpo d'occhio e animazioni leggere.

## Non obiettivi

- Funzioni nuove di ricerca o di dati (restano quelle di SP3).
- Bandiere e nomi delle nazioni (servono le mappe `database_id → nome`, sottoprogetto successivo).
- Tema chiaro (idea per dopo nella spec madre).
- Icone dei tratti o dei ruoli disegnate su misura.

## Anti-obiettivi

- Perdere una funzione di SP3 nel riordino (filtri, barra a testo, ricerche salvate, viste, export, watcher).
- Un mockup che non si può riprodurre con i fogli di stile Qt: la proposta scelta deve diventare l'app vera, non restare un'immagine.
- Animazioni che rallentano il lavoro (ogni animazione dura poco e non blocca l'input).
- Colori nei widget fuori da `ui/theme.py`.

## Vincoli

- Valgono i Global Constraints di SP1–SP3 (Python 3.14, PySide6 6.12.0, nessuna installazione o commit da parte di Claude, niente segnaposti nei comandi, niente attribuzioni a Claude).
- **Nessuna dipendenza nuova** (né Python né font da scaricare nel repo): font di sistema con fallback.
- I mockup HTML usano solo ciò che Qt Style Sheets sa rendere: colori, bordi, raggi, padding, font, gradienti semplici. Niente ombre sfumate, filtri, transizioni CSS, layout che Qt Widgets non riproduce.
- Le animazioni usano le classi di animazione di Qt (`QPropertyAnimation` o equivalenti), durata breve; i test non dipendono dal loro tempo.
- Interfaccia in inglese con `tr()`.

## Decisioni

### Riordino (utente)

- **Viste di colonne:** fuori dalla colonna sinistra; *(proposta di Claude, da confermare nei mockup)* una fila di linguette sopra la tabella (General · Technical · Mental · Physical · Goalkeeping · Hidden · Contract · Hidden by FM · viste dell'utente · `+` per salvare la vista corrente), come le viste di FM.
- **Ricerche salvate:** barra laterale **richiudibile**, stretta di default, con il numero dei nuovi visibile anche da chiusa.
- **Barra a testo:** **nascosta**, si apre a richiesta (icona e scorciatoia da tastiera); il filtro corrente resta visibile in forma compatta.
- **Filtri:** la riga dei filtri deve far capire che ce ne sono molti altri; *(proposta di Claude)* "All filters" diventa il pulsante principale con il numero dei filtri attivi, i filtri attivi compaiono come chip rimovibili, i filtri rapidi restano pochi. La forma esatta la decidono i mockup.
- **Scheda del giocatore:** **sempre visibile ma più compatta** (testata corta: nome con "copy name", età, club, ruoli, CA e PA in evidenza; il resto nelle schede interne).

### Stile (utente)

- Tre proposte, ciascuna con una direzione propria. Si confrontano come **mockup statici nel browser** della stessa schermata (finestra principale con tabella, barra laterale, scheda e popup dei filtri aperto); poi la scelta si applica all'app e l'utente la prova lì.
- Priorità: **leggibilità dei numeri** (attributi, CA/PA, soldi allineati e distinguibili; fasce di colore degli attributi) e **animazioni leggere** (apertura/chiusura della barra laterale, comparsa del popup, cambio di giocatore nella scheda).
- Tabella **media** di default; **compatta** con un pulsante o voce di menu, scelta ricordata tra un avvio e l'altro.

### Ordine di lavoro *(design)*

1. **Mockup:** le tre proposte mostrano già il layout riordinato; nomi e numeri inventati (niente dati del gioco). L'utente sceglie: è un punto di arresto del piano.
2. **Riordino** nel codice (viste a linguette, barra laterale, barra a testo a richiesta, chip dei filtri, scheda compatta) con i test aggiornati.
3. **Stile:** token e foglio di stile della proposta scelta, densità media/compatta, animazioni.
4. Prova dell'utente nell'app, wiki, PR.

## Lasciato a chi costruisce

- Direzione di ognuna delle tre proposte, palette, font di sistema e spaziature.
- Scorciatoia esatta della barra a testo, durata delle animazioni (breve), dove sta il pulsante della densità.
- Come si ricorda la densità (`QSettings`).

## Criteri di successo

1. Sopra la tabella al massimo due righe con la barra a testo chiusa; nessuna funzione di SP3 persa (i test di SP3 restano verdi, aggiornati solo dove cambia il layout).
2. Tre mockup affiancati nel browser; l'utente ne sceglie uno (o un mix).
3. L'app con lo stile scelto rispecchia il mockup; tutti i colori vengono da `ui/theme.py`.
4. Il passaggio media/compatta cambia l'altezza delle righe e resta dopo il riavvio.
5. Le animazioni non rallentano: la barra laterale si apre e chiude e la scheda cambia giocatore senza ritardi percepibili.
6. ruff, mypy, lint-imports e CI verdi; wiki aggiornata.
