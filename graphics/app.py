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
BOARD_CSV = GRAPHICS_ROOT / "assets" / "pieces1" / "board.csv"


def load_board_from_csv(csv_path: Path) -> Board:
    if not csv_path.exists():
        raise FileNotFoundError(f"Board CSV not found: {csv_path}")

    rows: List[List[Optional[Piece]]] = []
    for raw_line in csv_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        tokens = [token.strip() for token in raw_line.split(",")]
        row: List[Optional[Piece]] = []
        for token in tokens:
            if token == "" or token == ".":
                row.append(None)
            else:
                row.append(Piece(token[0], token[1]))
        rows.append(row)

    return Board(rows)


class GraphicsApp:
    def __init__(self, asset_root: str | Path | None = None):
        self.board = load_board_from_csv(BOARD_CSV)
        self.controller = GameController(self.board)
        asset_root = asset_root or (GRAPHICS_ROOT / "assets" / "pieces1")
        self.renderer = Renderer(asset_root)
        self.click_events: List[tuple[str, int, int]] = []
        self.current_time_ms = 0

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
