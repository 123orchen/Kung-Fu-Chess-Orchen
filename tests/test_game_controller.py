import pytest
from board import Board
from game_controller import GameController
from piece import Piece


def test_click_selection():
    # לוח 2x2: כלי ב-0,0 ומשבצת ריקה ב-0,1
    grid = [[Piece('w', 'K'), None], [None, None]]
    board = Board(grid)
    controller = GameController(board)

    # לחיצה על (50, 50) - זה תא 0,0
    controller.handle_click(50, 50)
    assert controller._selected_piece is not None
    assert controller._selected_piece._type == 'K'


def test_click_outside_ignored():
    grid = [[None, None], [None, None]]
    board = Board(grid)
    controller = GameController(board)

    # לחיצה מחוץ ללוח (300, 300)
    controller.handle_click(300, 300)
    assert controller._selected_piece is None


def test_wait_logic():
    grid = [[None, None], [None, None]]
    board = Board(grid)
    controller = GameController(board)

    controller.handle_wait(500)
    assert controller._time_ms == 500