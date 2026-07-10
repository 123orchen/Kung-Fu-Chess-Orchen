import pytest
from piece import Piece
from board import Board
from moveResolver import MoveResolver
from config import PAWN, WHITE_TURN, BLACK_TURN


def test_pawn_movement():
    # לוח עם חייל לבן ב-1,1
    grid = [[None, None, None],
            [None, Piece(WHITE_TURN, PAWN), None],
            [None, None, None]]
    board = Board(grid)
    pawn = board.get_piece(1, 1)

    # בדיקת צעד יחיד קדימה (למעלה) - חוקי
    assert MoveResolver.is_legal(board, pawn, 0, 1) is True

    # בדיקת צעד כפול - לא חוקי
    assert MoveResolver.is_legal(board, pawn, -1, 1) is False


def test_pawn_capture():
    # חייל לבן ב-1,1, צריח שחור ב-0,0 (אלכסון), וצריח שחור ב-0,1 (קדימה)
    grid = [[Piece(BLACK_TURN, 'R'), Piece(BLACK_TURN, 'R'), None],
            [None, Piece(WHITE_TURN, PAWN), None],
            [None, None, None]]
    board = Board(grid)
    pawn = board.get_piece(1, 1)

    # 1. בדיקת תפיסה באלכסון - חוקי
    assert MoveResolver.is_legal(board, pawn, 0, 0) is True

    # 2. בדיקת תפיסה ישרה (קדימה) - לא חוקי כי יש שם כלי!
    # לפי חוקי השחמט, חייל לא יכול לתפוס כלי שנמצא בדיוק מולו.
    assert MoveResolver.is_legal(board, pawn, 0, 1) is False


def test_black_pawn_direction():
    # חייל שחור ב-1,1 - זז למטה ל-2,1
    grid = [[None, None, None],
            [None, Piece(BLACK_TURN, PAWN), None],
            [None, None, None]]
    board = Board(grid)
    pawn = board.get_piece(1, 1)

    # זז למטה (2,1) - חוקי
    assert MoveResolver.is_legal(board, pawn, 2, 1) is True
    # זז למעלה (0,1) - לא חוקי
    assert MoveResolver.is_legal(board, pawn, 0, 1) is False