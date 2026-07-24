"""Client-side WebSocket connection to the game server.

The graphics app runs a synchronous, blocking loop (OpenCV's
`cv2.waitKey`), so the WebSocket connection - which needs `asyncio` -
runs on its own background thread with its own event loop. The two
sides only talk through a thread-safe queue:

  - Outgoing: `send_move(...)` schedules a send on the background loop.
  - Incoming: messages from the server land in `self.incoming`; the
    main/graphics thread calls `poll_incoming()` once per frame to
    drain it and apply any opponent moves.
"""
import asyncio
import json
import logging
import queue
import threading
from typing import Optional
from urllib.parse import quote

import websockets

logger = logging.getLogger("kfc-client")


class NetworkClient:
    def __init__(self, uri: str = "ws://localhost:8000/ws", username: str = "Player", password: str = ""):
        self.uri = f"{uri}?username={quote(username)}&password={quote(password)}"
        self.username = username
        self.rating: Optional[int] = None
        self.color: Optional[str] = None
        self.game_id: Optional[str] = None
        self.opponent: Optional[str] = None
        self.incoming: "queue.Queue[dict]" = queue.Queue()
        self.connected = False
        self.error: Optional[str] = None

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._ws = None
        self._logged_in = threading.Event()
        self._matched = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self, timeout: float = 5.0) -> bool:
        """Connect and block until login succeeds or fails (or times out)."""
        self._thread.start()
        self._logged_in.wait(timeout=timeout)
        return self.connected and self.error is None

    def wait_for_match(self, timeout: float = 65.0) -> bool:
        """Block until matchmaking finds an opponent (or times out / fails)."""
        self._matched.wait(timeout=timeout)
        return self.color is not None

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connect_and_listen())
        except Exception as exc:  # connection refused, dropped, etc.
            self.error = str(exc)
            logger.warning("Network client stopped: %s", exc)
        finally:
            self.connected = False
            self._logged_in.set()  # unblock start()/wait_for_match() even on early failure
            self._matched.set()

    async def _connect_and_listen(self):
        async with websockets.connect(self.uri) as ws:
            self._ws = ws
            self.connected = True
            async for raw in ws:
                data = json.loads(raw)
                msg_type = data.get("type")
                if msg_type == "login_ok":
                    self.rating = data.get("rating")
                    self._logged_in.set()
                elif msg_type == "matched":
                    self.color = data["color"]
                    self.game_id = data.get("game_id")
                    self.opponent = data.get("opponent")
                    self._matched.set()
                elif msg_type == "no_match":
                    self.error = "No opponent found within the wait time"
                    self._matched.set()
                elif msg_type == "error":
                    self.error = data.get("message", "server error")
                    self._logged_in.set()
                    self._matched.set()
                else:
                    self.incoming.put(data)

    def send_move(self, color: str, piece_type: str, from_rc, to_rc, move_type: str = "normal"):
        if not self.connected or self._ws is None or self._loop is None:
            return
        payload = json.dumps({
            "type": "move",
            "color": color,
            "piece": piece_type,
            "from": list(from_rc),
            "to": list(to_rc),
            "move_type": move_type,
        })
        asyncio.run_coroutine_threadsafe(self._ws.send(payload), self._loop)

    def send_game_over(self, winner_color: str):
        if not self.connected or self._ws is None or self._loop is None:
            return
        payload = json.dumps({"type": "game_over", "winner": winner_color})
        asyncio.run_coroutine_threadsafe(self._ws.send(payload), self._loop)

    def poll_incoming(self):
        """Drain and return every message received since the last call."""
        messages = []
        while True:
            try:
                messages.append(self.incoming.get_nowait())
            except queue.Empty:
                break
        return messages
