from config import KING, BISHOP, ROOK, QUEEN, KNIGHT, PAWN, WHITE_TURN, BLACK_TURN, VALID_COLORS, VALID_PIECES


class Piece:
    def __init__(self, color, type):
        self._color = color
        self._type = type

    @property
    def color(self):
        return self._color

    @property
    def type(self):
        return self._type

    def is_jumping(self):
        return self._type == KNIGHT

    # זו המתודה שחסרה לך!
    def get_delta(self, dr, dc):
        return (0 if dr == 0 else dr // abs(dr),
                0 if dc == 0 else dc // abs(dc))

    def is_valid_move(self, dr, dc, is_capture=False):
        if self._type == PAWN:
            direction = -1 if self._color == WHITE_TURN else 1
            if is_capture:
                return dr == direction and abs(dc) == 1
            return dr == direction and dc == 0

        rules = {
            KING: lambda dr, dc: abs(dr) <= 1 and abs(dc) <= 1,
            ROOK: lambda dr, dc: dr == 0 or dc == 0,
            BISHOP: lambda dr, dc: abs(dr) == abs(dc),
            QUEEN: lambda dr, dc: abs(dr) == abs(dc) or dr == 0 or dc == 0,
            KNIGHT: lambda dr, dc: {abs(dr), abs(dc)} == {1, 2}
        }
        return rules.get(self._type, lambda dr, dc: False)(dr, dc)

    @staticmethod
    def is_valid_token(token):
        if token == '.': return True
        if len(token) != 2: return False
        return token[0] in VALID_COLORS and token[1] in VALID_PIECES

    def __str__(self):
        return f"{self._color}{self._type}"
