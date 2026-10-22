"""Web backend for the Shithead card game.

Players connect over a WebSocket at /ws, join a queue for a 2-4 player game,
and the server runs the game with the existing Game.py rules engine.
Every message is JSON. After each move the server pushes a fresh state to every player,
and each player only sees what they are allowed to see (their own hand, not the others').

Run locally:  uvicorn main:app --reload   (from inside the backend/ folder)
"""
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Game.py, Cards.py and Player.py live one folder up, shared with the desktop version
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from Game import Game  # noqa: E402

app = FastAPI(title="Shithead Card Game")

# Players waiting for a game, by requested game size: {2: [(name, websocket), ...], ...}
waiting_queues = {2: [], 3: [], 4: []}

# All running games: {room_id: Room}
rooms = {}

# Everything runs on one asyncio event loop, so code between two `await`s never
# runs at the same time as other code. That's why no locks are needed (unlike server.py).


class Room:
    def __init__(self, players):
        self.id = str(uuid.uuid4())
        self.sockets = {}  # name -> websocket
        self.message = ""
        self.game = Game()

        for name, ws in players:
            self.game.add_player(name)
            self.sockets[name] = ws
        self.game.deal_cards()

        first = self.game.get_setup_player()
        self.message = f"{first.name}, choose 3 face-up cards."

    async def broadcast_state(self):
        for name, ws in list(self.sockets.items()):
            try:
                await ws.send_json(state_for(self, name))
            except Exception:
                pass  # this player disconnected; their own handler will clean up


# -----------------------------
# JSON views of the game
# -----------------------------
def card_json(card):
    return {"value": card.value, "suit": card.suit}


def find_player(game, name):
    """Find a player by name. Finished players are removed from game.Players, so this can return None."""
    for player in game.Players:
        if player.name == name:
            return player
    return None


def turn_name(game):
    """Name of the player whose turn it is (setup or playing), or None."""
    if game.state == "setup":
        player = game.get_setup_player()
    elif game.state == "playing":
        player = game.get_current_player()
    else:
        player = None
    return player.name if player else None


def state_for(room, name):
    """The game state as seen by one player: own hand visible, other hands hidden."""
    game = room.game
    me = find_player(game, name)

    players = []
    for player in game.Players:
        players.append({
            "name": player.name,
            "hand_count": len(player.hand),
            "face_up": [card_json(c) for c in player.face_up],
            "face_down_count": len(player.face_down),
        })

    is_setup_player = game.state == "setup" and turn_name(game) == name

    return {
        "type": "state",
        "you": name,
        "state": game.state,  # setup / playing / game_over
        "turn": turn_name(game),
        "message": room.message,
        "pile": [card_json(c) for c in game.current_pile],
        "deck_count": len(game.current_deck.deck),
        "burned_count": len(game.trash),
        "players": players,
        "hand": [card_json(c) for c in me.hand] if me else [],
        "active_zone": me.active_cards()[1] if me else None,
        "selected": list(game.selected_indices) if is_setup_player else [],
        "finish_order": list(game.finish_order),
    }


# -----------------------------
# Handling player actions
# -----------------------------
def is_index(value):
    return isinstance(value, int) and not isinstance(value, bool)


