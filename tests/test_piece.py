from piece import Piece

def test_piece_creation():
    p = Piece('w', 'K')
    assert str(p) == "wK"
    assert p.color == 'w'

def test_is_valid_token():
    assert Piece.is_valid_token('wK') is True
    assert Piece.is_valid_token('.') is True
    assert Piece.is_valid_token('xZ') is False  # שגיאה
    assert Piece.is_valid_token('wKK') is False # ארוך מדי