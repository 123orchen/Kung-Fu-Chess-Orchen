import pytest
from board import Board
from piece import Piece
from game_controller import GameController


def test_rook_blocked_by_own_piece():
    # wR ב-0,0 ו-wP ב-0,1. צריח לא יכול לזוז ל-0,2
    grid = [[Piece('w', 'R'), Piece('w', 'P'), None]]
    board = Board(grid)
    controller = GameController(board)

    # ניסיון תזוזה מצד לצד (0,0 ל-0,2)
    controller.handle_click(50, 50)  # בחר צריח
    controller.handle_click(250, 50)  # ניסיון לעבור דרך החייל

    # הצריח אמור להישאר במקום
    assert board.get_piece(0, 0).type == 'R'
    assert board.get_piece(0, 1).type == 'P'


def test_knight_jumps_over_blockers():
    # סוס ב-0,0 וחייל ב-0,1. סוס יכול לקפוץ ל-2,1
    grid = [[Piece('w', 'N'), Piece('w', 'P'), None],
            [None, None, None],
            [None, None, None]]
    board = Board(grid)
    controller = GameController(board)

    controller.handle_click(50, 50)  # בחר סוס
    controller.handle_click(150, 250)  # תזוזה ל-2,1

    assert board.get_piece(2, 1) is not None
    assert board.get_piece(2, 1).type == 'N'


def test_cannot_capture_own_piece():
    # צריח ב-0,0 וחייל לבן ב-0,2. לא יכול לתפוס אותו
    grid = [[Piece('w', 'R'), None, Piece('w', 'P')]]
    board = Board(grid)
    controller = GameController(board)

    controller.handle_click(50, 50)
    controller.handle_click(250, 50)

    # הצריח לא זז
    assert board.get_piece(0, 0).type == 'R'
    assert board.get_piece(0, 2).type == 'P'


def test_rook_captures_enemy():
    # צריח לבן ב-0,0 וחייל שחור ב-0,2
    grid = [[Piece('w', 'R'), None, Piece('b', 'P')]]
    board = Board(grid)
    controller = GameController(board)

    controller.handle_click(50, 50)
    controller.handle_click(250, 50)

    # הצריח תפס את החייל
    assert board.get_piece(0, 2).type == 'R'
    assert board.get_piece(0, 2).color == 'w'