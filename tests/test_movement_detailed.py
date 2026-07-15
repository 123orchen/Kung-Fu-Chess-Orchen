import pytest
from model.piece import Piece

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
    p = Piece('w', type)
    assert p.is_valid_move(from_r, from_c, to_r, to_c) == expected