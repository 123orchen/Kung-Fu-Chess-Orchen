from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from config import CELL_SIZE
from graphics.py.img import Img


class SpriteManager:
    def __init__(self, asset_root: str | Path | None = None):
        if asset_root is None:
            asset_root = Path(__file__).resolve().parent / "assets" / "pieces_mine"
        self.asset_root = Path(asset_root)
        self._state_cache: Dict[str, Dict[str, dict]] = {}

    def get_sprite(self, piece, state: str, current_time_ms: int) -> Optional[Img]:
        path = self._get_frame_path(piece, state, current_time_ms)
        if path is None:
            return None
        return Img().read(path, size=(CELL_SIZE, CELL_SIZE), keep_aspect=True)

    def get_state(self, piece, scheduler) -> str:
        if scheduler is not None and scheduler.is_piece_moving(piece):
            move = scheduler.get_move_for_piece(piece)
            if move is not None and move.is_jump():
                return "jump"
            return "move"
        return "idle"

    def _get_frame_path(self, piece, state: str, current_time_ms: int) -> Optional[Path]:
        piece_key = f"{piece.color}{piece.type}"
        paths, config = self._get_state_data(piece_key, state)
        if not paths and state != "idle":
            paths, config = self._get_state_data(piece_key, "idle")
        if not paths:
            return None

        frames_per_sec = config.get("frames_per_sec", 1)
        is_loop = config.get("is_loop", True)
        frame_count = len(paths)

        if frames_per_sec <= 0 or frame_count == 1:
            index = 0
        else:
            frame_number = int((current_time_ms / 1000.0) * frames_per_sec)
            if is_loop:
                index = frame_number % frame_count
            else:
                index = min(frame_number, frame_count - 1)

        return paths[index]

    def _get_state_data(self, piece_key: str, state: str) -> tuple[List[Path], dict]:
        if piece_key not in self._state_cache:
            self._state_cache[piece_key] = {}

        if state in self._state_cache[piece_key]:
            return self._state_cache[piece_key][state]["paths"], self._state_cache[piece_key][state]["config"]

        state_dir = self.asset_root / piece_key / "states" / state
        paths: List[Path] = []
        config = {"frames_per_sec": 1, "is_loop": True}

        if state_dir.exists():
            config_path = state_dir / "config.json"
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text(encoding="utf-8"))
                    config = config.get("graphics", config)
                except json.JSONDecodeError:
                    config = {"frames_per_sec": 1, "is_loop": True}

            sprite_dir = state_dir / "sprites"
            if sprite_dir.exists():
                paths = sorted([p for p in sprite_dir.iterdir() if p.suffix.lower() == ".png"])

        self._state_cache[piece_key][state] = {"paths": paths, "config": config}
        return paths, config
