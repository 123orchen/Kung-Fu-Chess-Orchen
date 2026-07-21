from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

import cv2

from config import (
    BOTTOM_MARGIN, CELL_SIZE, LEFT_PANEL_WIDTH, RIGHT_PANEL_WIDTH, TOP_MARGIN,
)
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
        # The full canvas (board + side panels + header/footer) is often
        # taller than a laptop screen. A plain cv2.namedWindow() defaults to
        # WINDOW_AUTOSIZE - a fixed, non-resizable window at the canvas's
        # native pixel size - so anything past the bottom of the screen
        # becomes unreachable (that's what was cutting off the footer and
        # even the top row). WINDOW_NORMAL makes it resizable, and we open
        # it at a size that fits comfortably on common screens; OpenCV
        # always reports mouse-click coordinates back in the *canvas's*
        # original pixel space regardless of the on-screen window size, so
        # this doesn't change any of the click/board-offset math.
        canvas_width = LEFT_PANEL_WIDTH + CELL_SIZE * 8 + RIGHT_PANEL_WIDTH
        canvas_height = TOP_MARGIN + CELL_SIZE * 8 + BOTTOM_MARGIN
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, min(canvas_width, 1000), min(canvas_height, 640))
        cv2.moveWindow(WINDOW_NAME, 20, 20)
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
                current_time_ms=self.current_time_ms,
                game_engine=self.controller.engine,
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
        # The board is drawn offset inside the window (side panels + header/
        # footer take up the rest) - translate to board-relative coordinates
        # here, once, so the controller/BoardMapper stay untouched and keep
        # assuming a plain (0,0)-origin board like the text runner and tests do.
        board_x = x - self.renderer.board_offset_x
        board_y = y - self.renderer.board_offset_y
        if not (0 <= board_x < self.renderer.board_size and 0 <= board_y < self.renderer.board_size):
            return  # click landed in a panel/header/footer, not on the board

        if event == cv2.EVENT_LBUTTONDOWN:
            self.click_events.append(("click", board_x, board_y))
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.click_events.append(("jump", board_x, board_y))


def run():
    GraphicsApp().run()


if __name__ == "__main__":
    run()
