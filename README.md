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
    └── index.html
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

**Frontend**
Open `web/index.html` in a browser.

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
- [ ] Phase 2 — WebSocket backend
- [ ] Phase 3 — Browser frontend
- [ ] Phase 4 — Local 2-player test
- [ ] Phase 5 — Deploy (Render + Netlify)
- [ ] Phase 6 — Polish (demo GIF, architecture diagram)
