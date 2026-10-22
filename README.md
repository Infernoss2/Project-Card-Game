# 🃏 Shithead Card Game

## 📌 Overview
A Python implementation of **Shithead** (also known as Palace / Karma) for 2–4 players,
built with object-oriented design. The project is being extended from a desktop game
into a **browser game anyone can play from a link**.

---

## 🗂️ Project Structure

```
Project-Card-Game/
├── Game.py, Cards.py, Player.py   # Rules engine, deck, player zones (shared by both versions)
├── server.py, network.py          # Desktop version: socket server + client networking
├── game_gui.py                    # Desktop version: pygame UI
├── backend/                       # Web version: FastAPI + WebSocket server
│   ├── main.py
│   └── requirements.txt
└── web/                           # Web version: HTML + JavaScript frontend
    ├── index.html                 # Screens: menu, waiting room, card table, results
    ├── style.css                  # Card-table design, responsive down to phone size
    ├── app.js                     # Draws the state from the server, sends player actions
    └── config.js                  # Backend URL (local vs deployed)
```

---

## 🌐 Web Version Architecture

| Piece    | Tech                          | Hosted on |
|----------|-------------------------------|-----------|
| Frontend | HTML + JavaScript             | Netlify   |
| Backend  | FastAPI + WebSockets, JSON    | Render    |

The browser connects to the backend over a WebSocket. The backend runs the game using
the existing `Game.py` rules engine and pushes state updates to every player.

---

## 🚀 Running Locally (web version)

**Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Check it works: open http://127.0.0.1:8000/health → `{"status": "ok"}`

**Tests** (from `backend/`)
```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## 📡 WebSocket Protocol

Connect to `ws://<host>/ws`. All messages are JSON.

**Client → server**

| Message | When |
|---------|------|
| `{"type": "join", "name": "Sagi", "players": 2}` | First message. `players` is 2, 3 or 4 |
| `{"type": "setup_toggle", "index": 0}` | Setup: select / unselect a hand card as face-up |
| `{"type": "setup_confirm"}` | Setup: confirm the 3 selected cards |
| `{"type": "play", "zone": "hand", "indices": [0, 2]}` | Play cards of the same value from `hand` or `face_up` |
| `{"type": "play_face_down", "index": 1}` | Flip and play a face-down card |
| `{"type": "take_pile"}` | Pick up the pile |

**Server → client**

| Message | Meaning |
|---------|---------|
| `{"type": "joined", "you": "Sagi"}` | Your name in the game (made unique if taken) |
| `{"type": "waiting", "joined": 1, "needed": 2}` | Waiting for more players |
| `{"type": "state", ...}` | Full game state from your point of view — sent to everyone after every move |
| `{"type": "error", "message": "..."}` | Your last action was rejected (only sent to you) |

The `state` message contains your own `hand`, but only counts for other players' hands,
so players can't see each other's cards.

**Frontend** (in a second terminal, from the project root)
```bash
python3 -m http.server 5500 --directory web
```
Open http://localhost:5500 in two browser tabs, join a 2-player game in each, and play.
`web/config.js` picks the backend URL: `ws://localhost:8000/ws` when running locally.

---

## 🎮 Game Rules (Simplified)
- Each player gets face-down cards, face-up cards, and a hand.
- Players take turns playing a card equal to or higher than the top of the pile.
- Special cards:
  - **2** — can be played on anything, resets the pile
  - **3** — can be played on anything, transparent (the next player plays on the card below it)
  - **7** — the next card must be 7 or lower
  - **8** — skips the next player
  - **10** — can be played on anything, burns the pile (play again)
  - **Q** — blocks the wild cards: 2, 3 and 10 can't be played on it
- Four of the same value in a row also burns the pile.
- If you can't play, you pick up the pile.
- First to get rid of all their cards wins — the last player left is the *Shithead*.

---

## 🚧 Status
- [x] Desktop version (pygame + sockets)
- [x] Phase 1 — Web project structure
- [x] Phase 2 — WebSocket backend
- [x] Phase 3 — Browser frontend
- [ ] Phase 4 — Local 2-player test
- [ ] Phase 5 — Deploy (Render + Netlify)
- [ ] Phase 6 — Polish (demo GIF, architecture diagram)
