"""Stage A server: single-process FastAPI server, one WebSocket endpoint.

Scope on purpose (matches the first stage of the assignment):
  - Exactly one game / one board. No login, no rooms, no ELO yet - those
    are later stages.
  - First client to connect is White, second is Black. A third connection
    is rejected (spectators come in a later stage, alongside rooms).
  - A client sends a "move" message; the server relays it to the other
    player as-is. The server does not validate chess rules - each client
    runs the same engine locally and is trusted to only send legal moves
    for its own color (this can be hardened later if needed).
  - The Bus is wired in now (as required) and used to log every move;
    later stages can add more subscribers (score, sound, animations)
    without touching this file.

Run with:  uvicorn server.server:app --reload
"""
import json
import logging
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from server.bus import Bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kfc-server")

app = FastAPI()
bus = Bus()


def _log_move(data):
    logger.info("move: %s", data)


bus.subscribe("move", _log_move)


class GameRoom:
    """Stage A/B: exactly one game. Rooms/multiple games arrive in a later stage."""

    def __init__(self):
        # 'w'/'b' -> {"ws": WebSocket, "username": str}
        self.players: Dict[str, dict] = {}

    def assign_color(self) -> Optional[str]:
        if "w" not in self.players:
            return "w"
        if "b" not in self.players:
            return "b"
        return None  # full - spectators not supported yet


room = GameRoom()


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Stage B: username is sent as a query param, e.g. /ws?username=Dana
    # ("just for presentation" per the spec - no password/verification yet,
    # that's a later stage). Fall back to a placeholder if it's missing.
    username = websocket.query_params.get("username") or "Anonymous"

    color = room.assign_color()
    if color is None:
        await websocket.send_text(json.dumps({"type": "error", "message": "Game is full"}))
        await websocket.close()
        return

    room.players[color] = {"ws": websocket, "username": username}
    await websocket.send_text(json.dumps({"type": "assign", "color": color, "username": username}))
    logger.info("%s connected as %s (players now: %s)",
                username, color, {c: p["username"] for c, p in room.players.items()})

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Ignoring non-JSON message: %r", raw)
                continue

            if data.get("type") == "move":
                if data.get("color") != color:
                    logger.warning("Player %s tried to send a move for the other color", color)
                    continue
                bus.publish("move", data)
                await _relay_to_opponent(color, raw)
    except WebSocketDisconnect:
        logger.info("%s (%s) disconnected", username, color)
        room.players.pop(color, None)
        # Stage A: no auto-resign countdown yet - added in a later stage.


async def _relay_to_opponent(sender_color: str, raw: str):
    for other_color, player in room.players.items():
        if other_color != sender_color:
            await player["ws"].send_text(raw)
