"""Stage D server: matchmaking by ELO, disconnect auto-resign with countdown.

Builds on stages A-C. The big change here is that the server no longer
holds a single global game - it can host many concurrent games at once,
each identified by a game_id, because matchmaking pairs up whichever two
players are compatible right now.

Flow per connection:
  1. Login (username + password, same as stage C).
  2. Automatic matchmaking ("Play"): look for a waiting opponent whose
     rating is within +-100. If found, both players are placed in a new
     game and told their color. If not, the player waits up to 60s; if
     still no match, the server reports "no_match" and closes.
     (There's no Home Screen GUI yet with an actual Play button - see the
     handoff notes. This auto-plays right after login instead.)
  3. Once matched, moves are relayed within that specific game only.
  4. If a player disconnects mid-game, the opponent is told to show a
     20-second countdown. If the game hasn't otherwise ended by then, the
     disconnected player auto-resigns and ELO is updated. There's no
     reconnect support yet - see handoff notes.

Run with:  uvicorn server.server:app --reload
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from server.bus import Bus
from server.db import PlayerDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kfc-server")

app = FastAPI()
bus = Bus()
db = PlayerDB()

ELO_RANGE = 100
MATCH_TIMEOUT_SEC = 60
DISCONNECT_GRACE_SEC = 20


def _log_move(data):
    logger.info("move: %s", data)


def _log_score(data):
    logger.info("score update: %s", data)


bus.subscribe("move", _log_move)
bus.subscribe("score", _log_score)


class GameRoom:
    def __init__(self):
        # 'w'/'b' -> {"ws": WebSocket, "username": str, "rating": int}
        self.players: Dict[str, dict] = {}
        self.game_over_recorded = False


games: Dict[str, GameRoom] = {}
connections: Dict[WebSocket, dict] = {}  # ws -> {"game_id": str, "color": str}
waiting: list = []  # each: {"username", "rating", "ws", "event": asyncio.Event}


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    username = websocket.query_params.get("username") or "Anonymous"
    password = websocket.query_params.get("password") or ""

    ok, rating, error = db.login_or_register(username, password)
    if not ok:
        await websocket.send_text(json.dumps({"type": "error", "message": error}))
        await websocket.close()
        return

    await websocket.send_text(json.dumps({"type": "login_ok", "rating": rating}))
    logger.info("%s logged in (rating %s)", username, rating)

    match = await _matchmake(websocket, username, rating)
    if match is None:
        await websocket.send_text(json.dumps({"type": "no_match"}))
        await websocket.close()
        return
    game_id, color = match

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Ignoring non-JSON message: %r", raw)
                continue

            msg_type = data.get("type")
            if msg_type == "move":
                if data.get("color") != color:
                    logger.warning("Player %s tried to send a move for the other color", color)
                    continue
                bus.publish("move", data)
                await _relay_to_opponent(game_id, color, raw)
            elif msg_type == "game_over":
                winner = data.get("winner")
                if winner in ("w", "b"):
                    await _finish_game(game_id, winner)
    except WebSocketDisconnect:
        logger.info("%s (%s) disconnected from game %s", username, color, game_id)
        connections.pop(websocket, None)
        await _handle_disconnect(game_id, color)


async def _matchmake(websocket: WebSocket, username: str, rating: int):
    """Returns (game_id, color) once matched, or None if no match within the timeout."""
    for i, entry in enumerate(waiting):
        if abs(entry["rating"] - rating) <= ELO_RANGE:
            waiting.pop(i)
            game_id = uuid.uuid4().hex[:8]
            room = GameRoom()
            room.players["w"] = {"ws": entry["ws"], "username": entry["username"], "rating": entry["rating"]}
            room.players["b"] = {"ws": websocket, "username": username, "rating": rating}
            games[game_id] = room
            connections[entry["ws"]] = {"game_id": game_id, "color": "w"}
            connections[websocket] = {"game_id": game_id, "color": "b"}
            await entry["ws"].send_text(json.dumps({
                "type": "matched", "color": "w", "game_id": game_id, "opponent": username,
            }))
            entry["event"].set()
            logger.info("Matched %s (w) vs %s (b) in game %s", entry["username"], username, game_id)
            await websocket.send_text(json.dumps({
                "type": "matched", "color": "b", "game_id": game_id, "opponent": entry["username"],
            }))
            return game_id, "b"

    my_entry = {"username": username, "rating": rating, "ws": websocket, "event": asyncio.Event()}
    waiting.append(my_entry)
    try:
        await asyncio.wait_for(my_entry["event"].wait(), timeout=MATCH_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        if my_entry in waiting:
            waiting.remove(my_entry)
        return None

    conn = connections.get(websocket)
    return (conn["game_id"], conn["color"]) if conn else None


async def _relay_to_opponent(game_id: str, sender_color: str, raw: str):
    room = games.get(game_id)
    if not room:
        return
    for other_color, player in room.players.items():
        if other_color != sender_color:
            await player["ws"].send_text(raw)


async def _handle_disconnect(game_id: str, color: str):
    room = games.get(game_id)
    if room is None or room.game_over_recorded:
        return
    opponent_color = "b" if color == "w" else "w"
    opponent = room.players.get(opponent_color)
    if opponent is None:
        return

    await opponent["ws"].send_text(json.dumps({"type": "opponent_disconnected", "seconds": DISCONNECT_GRACE_SEC}))
    await asyncio.sleep(DISCONNECT_GRACE_SEC)
    if room.game_over_recorded:
        return  # game already ended some other way while we were waiting
    await _finish_game(game_id, winner_color=opponent_color)


async def _finish_game(game_id: str, winner_color: str):
    room = games.get(game_id)
    if room is None or room.game_over_recorded:
        return
    if "w" not in room.players or "b" not in room.players:
        return
    room.game_over_recorded = True

    loser_color = "b" if winner_color == "w" else "w"
    winner = room.players[winner_color]
    loser = room.players[loser_color]

    new_w_rating, new_l_rating = db.update_ratings_after_game(winner["username"], loser["username"])
    room.players[winner_color]["rating"] = new_w_rating
    room.players[loser_color]["rating"] = new_l_rating

    bus.publish("score", {
        "winner": winner["username"], "loser": loser["username"],
        "winner_rating": new_w_rating, "loser_rating": new_l_rating,
    })

    white_rating = room.players["w"]["rating"]
    black_rating = room.players["b"]["rating"]
    result = json.dumps({
        "type": "game_over", "winner": winner_color,
        "white_rating": white_rating, "black_rating": black_rating,
    })
    for player in room.players.values():
        try:
            await player["ws"].send_text(result)
        except Exception:
            pass  # that side may already be gone
