from __future__ import annotations

import numpy as np
import cv2
from pathlib import Path
from config import CELL_SIZE
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

    def render(self, board: Board, scheduler=None, current_turn: str | None = None,
               score_text: str | None = None, current_time_ms: int = 0, game_engine=None) -> Img:
        canvas = self._create_board_canvas()

        # Draw pieces with their sprites
        for row_idx, row in enumerate(board.get_grid()):
            for col_idx, piece in enumerate(row):
                if piece is None:
                    continue

                state = self.sprite_manager.get_state(piece, scheduler, current_time_ms)
                sprite = self.sprite_manager.get_sprite(piece, state, current_time_ms)
                if sprite is None:
                    continue

                sprite.draw_on(canvas, col_idx * CELL_SIZE, row_idx * CELL_SIZE)
                
                # Draw cooldown overlay if piece is on cooldown
                if scheduler is not None:
                    self._draw_cooldown_overlay(canvas, col_idx, row_idx, piece, scheduler, current_time_ms)

        if current_turn is not None:
            canvas.put_text(f"Turn: {current_turn}", 10, 30, 1.0, color=(0, 0, 0), thickness=2)
        if score_text:
            canvas.put_text(score_text, 10, 60, 1.0, color=(0, 0, 0), thickness=2)

        # Draw game over screen if game is over
        if game_engine is not None and game_engine.is_game_over():
            self._draw_game_over_screen(canvas, board)

        return canvas

    def _draw_cooldown_overlay(self, canvas, col_idx, row_idx, piece, scheduler, current_time_ms):
        """Draw a fading yellow overlay for pieces on cooldown"""
        alpha = scheduler.get_cooldown_alpha(piece, current_time_ms)
        if alpha <= 0:
            return
        
        x = col_idx * CELL_SIZE
        y = row_idx * CELL_SIZE
        
        # Create semi-transparent yellow overlay
        overlay_img = Img()
        overlay_img.img = np.zeros((CELL_SIZE, CELL_SIZE, 4), dtype=np.uint8)
        
        # חישוב ערך הצבע עם הגבלה ל-255 כדי למנוע Overflow
        color_val = int(max(0, min(255, 255 * alpha)))
        
        # BGRA format: Blue, Green, Red, Alpha
        overlay_img.img[:, :, 0] = 0           # B
        overlay_img.img[:, :, 1] = color_val   # G (yellow)
        overlay_img.img[:, :, 2] = color_val   # R (yellow)
        overlay_img.img[:, :, 3] = int(max(0, min(255, 100 * alpha))) # A (transparency)
        
        # Draw overlay on canvas
        overlay_img.draw_on(canvas, x, y)

    def _draw_game_over_screen(self, canvas, board):
        """Draw game over screen with winner information"""
        # Create semi-transparent dark overlay
        overlay = np.zeros((self.board_size, self.board_size, 3), dtype=np.uint8)
        canvas.img = cv2.addWeighted(canvas.img, 0.3, overlay, 0.7, 0)
        
        # Determine winner
        white_king_alive = board.is_king_on_board('w')
        black_king_alive = board.is_king_on_board('b')
        
        if white_king_alive and not black_king_alive:
            winner_text = "🏆 WHITE WINS! 🏆"
            title_text = "GAME OVER"
        elif black_king_alive and not white_king_alive:
            winner_text = "🏆 BLACK WINS! 🏆"
            title_text = "GAME OVER"
        else:
            winner_text = "DRAW"
            title_text = "GAME OVER"
        
        # Draw title
        text_y = self.board_size // 2 - 60
        canvas.put_text(title_text, 
                       self.board_size // 2 - 100, text_y,
                       2.5, color=(255, 255, 255), thickness=4)
        
        # Draw winner
        text_y += 100
        canvas.put_text(winner_text,
                       self.board_size // 2 - 150, text_y,
                       2.0, color=(0, 255, 255), thickness=3)
        
        # Draw instructions
        text_y += 80
        canvas.put_text("Press Q or ESC to exit",
                       self.board_size // 2 - 120, text_y,
                       1.0, color=(255, 255, 255), thickness=2)

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
