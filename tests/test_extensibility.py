"""
Proves the movement engine is genuinely extensible: a brand-new piece type
(e.g. a "Drone" that moves up to 2 squares in any direction, as mentioned in
the game design doc) can be added with a single PIECE_RULES entry, with zero
changes to rule_engine.py or movement_rules.py, thanks to the generic
'max_distance' support added there.

This test does NOT add a real piece to the game - it registers a temporary
custom piece type only for the duration of the test (via monkeypatch), to
demonstrate the mechanism without shipping a new piece nobody asked for.
"""
import pytest
import config
from model.board import Board
from model.piece import Piece
from rules.rule_engine import RuleEngine
from rules.movement_rules import PathValidator

CUSTOM_TYPE = 'X'
CUSTOM_RULE = {
    'move_type': 'slide',
    'vectors': [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    'max_distance': 2,
}


@pytest.fixture
def custom_piece_type(monkeypatch):
    monkeypatch.setitem(config.PIECE_RULES, CUSTOM_TYPE, CUSTOM_RULE)


def make_board(pieces):
    grid = [[None for _ in range(8)] for _ in range(8)]
    for (r, c), piece in pieces.items():
        grid[r][c] = piece
    return Board(grid)


def test_new_piece_type_can_move_within_its_declared_range(custom_piece_type):
    piece = Piece('w', CUSTOM_TYPE)
    board = make_board({(4, 4): piece})
    assert RuleEngine.is_legal(board, piece, 4, 6) is True   # 2 squares right
    assert RuleEngine.is_legal(board, piece, 2, 4) is True   # 2 squares up
    assert RuleEngine.is_legal(board, piece, 2, 2) is True   # 2 squares diagonal


def test_new_piece_type_cannot_exceed_its_declared_range(custom_piece_type):
    piece = Piece('w', CUSTOM_TYPE)
    board = make_board({(4, 4): piece})
    assert RuleEngine.is_legal(board, piece, 4, 7) is False  # 3 squares - too far
    assert RuleEngine.is_legal(board, piece, 6, 5) is False  # not a straight/diagonal line


def test_new_piece_type_path_is_still_blocked_correctly(custom_piece_type):
    piece = Piece('w', CUSTOM_TYPE)
    blocker = Piece('w', CUSTOM_TYPE)
    board = make_board({(4, 4): piece, (4, 5): blocker})
    assert PathValidator.is_path_clear(board, None, 4, 4, 4, 6) is False


def test_custom_piece_type_does_not_leak_into_real_game():
    # No fixture used here - proves the demo type from the tests above
    # never actually gets registered in the real, shipped PIECE_RULES.
    assert CUSTOM_TYPE not in config.PIECE_RULES
    assert CUSTOM_TYPE not in config.VALID_PIECES
