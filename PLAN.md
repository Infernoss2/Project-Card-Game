# Project Card Game — Web Version Plan

> Working notes for turning the desktop game into a browser game anyone can play via a link.
> Pick this up in a new session started **inside this directory** (`~/Project-Card-Game`).

## Where things are
- **Real code (use this):** `~/Project-Card-Game` — owned by me, 25-commit history, full game.
- **GitHub source of truth:** `github.com/Infernoss2/Project-Card-Game` (friend's repo, I'm sole contributor).
- **Deleted trash:** `/home/sagib_Linux/Shited/` was a broken, root-owned, near-empty clone. Remove it (see repo chat / command below). Not part of this project.

## What the project is
"Shithead" (Palace/Karma) card game, 2–4 players, Python.
- `Game.py` — rules engine (turns, special cards 2/5/6/8/10, 4-of-a-kind burns, setup, win order). **Good, reusable.**
- `Cards.py`, `Player.py` — deck + player zones (hand / face-up / face-down). Reusable.
- `server.py` — socket server + matchmaking (binds `127.0.0.1` = localhost only).
- `network.py` — client networking (hardcoded `127.0.0.1`).
- `game_gui.py` — **pygame desktop UI** (will be replaced).
- `client.py`, `test_game.py` — stale leftover scripts, ignore/remove.

## The goal
Anyone clicks a link and plays in the browser — like my `Whist_calculator` on Netlify.
This needs TWO hosted pieces (Netlify alone can't do it — it only serves static files):

| Piece | Rewrite | Hosts on |
|-------|---------|----------|
| Frontend (UI) | pygame → **HTML + JavaScript** | **Netlify** |
| Backend (server) | sockets + **pickle** → **WebSockets + JSON** | **Render / Railway / Fly.io** (free tier) |

`Game.py` logic is reused almost unchanged. The UI and networking plumbing get rewritten.

## Known issues to fix during the rewrite
- Server binds to `127.0.0.1` → must be `0.0.0.0` + configurable host.
- `pickle` over the network = remote code execution risk → replace with **JSON**.
- GUI polls the server every frame (60x/sec) → WebSockets push instead.

## Stages (do in order, on a branch)
Work on a branch `web-version`; keep `main` (the working desktop game) safe.

1. **Setup** — create `web-version` branch, add project structure (`/web` frontend, `/backend` server), README.
2. **Backend** — WebSocket server (Python `websockets` or FastAPI), JSON messages, reuse `Game.py`. Run locally.
3. **Frontend** — HTML/JS board: menu → waiting room → play. Talks to backend over WebSocket.
4. **Wire + test** — full 2-player game in two browser tabs locally.
5. **Deploy** — backend to Render, frontend to Netlify, point frontend at the live backend URL.
6. **Polish** — README with demo GIF + architecture diagram (for CV/LinkedIn).

## Open questions for next session
- Confirm backend framework (plain `websockets` lib vs FastAPI — recommend FastAPI for CV value).
- Decide whether to push `web-version` to GitHub early (backup) or keep local until Stage 4.

## Git note
Nothing is pushed to GitHub until I review and approve. Branches live locally first.
