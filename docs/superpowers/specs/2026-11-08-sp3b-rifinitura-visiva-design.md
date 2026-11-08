# SP3b — Rifinitura visiva: design

> Seconda parte di SP3b, dopo la [spec del design grafico](2026-11-07-sp3b-design-grafico-design.md). Stesso branch `feat/sp3b-design` e stessa PR, ancora da aprire. Decisioni prese con l'utente il 2026-11-08, dopo la prova dell'app (un blocco di domande a scelta multipla con anteprima). Dopo l'approvazione: `superpowers:writing-plans` → `docs/superpowers/plans/2026-11-08-sp3b-rifinitura-visiva.md` → `superpowers:executing-plans` con TDD.

## Intento

L'utente ha provato l'app di SP3b ed era deluso:

- a schermo intero restava uno spazio vuoto tra la tabella e la scheda;
- colori e stile non sembravano quelli del mockup;
- i font sembravano "pixelati";
- le animazioni scattavano.

Ha chiesto cose belle da vedere, anche con librerie esterne, l'azzurro acceso del mockup C, più abbellimenti in generale e un esagono degli attributi nella scheda del giocatore.

Le cause, trovate con uno screenshot a 1920 px e la lettura del codice:

- **Spazio vuoto:** le colonne della tabella hanno larghezza fissa, finiscono a circa 860 px e lasciano fondo vuoto fino alla scheda. Intanto nomi e club sono troncati.
- **Look lontano dal mockup:**
  - nessun pannello: tutto è piatto sullo stesso fondo;
  - soldi lunghi e troncati;
  - fasce di colore degli attributi solo nella scheda;
  - filtri rapidi minimo-massimo che occupano mezza riga.
- **Il blu:** è lo stesso `#4a8ad6` di C, ma su fondo blu-ardesia sembra spento.
- **Font:** Qt non legge l'ingrandimento del testo di GNOME (115% sul PC dell'utente). Figtree a 10pt, cioè circa 13 px su uno schermo da 16" 1920×1200, è sottile e sgranato.
- **Animazioni:** sono le scelte di SP3b a rallentarle:
  - `HoverFade` cambia il foglio di stile di un pulsante circa 60 volte in 150 ms;
  - la barra laterale anima la propria larghezza dentro il layout, quindi Qt ridispone tutta la finestra (con la tabella da 126.000 righe) a ogni passo;
  - la scheda ha un `QGraphicsOpacityEffect` sempre attivo, che la ridisegna fuori schermo a ogni aggiornamento.

## Obiettivi

1. La tabella riempie lo spazio disponibile a ogni larghezza della finestra.
2. Il look del mockup, ma su fondo nero neutro e con accento azzurro acceso: pannelli con angoli arrotondati, numeri leggibili, colori degli attributi anche nella tabella.
3. Testo nitido.
4. Una scheda del giocatore bella da vedere, con l'esagono delle aree e animazioni fluide.
5. Animazioni nel resto dell'app che non scattano.

## Non obiettivi

- Portare in Qt Quick il resto della finestra (tabella, filtri, popup): resta in Qt Widgets, solo restilizzato.
- Funzioni nuove di ricerca o di dati.
- Confronto tra due giocatori sull'esagono, esagono per ruolo, tema chiaro.
- Bandiere delle nazioni.

## Anti-obiettivi

- Perdere una funzione della scheda attuale:
  - copia del nome;
  - tutti gli attributi, i nascosti, la personalità, il contratto, i piedi e i ruoli sul campo;
  - la nota sui valori non confermati.
- Colori scritti dentro i file QML o nei widget: vengono tutti dai token di `ui/theme.py`.
- Animazioni che bloccano l'input o ritardano la comparsa dei dati: il valore giusto è leggibile subito, l'animazione è solo la transizione.
- Un esagono che inventa precisione: è la media di attributi visibili, è un valore derivato e lo dice.

## Vincoli

- **Regole di SP1–SP3b:** Python 3.14, PySide6 6.12.0, pytest-qt 4.5.0. Niente installazioni, commit o push da parte di Claude, niente segnaposti nei comandi, niente attribuzioni a Claude.
- **Nessuna dipendenza Python nuova.** Qt Quick, QtQuick.Shapes e QtQuick.Effects (`MultiEffect`) sono già in PySide6 6.12.0. Verificato il 2026-11-08: un `QQuickWidget` con `Shape` e `MultiEffect` carica senza errori ed è disegnato anche con `QT_QPA_PLATFORM=offscreen`, quindi i test girano senza schermo.
- **Font, cambiato dall'utente:**
  - **Inter** variabile (OFL) al posto di Figtree, dal repository google/fonts (`ofl/inter/Inter[opsz,wght].ttf` e `ofl/inter/OFL.txt`, verificati raggiungibili);
  - JetBrains Mono resta per i numeri;
  - Figtree e la sua licenza escono dal pacchetto.
- **Architettura esagonale:**
  - il calcolo delle aree dell'esagono è logica di gioco: sta in `domain`, in Python puro, testato da solo;
  - la UI lo chiama e basta;
  - i file QML stanno nel pacchetto (`src/fmxray/ui/qml/`) e finiscono nel wheel.
- **Test:** non dipendono dalla durata delle animazioni.

## Decisioni

### Dell'utente (2026-11-08)

- **Accento `#3ea6ff`** (azzurro acceso), con testo scuro sui pulsanti pieni. Fondo nero neutro come nel mockup C.
- **Esagono a 6 aree di gioco:** Attacco, Tecnica, Creatività, Difesa, Fisico, Mentale. Ogni area è la media dei suoi attributi, da 1 a 20. I portieri hanno 6 aree proprie.
- **Scheda del giocatore in Qt Quick (QML)** dentro la finestra a widget (`QQuickWidget`): animazioni sulla GPU, ombre e forme. Il resto dell'interfaccia resta in widget.
- **Testo:** Inter a 11pt.

