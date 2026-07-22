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
    """Stage A: exactly one game. Rooms/multiple games arrive in a later stage."""

    def __init__(self):
        self.players: Dict[str, WebSocket] = {}  # 'w'/'b' -> websocket (matches Piece.color)

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

    color = room.assign_color()
    if color is None:
        await websocket.send_text(json.dumps({"type": "error", "message": "Game is full"}))
        await websocket.close()
        return

    room.players[color] = websocket
    await websocket.send_text(json.dumps({"type": "assign", "color": color}))
    logger.info("Player connected as %s (players now: %s)", color, list(room.players))

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
        logger.info("Player %s disconnected", color)
        room.players.pop(color, None)
        # Stage A: no auto-resign countdown yet - added in a later stage.


async def _relay_to_opponent(sender_color: str, raw: str):
    for other_color, ws in room.players.items():
        if other_color != sender_color:
            await ws.send_text(raw)
