import pytest
from model.board import Board
from game.controller import GameController
from game.game_engine import GameEngine
from game.real_time_arbiter import MoveScheduler
from model.piece import Piece
from config import PAWN, WHITE_TURN


def create_board():
    # חייל לבן בשורה 1, טור 0 (כדי שיוכל לנוע ל-0,0)
    grid = [[None, None],
            [Piece(WHITE_TURN, PAWN), None]]
    return Board(grid)


def test_move_pending_before_arrival():
    board = create_board()
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)
    controller = GameController(board, engine, scheduler)

    # לחיצה על (0, 1) -> (50, 150) ועל (0, 0) -> (50, 50)
    controller.handle_click(50, 150)
    controller.handle_click(50, 50)

    controller.handle_wait(500)

    # אחרי 500ms החייל עדיין ב-(1,0) ולא עבר ל-(0,0)
    assert board.get_piece(1, 0) is not None
    assert board.get_piece(0, 0) is None


def test_move_executes_after_arrival():
    board = create_board()
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)
    controller = GameController(board, engine, scheduler)

    controller.handle_click(50, 150)
    controller.handle_click(50, 50)

    controller.handle_wait(1000)

    # בגלל הטריק של ה-< (פחות מ-), ב-1000ms הוא עדיין לא זז
    # נחכה עוד טיפה או נריץ עוד wait כדי לוודא שזה קרה
    controller.handle_wait(1)
    assert board.get_piece(0, 0) is not None