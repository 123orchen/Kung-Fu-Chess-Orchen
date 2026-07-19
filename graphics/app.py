from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

import cv2

from config import CELL_SIZE
from game.controller import GameController
from graphics.renderer import Renderer
from model.board import Board
from model.piece import Piece

WINDOW_NAME = "ChessGame"
GRAPHICS_ROOT = Path(__file__).resolve().parent


class GraphicsApp:
    def __init__(self, asset_root: str | Path | None = None):
        self.board = self._create_default_board()
        self.controller = GameController(self.board)
        asset_root = asset_root or (GRAPHICS_ROOT / "assets" / "pieces_mine")
        self.renderer = Renderer(asset_root)
        self.click_events: List[tuple[str, int, int]] = []
        self.current_time_ms = 0

    def _create_default_board(self) -> Board:
        """Create a standard chess starting position."""
        grid: List[List[Optional[Piece]]] = []
        
        # Row 0: Black back rank
        grid.append([
            Piece('b', 'R'), Piece('b', 'N'), Piece('b', 'B'), Piece('b', 'Q'),
            Piece('b', 'K'), Piece('b', 'B'), Piece('b', 'N'), Piece('b', 'R')
        ])
        
        # Row 1: Black pawns
        grid.append([Piece('b', 'P') for _ in range(8)])
        
        # Rows 2-5: Empty
        for _ in range(4):
            grid.append([None for _ in range(8)])
        
        # Row 6: White pawns
        grid.append([Piece('w', 'P') for _ in range(8)])
        
        # Row 7: White back rank
        grid.append([
            Piece('w', 'R'), Piece('w', 'N'), Piece('w', 'B'), Piece('w', 'Q'),
            Piece('w', 'K'), Piece('w', 'B'), Piece('w', 'N'), Piece('w', 'R')
        ])
        
        return Board(grid)

    def run(self):
        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self._mouse_callback)

        last_time = time.time()
        while True:
            now = time.time()
            dt_ms = int((now - last_time) * 1000)
            last_time = now
            self.current_time_ms += dt_ms
            self.controller.handle_wait(dt_ms)

            self._process_clicks()
            image = self.renderer.render(
                self.board,
                scheduler=self.controller.scheduler,
                current_turn=None,
                score_text=self._build_score_text(),
                current_time_ms=self.current_time_ms,
                game_engine=self.controller._engine,
            )
            cv2.imshow(WINDOW_NAME, image.img)

            key = cv2.waitKey(30) & 0xFF
            if key == ord("q") or key == 27:
                break
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyAllWindows()

    def _process_clicks(self):
        while self.click_events:
            event, x, y = self.click_events.pop(0)
            if event == "click":
                self.controller.handle_click(x, y)
            elif event == "jump":
                self.controller.handle_jump(x, y)

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.click_events.append(("click", x, y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.click_events.append(("jump", x, y))

    def _build_score_text(self) -> str:
        white_count = 0
        black_count = 0
        for row in self.board.get_grid():
            for piece in row:
                if piece is None:
                    continue
                if piece.color == "w":
                    white_count += 1
                elif piece.color == "b":
                    black_count += 1
        return f"White: {white_count}  Black: {black_count}"


def run():
    GraphicsApp().run()


if __name__ == "__main__":
    run()