### Di Claude (da controllare leggendo)

**Token nuovi:**

| Token | Valore | Token | Valore |
| --- | --- | --- | --- |
| background | `#0e0f12` | primary_text | `#06223a` |
| surface (pannelli) | `#16181d` | selection | `#163450` |
| raised | `#1f2228` | chip_background / chip_text | `#15314a` / `#bfe1ff` |
| border | `#272a31` | new | `#3ea6ff` |
| text / text_muted | `#eef1f5` / `#8f97a6` | font_text / font_size | Inter / 11pt |
| accent / primary | `#3ea6ff` | row height medium / compact | 30 / 24 |

- Le fasce degli attributi restano quelle di SP3b.
- Il raggio dei controlli resta 6, i pannelli hanno raggio 10.

**Aree dell'esagono**, ognuna la media degli attributi presenti, con un decimale:

| Area | Giocatori di movimento |
| --- | --- |
| Attack | finishing, off_the_ball, long_shots, heading |
| Technique | first_touch, technique, dribbling, passing |
| Creativity | vision, flair, decisions, crossing |
| Defence | marking, tackling, positioning, anticipation |
| Physical | pace, acceleration, strength, stamina, agility, balance |
| Mental | determination, work_rate, teamwork, concentration, composure, bravery |

| Area | Portieri (`GK` tra i ruoli naturali) |
| --- | --- |
| Shot stopping | reflexes, handling, one_on_ones |
| Aerial | aerial_reach, command_of_area, punching, jumping_reach |
| Sweeping | rushing_out, anticipation, acceleration |
| Distribution | kicking, throwing, passing, first_touch |
| Physical | agility, strength, balance, stamina |
| Mental | concentration, composure, decisions, positioning, communication |

- Un'area senza nessun attributo noto vale "nessun valore": nell'esagono va al centro, accanto c'è "-".
- Le aree hanno provenienza `derived`.

**Tabella:**
- **Colonne:** dopo ogni nuovo risultato le colonne si adattano al contenuto (con la precisione di Qt, circa 1000 righe) e la colonna Name prende lo spazio che resta. Se non c'è Name, lo prende l'ultima colonna.
- **Soldi in forma compatta:** colonne con unità `MONEY_INTERNAL`, scritti `4.2M`, `950K`, `12.5K`; sotto 1000 il numero com'è. Il valore completo con i separatori è nel tooltip.
- **Attributi 1–20 come pillole:** un riquadro arrotondato tinto con il colore della fascia, testo pieno, disegnato da un delegato.
- **Riga sotto il mouse:** evidenziata.
- **Pannello:** tabella e linguette delle viste stanno in un pannello con angoli arrotondati.

**Finestra:**
- Le due righe in alto restano senza pannello, sul fondo.
- La tabella e la scheda sono due pannelli separati da 10 px.

**Filtri rapidi:** Age resta min–max in due campi stretti. CA e PA diventano un solo campo "min" ("CA ≥", "PA ≥"). Il popup "All filters" mantiene gli intervalli completi.

**Scheda in QML (larghezza minima 320 px), dall'alto:**
- **Testata:**
  - cerchio con le iniziali, nome, pulsante copia;
  - "età · club · ruoli";
  - CA e PA grandi, PA in azzurro;
  - una barra da 0 a 200: la parte piena arriva al CA, la parte tenue continua fino al PA;
  - la scritta "room to grow N" con N = PA − CA.
- **Esagono delle 6 aree:**
  - griglia a tre anelli (cioè 1/3, 2/3 e 3/3 di 20);
  - poligono pieno azzurro trasparente con il bordo azzurro;
  - etichette con il valore.
- **Linguette Attributes / Hidden / Contract / Positions:**
  - stessi contenuti di oggi;
  - numeri in JetBrains Mono, colorati per fascia;
  - i ruoli su un piccolo campo disegnato in QML.
- **Nota non confermati:** una sola riga "values not yet confirmed ⓘ" in fondo se qualche campo mostrato non è confermato; prende il posto della ⓘ su ogni gruppo (era un problema minore rimandato).
- **Ombra:** il pannello della scheda ha un'ombra morbida (`MultiEffect`).
- **Animazioni al cambio di giocatore** (sulla GPU, 250 ms, OutCubic): il poligono passa dal vecchio al nuovo profilo, CA e PA scorrono fino al nuovo valore, la barra si allunga o si accorcia.
- **Scheda vuota:** dice "Select a player".

**Ponte Python ↔ QML:**
- `PlayerCard` resta un `QWidget` con la stessa interfaccia di oggi: `show_player(meta, values)`, `clear()`, `copy_button` → `copy_name()`. Così la finestra principale non cambia.
- Dentro, un oggetto Python con proprietà (`CardModel`) prepara i testi, i colori e le aree. Il QML li mostra e basta.
- I test controllano `CardModel` e il caricamento del QML senza errori, non i pixel.

**Animazioni del resto dell'app:**
- `HoverFade` sparisce e il passaggio del mouse lo fa il foglio di stile (`:hover`).
- La barra delle ricerche salvate da aperta si sovrappone alla tabella: la sua apertura anima la geometria di un pannello sopra la tabella, non la larghezza dentro il layout, quindi la tabella non viene ridisposta.
- `grow_in` dei chip e `fade_in` del popup restano.

## Cosa resta a chi costruisce

- Struttura interna dei file QML (componenti separati per esagono, griglia attributi, campo).
- Come passare i token al QML (proprietà di contesto o oggetto `Theme`), purché vengano da `TOKENS`.
- Disposizione dei ruoli sul campo QML (ricavata da quella di `PitchWidget`).
