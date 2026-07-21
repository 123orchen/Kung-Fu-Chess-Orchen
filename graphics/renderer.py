from __future__ import annotations

import numpy as np
import cv2
from pathlib import Path
from config import (
    BOTTOM_MARGIN, CELL_SIZE, LEFT_PANEL_WIDTH, PANEL_ROW_HEIGHT,
    RIGHT_PANEL_WIDTH, TOP_MARGIN,
)
from graphics.py.img import Img
from graphics.sprite_manager import SpriteManager
from model.board import Board


class Renderer:
    def __init__(self, asset_root: str | Path | None = None):
        if asset_root is None:
            asset_root = Path(__file__).resolve().parent / "assets" / "pieces_mine"
        self.sprite_manager = SpriteManager(asset_root)
        self.board_size = CELL_SIZE * 8
        self.light_color = (240, 217, 181)
        self.dark_color = (181, 136, 99)
        self.panel_bg_color = (60, 60, 60)
        # Where the 8x8 board sits inside the full canvas (panels/header/footer
        # take up the rest). Mouse clicks must be translated by this same
        # offset before reaching the controller - see GraphicsApp._mouse_callback.
        self.board_offset_x = LEFT_PANEL_WIDTH
        self.board_offset_y = TOP_MARGIN
        self.canvas_width = LEFT_PANEL_WIDTH + self.board_size + RIGHT_PANEL_WIDTH
        self.canvas_height = TOP_MARGIN + self.board_size + BOTTOM_MARGIN

    def render(self, board: Board, scheduler=None, current_time_ms: int = 0,
               game_engine=None, black_name: str = "Black Player",
               white_name: str = "White Player") -> Img:
        canvas = self._create_full_canvas()

        self._draw_board_squares(canvas)
        self._draw_pieces(canvas, board, scheduler, current_time_ms)

        score = game_engine.get_score() if game_engine is not None else {'w': 0, 'b': 0}
        move_history = game_engine.move_history if game_engine is not None else None

        self._draw_header_footer(canvas, black_name, white_name, score)
        self._draw_side_panel(canvas, move_history, color='b', x0=0, header="Black")
        self._draw_side_panel(canvas, move_history, color='w',
                               x0=self.board_offset_x + self.board_size, header="White")

        if game_engine is not None and game_engine.is_game_over():
            self._draw_game_over_screen(canvas, board)

        return canvas

    def _draw_board_squares(self, canvas: Img):
        for row_idx in range(8):
            for col_idx in range(8):
                color = self.light_color if (row_idx + col_idx) % 2 == 0 else self.dark_color
                y0 = self.board_offset_y + row_idx * CELL_SIZE
                x0 = self.board_offset_x + col_idx * CELL_SIZE
                canvas.img[y0:y0 + CELL_SIZE, x0:x0 + CELL_SIZE] = color

    def _draw_pieces(self, canvas: Img, board: Board, scheduler, current_time_ms: int):
        for row_idx, row in enumerate(board.get_grid()):
            for col_idx, piece in enumerate(row):
                if piece is None:
                    continue

                state = self.sprite_manager.get_state(piece, scheduler, current_time_ms)
                sprite = self.sprite_manager.get_sprite(piece, state, current_time_ms)
                if sprite is None:
                    continue

                x = self.board_offset_x + col_idx * CELL_SIZE
                y = self.board_offset_y + row_idx * CELL_SIZE
                sprite.draw_on(canvas, x, y)

                if scheduler is not None:
                    self._draw_cooldown_overlay(canvas, x, y, piece, scheduler, current_time_ms)

    def _draw_cooldown_overlay(self, canvas, x, y, piece, scheduler, current_time_ms):
        """Draw a fading yellow overlay for pieces on cooldown"""
        alpha = scheduler.get_cooldown_alpha(piece, current_time_ms)
        if alpha <= 0:
            return

        overlay_img = Img()
        overlay_img.img = np.zeros((CELL_SIZE, CELL_SIZE, 4), dtype=np.uint8)

        color_val = int(max(0, min(255, 255 * alpha)))

        overlay_img.img[:, :, 0] = 0
        overlay_img.img[:, :, 1] = color_val
        overlay_img.img[:, :, 2] = color_val
        overlay_img.img[:, :, 3] = int(max(0, min(255, 100 * alpha)))

        overlay_img.draw_on(canvas, x, y)

    def _draw_header_footer(self, canvas: Img, black_name, white_name, score):
        center_x = self.canvas_width // 2

        canvas.put_text(f"Name: {black_name}", center_x - 140, 30, 0.8, color=(255, 255, 255), thickness=2)
        canvas.put_text(f"Score: {score.get('b', 0)}", center_x - 60, 60, 0.7, color=(255, 255, 255), thickness=1)

        footer_y = self.board_offset_y + self.board_size
        canvas.put_text(f"Score: {score.get('w', 0)}", center_x - 60, footer_y + 30, 0.7, color=(255, 255, 255), thickness=1)
        canvas.put_text(f"Name: {white_name}", center_x - 140, footer_y + 60, 0.8, color=(255, 255, 255), thickness=2)

    def _draw_side_panel(self, canvas: Img, move_history, color, x0, header):
        panel_width = LEFT_PANEL_WIDTH if x0 == 0 else RIGHT_PANEL_WIDTH
        y0 = self.board_offset_y
        canvas.img[y0:y0 + self.board_size, x0:x0 + panel_width] = self.panel_bg_color

        canvas.put_text(header, x0 + panel_width // 2 - 20, y0 + 20, 0.6, color=(255, 255, 255), thickness=2)
        canvas.put_text("Time", x0 + 10, y0 + 45, 0.45, color=(200, 200, 200), thickness=1)
        canvas.put_text("Move", x0 + 100, y0 + 45, 0.45, color=(200, 200, 200), thickness=1)

        if move_history is None:
            return

        entries = move_history.for_color(color)
        rows_available = max(0, (self.board_size - 70) // PANEL_ROW_HEIGHT)
        visible = entries[-rows_available:] if rows_available else []

        row_y = y0 + 70
        for entry in visible:
            canvas.put_text(entry.elapsed_label, x0 + 10, row_y, 0.42, color=(230, 230, 230), thickness=1)
            canvas.put_text(entry.notation, x0 + 100, row_y, 0.42, color=(230, 230, 230), thickness=1)
            row_y += PANEL_ROW_HEIGHT

    def _draw_game_over_screen(self, canvas, board):
        """Draw game over screen with winner information"""
        overlay = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        canvas.img = cv2.addWeighted(canvas.img, 0.3, overlay, 0.7, 0)

        white_king_alive = board.is_king_on_board('w')
        black_king_alive = board.is_king_on_board('b')

        if white_king_alive and not black_king_alive:
            winner_text = "WHITE WINS!"
            title_text = "GAME OVER"
        elif black_king_alive and not white_king_alive:
            winner_text = "BLACK WINS!"
            title_text = "GAME OVER"
        else:
            winner_text = "DRAW"
            title_text = "GAME OVER"

        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2

        text_y = center_y - 60
        canvas.put_text(title_text, center_x - 100, text_y, 2.5, color=(255, 255, 255), thickness=4)

        text_y += 100
        canvas.put_text(winner_text, center_x - 150, text_y, 2.0, color=(0, 255, 255), thickness=3)

        text_y += 80
        canvas.put_text("Press Q or ESC to exit", center_x - 120, text_y, 1.0, color=(255, 255, 255), thickness=2)

    def _create_full_canvas(self) -> Img:
        canvas = Img()
        canvas.img = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.uint8)
        return canvas
