import pytest
from model.board import Board
from model.piece import Piece
from rules.rule_engine import RuleEngine


def make_board_with_piece(color, p_type, from_r, from_c):
    grid = [[None for _ in range(8)] for _ in range(8)]
    piece = Piece(color, p_type)
    grid[from_r][from_c] = piece
    return Board(grid), piece


@pytest.mark.parametrize("type, from_r, from_c, to_r, to_c, expected", [
    ('K', 0, 0, 0, 1, True),  # מלך: צעד אחד חוקי
    ('K', 0, 0, 0, 2, False), # מלך: שני צעדים לא חוקי
    ('R', 0, 0, 0, 5, True),  # צריח: ישר חוקי
    ('R', 0, 0, 1, 1, False), # צריח: אלכסוני לא חוקי
    ('B', 0, 0, 2, 2, True),  # רץ: אלכסוני חוקי
    ('N', 0, 0, 2, 1, True),  # סוס: L חוקי
    ('Q', 0, 0, 5, 5, True),  # מלכה: אלכסוני חוקי
])
def test_piece_moves(type, from_r, from_c, to_r, to_c, expected):
    board, piece = make_board_with_piece('w', type, from_r, from_c)
    assert RuleEngine.is_legal(board, piece, to_r, to_c) == expected
