"""Web backend for the Shithead card game.

Phase 1: skeleton only. Phase 2 adds the WebSocket game server that reuses Game.py.
Run locally:  uvicorn main:app --reload   (from inside the backend/ folder)
"""
from fastapi import FastAPI

app = FastAPI(title="Shithead Card Game")


@app.get("/health")
def health():
    return {"status": "ok"}
