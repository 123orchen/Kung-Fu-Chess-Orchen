from config import KNIGHT, QUEEN, VALID_COLORS, VALID_PIECES


class Piece:
    def __init__(self, color, type):
        self._color = color
        self._type = type

    @property
    def color(self): return self._color

    @property
    def type(self): return self._type

    def promote(self):
        self._type = QUEEN

    def __str__(self):
        return f"{self._color}{self._type}"

    def is_jumping(self):
        return self._type == KNIGHT

    @classmethod
    def is_valid_token(cls, token):
        if token == '.':
            return True
        if not isinstance(token, str) or len(token) != 2:
            return False
        color, p_type = token[0], token[1]
        return color in VALID_COLORS and p_type in VALID_PIECES
