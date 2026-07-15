from __future__ import annotations

import numpy as np
from py.img import Img
from config import CELL_SIZE
from graphics.sprite_manager import SpriteManager
from model.board import Board


class Renderer:
    def __init__(self, asset_root: str = "pieces1"):
        self.sprite_manager = SpriteManager(asset_root)
        self.board_size = CELL_SIZE * 8
        self.light_color = (240, 217, 181)
        self.dark_color = (181, 136, 99)

    def render(self, board: Board, scheduler=None, current_turn: str | None = None,
               score_text: str | None = None, current_time_ms: int = 0) -> Img:
        canvas = self._create_board_canvas()

        for row_idx, row in enumerate(board.get_grid()):
            for col_idx, piece in enumerate(row):
                if piece is None:
                    continue

                state = self.sprite_manager.get_state(piece, scheduler)
                sprite = self.sprite_manager.get_sprite(piece, state, current_time_ms)
                if sprite is None:
                    continue

                sprite.draw_on(canvas, col_idx * CELL_SIZE, row_idx * CELL_SIZE)

        if current_turn is not None:
            canvas.put_text(f"Turn: {current_turn}", 10, 30, 1.0, color=(0, 0, 0), thickness=2)
        if score_text:
            canvas.put_text(score_text, 10, 60, 1.0, color=(0, 0, 0), thickness=2)

        return canvas

    def _create_board_canvas(self) -> Img:
        canvas = Img()
        board_pixels = self.board_size
        canvas.img = np.zeros((board_pixels, board_pixels, 3), dtype=np.uint8)

        for row_idx in range(8):
            for col_idx in range(8):
                color = self.light_color if (row_idx + col_idx) % 2 == 0 else self.dark_color
                y0 = row_idx * CELL_SIZE
                x0 = col_idx * CELL_SIZE
                canvas.img[y0:y0 + CELL_SIZE, x0:x0 + CELL_SIZE] = color

        return canvas
