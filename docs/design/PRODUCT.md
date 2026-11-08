# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

Desktop app in PySide6 (Qt Widgets) for Windows and Linux; design proposals are HTML mockups limited to what Qt Style Sheets can render.

## Users
One person, the developer-player: a Football Manager 27 player who runs a single-player career and keeps FM X-Ray open on a second monitor while FM is on the first. The job: find players worth signing or watching by filtering the whole database, including values FM hides.

## Product Purpose
FM X-Ray reads FM save files locally, in read-only mode, and shows every player with every field, including Current Ability (CA), Potential Ability (PA) and hidden attributes. Success: a search like "under 22, PA above 180, natural centre-back" answers in a blink, and the table updates by itself when FM saves.

## Positioning
Reads the save on disk instead of the game's memory, so it is open source, runs on Linux under Proton as well as Windows, and never touches the running game.

## Operating Context
Used during a career session, glanced at between matches and transfer windows, next to FM's own dark interface. Data volume: about 126,000 players per save. Values are copied by name into FM's own search.

## Capabilities and Constraints
- Filters on any field (popup with tabs, clickable pitch for positions, quick filters, optional text bar), saved searches with "new since last snapshot", column views, CSV export, automatic import when FM saves.
- Read-only; no network; no Sports Interactive / SEGA data in the repository.
- Interface text in English. Money is in the save's internal unit (not euros yet). Most fields are marked "unconfirmed" on FM27 until verified.

## Evidence on Hand
No real game data may appear in design work: mockups use invented names and numbers.

## Product Principles
- The table is the product: everything else serves finding and reading players.
- Numbers first: attributes, CA/PA and money must read at a glance.
- Never claim certainty the data does not have (unconfirmed and estimated values stay recognisable).
- Calm next to FM: the second screen must not compete with the game.
