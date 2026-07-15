import pytest
from model.board import Board
from game.game_engine import GameEngine
from game.real_time_arbiter import MoveScheduler
from model.piece import Piece


@pytest.fixture
def setup_game():
    # יצירת לוח 3x3 עם צריח ומלך
    grid = [[None for _ in range(3)] for _ in range(3)]
    grid[1][0] = Piece('w', 'R')
    grid[1][2] = Piece('b', 'K')
    board = Board(grid)
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)
    return engine, board, scheduler


def test_king_capture_ends_game(setup_game):
    engine, board, scheduler = setup_game
    rook = board.get_piece(1, 0)

    # מהלך אכילת המלך
    engine.request_move(rook, 1, 2, 1000)
    engine.process_time_step(1000)

    assert engine.is_game_over() is True

    # ניסיון לבצע מהלך נוסף אחרי שהמשחק נגמר
    result = engine.request_move(rook, 1, 1, 2000)
    assert result is False


def test_no_moves_after_game_over(setup_game):
    engine, board, scheduler = setup_game
    rook = board.get_piece(1, 0)

    # סיום המשחק
    engine.request_move(rook, 1, 2, 1000)
    engine.process_time_step(1000)

    # הוספת כלי נוסף לשחור וניסיון להזיז אותו
    board._grid[0][0] = Piece('b', 'R')
    board._piece_locations[board._grid[0][0]] = (0, 0)

    rook_black = board.get_piece(0, 0)
    result = engine.request_move(rook_black, 0, 1, 2000)

    assert result is False
    assert engine.is_game_over() is True