def apply_action(game, name, msg):
    """Validate and apply one action from a player. Returns (ok, message) like Game's methods."""
    action = msg.get("type")

    if game.state == "game_over":
        return False, "The game is over."

    if turn_name(game) != name:
        return False, "It's not your turn."

    if game.state == "setup":
        if action == "setup_toggle":
            if not is_index(msg.get("index")):
                return False, "Invalid card index."
            return game.toggle_setup_card(msg["index"])
        if action == "setup_confirm":
            return game.confirm_setup_selection()
        return False, "During setup you can only choose your face-up cards."

    # state == "playing"
    player = game.get_current_player()
    _, active_zone = player.active_cards()

    if action == "play":
        zone = msg.get("zone")
        indices = msg.get("indices")
        if not isinstance(indices, list) or not indices or not all(is_index(i) for i in indices):
            return False, "Invalid card indices."
        # Block playing the same card twice, e.g. indices [0, 0]
        if len(set(indices)) != len(indices):
            return False, "Each card can only be played once."
        # Game.play_selected_cards doesn't check this itself
        if zone != active_zone:
            return False, "You can only play from your active zone."
        return game.play_selected_cards(zone, indices)

    if action == "play_face_down":
        if not is_index(msg.get("index")):
            return False, "Invalid card index."
        return game.handle_card_click("face_down", msg["index"])

    if action == "take_pile":
        return game.take_pile_by_choice()

    return False, f"Unknown action: {action}"


def auto_pickup(game):
    """If the current player has no legal move, they pick up the pile automatically (same as server.py)."""
    if game.state != "playing" or not game.current_pile:
        return None
    player = game.get_current_player()
    if game.can_player_play_any(player):
        return None
    game.pickup_pile(player)
    game.advance_turn()
    return f"{player.name} couldn't play and picked up the pile."


# -----------------------------
# Matchmaking
# -----------------------------
def unique_name(requested):
    """Clean up the requested name and make sure no one waiting or playing already uses it."""
    base = requested.strip()[:20] if isinstance(requested, str) else ""
    base = base or "Player"
    taken = {n for queue in waiting_queues.values() for n, _ in queue}
    for room in rooms.values():
        taken.update(room.sockets)
    name, i = base, 2
    while name in taken:
        name = f"{base} {i}"
        i += 1
    return name


async def join_queue(ws, name, size):
    """Add a player to the queue. Returns the new Room if this player filled it, else None."""
    queue = waiting_queues[size]
    queue.append((name, ws))

    if len(queue) < size:
        for _, other in queue:
            await other.send_json({"type": "waiting", "joined": len(queue), "needed": size})
        return None

    room = Room(queue[:size])
    rooms[room.id] = room
    del queue[:size]
    await room.broadcast_state()
    return room


def find_room(name):
    for room in rooms.values():
        if name in room.sockets:
            return room
    return None


async def handle_disconnect(name):
    for queue in waiting_queues.values():
        queue[:] = [(n, ws) for n, ws in queue if n != name]

    room = find_room(name)
    if room is None:
        return
    del room.sockets[name]
    if room.game.state != "game_over":
        room.game.state = "game_over"
        room.message = f"{name} left the game."
    await room.broadcast_state()
    if not room.sockets:
        del rooms[room.id]


# -----------------------------
# Endpoints
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    name = None
    try:
        # The first message must be: {"type": "join", "name": "...", "players": 2|3|4}
        join = await ws.receive_json()
        if not isinstance(join, dict) or join.get("type") != "join" or join.get("players") not in waiting_queues:
            await ws.send_json({"type": "error", "message": 'First send {"type": "join", "players": 2|3|4}.'})
            await ws.close()
            return

        name = unique_name(join.get("name"))
        await ws.send_json({"type": "joined", "you": name})
        await join_queue(ws, name, join["players"])

        while True:
            msg = await ws.receive_json()
            room = find_room(name)
            if room is None:
                await ws.send_json({"type": "error", "message": "Still waiting for players."})
                continue
            if not isinstance(msg, dict):
                await ws.send_json({"type": "error", "message": "Messages must be JSON objects."})
                continue

            ok, text = apply_action(room.game, name, msg)
            if not ok:
                await ws.send_json({"type": "error", "message": text})
                continue

            pickup = auto_pickup(room.game)
            room.message = f"{text} {pickup}" if pickup else text
            await room.broadcast_state()

    except WebSocketDisconnect:
        pass
    except ValueError:
        # receive_json got something that isn't valid JSON
        await ws.close(code=1003)
    finally:
        if name:
            await handle_disconnect(name)
