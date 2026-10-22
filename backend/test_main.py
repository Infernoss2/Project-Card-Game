"""Tests for the WebSocket backend. Run from backend/:  pytest -v"""
import random
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def join(ws, name, players=2):
    ws.send_json({"type": "join", "name": name, "players": players})
    joined = ws.receive_json()
    assert joined["type"] == "joined"
    return joined["you"]


def start_game(stack, names):
    """Connect len(names) players, return [(ws, name, first_state), ...]."""
    sockets = []
    for name in names:
        ws = stack.enter_context(client.websocket_connect("/ws"))
        you = join(ws, name, players=len(names))
        sockets.append([ws, you])

    # Everyone except the last player got a "waiting" message for each player who joined after them
    for i, (ws, _) in enumerate(sockets[:-1]):
        for _ in range(len(names) - 1 - i):
            assert ws.receive_json()["type"] == "waiting"

    return [(ws, you, ws.receive_json()) for ws, you in sockets]


def act(players, actor_ws, msg):
    """Send an action. Returns ("error", text) or ("state", {name: state}) after everyone got the update."""
    actor_ws.send_json(msg)
    reply = actor_ws.receive_json()
    if reply["type"] == "error":
        return "error", reply["message"]
    states = {reply["you"]: reply}
    for ws, name in players:
        if ws is not actor_ws:
            states[name] = ws.receive_json()
    return "state", states


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_join_requires_valid_player_count():
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "join", "players": 7})
        assert ws.receive_json()["type"] == "error"


def test_game_starts_in_setup_and_hides_other_hands():
    with ExitStack() as stack:
        (_, alice, a_state), (_, bob, b_state) = start_game(stack, ["Alice", "Bob"])

        assert a_state["state"] == "setup"
        assert a_state["turn"] == alice
        assert len(a_state["hand"]) == 6
        # Each player sees only their own hand; others are just counts
        assert a_state["hand"] != b_state["hand"]
        for p in a_state["players"]:
            assert "hand" not in p
            assert p["hand_count"] == 6 and p["face_down_count"] == 3


def test_not_your_turn():
    with ExitStack() as stack:
        _, (b_ws, _, _) = start_game(stack, ["Alice", "Bob"])
        b_ws.send_json({"type": "setup_confirm"})
        reply = b_ws.receive_json()
        assert reply == {"type": "error", "message": "It's not your turn."}


def do_setup(players, ws_by_name, first_state):
    """Every player picks their first 3 hand cards as face-up. Returns the latest states."""
    turn = first_state["turn"]
    while True:
        ws = ws_by_name[turn]
        for i in range(3):
            kind, _ = act(players, ws, {"type": "setup_toggle", "index": i})
            assert kind == "state"
        kind, states = act(players, ws, {"type": "setup_confirm"})
        assert kind == "state"
        state = states[turn]
        if state["state"] != "setup":
            return states
        turn = state["turn"]


def test_duplicate_indices_rejected():
    with ExitStack() as stack:
        started = start_game(stack, ["Alice", "Bob"])
        players = [(ws, name) for ws, name, _ in started]
        states = do_setup(players, dict((n, w) for w, n in players), started[0][2])

        turn = next(iter(states.values()))["turn"]
        ws = dict((n, w) for w, n in players)[turn]
        kind, text = act(players, ws, {"type": "play", "zone": "hand", "indices": [0, 0]})
        assert (kind, text) == ("error", "Each card can only be played once.")


def test_cannot_play_face_up_while_holding_hand():
    with ExitStack() as stack:
        started = start_game(stack, ["Alice", "Bob"])
        players = [(ws, name) for ws, name, _ in started]
        states = do_setup(players, dict((n, w) for w, n in players), started[0][2])

        turn = next(iter(states.values()))["turn"]
        ws = dict((n, w) for w, n in players)[turn]
        kind, text = act(players, ws, {"type": "play", "zone": "face_up", "indices": [0]})
        assert (kind, text) == ("error", "You can only play from your active zone.")


@pytest.mark.parametrize("seed", range(10))
def test_full_game_until_game_over(seed):
    """Two bots play a whole game: play all copies of a random valid card, otherwise take the pile.

    The seed fixes both the deck shuffle and the bots' choices, so each run is the same game.
    """
    random.seed(seed)  # Deck.shuffle uses the global random module
    bot = random.Random(seed)
    with ExitStack() as stack:
        started = start_game(stack, ["Alice", "Bob"])
        players = [(ws, name) for ws, name, _ in started]
        ws_by_name = dict((n, w) for w, n in players)
        states = do_setup(players, ws_by_name, started[0][2])

        for _ in range(2000):
            state = next(iter(states.values()))
            if state["state"] == "game_over":
                break
            turn = state["turn"]
            ws = ws_by_name[turn]
            me = states[turn]

            if me["active_zone"] == "face_down":
                kind, result = act(players, ws, {"type": "play_face_down", "index": 0})
            else:
                zone = me["active_zone"]
                cards = me["hand"] if zone == "hand" else next(
                    p for p in me["players"] if p["name"] == turn)["face_up"]
                kind = "error"
                for i in bot.sample(range(len(cards)), len(cards)):
                    same = [j for j, c in enumerate(cards) if c["value"] == cards[i]["value"]]
                    kind, result = act(players, ws, {"type": "play", "zone": zone, "indices": same})
                    if kind == "state":
                        break
                if kind == "error":
                    kind, result = act(players, ws, {"type": "take_pile"})
            assert kind == "state", result
            states = result
        else:
            raise AssertionError("Game did not finish in 2000 moves")

        final = next(iter(states.values()))
        assert sorted(final["finish_order"]) == sorted(ws_by_name)


def test_disconnect_ends_game_for_others():
    with ExitStack() as stack:
        (a_ws, alice, _), (b_ws, _, _) = start_game(stack, ["Alice", "Bob"])
        a_ws.close()
        state = b_ws.receive_json()
        assert state["state"] == "game_over"
        assert state["message"] == f"{alice} left the game."
