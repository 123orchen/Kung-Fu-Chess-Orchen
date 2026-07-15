from config import KNIGHT, PAWN, PAWN_MOVE_TYPE, PIECE_RULES, QUEEN, VALID_COLORS, VALID_PIECES, WHITE_TURN


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

    def is_valid_move(self, from_r, from_c, to_r, to_c):
        if from_r == to_r and from_c == to_c:
            return False

        dr, dc = to_r - from_r, to_c - from_c
        rule = PIECE_RULES.get(self._type)
        if not rule:
            return False

        move_type = rule['move_type']
        if move_type == PAWN_MOVE_TYPE:
            direction = -1 if self._color == WHITE_TURN else 1
            if dr == direction and abs(dc) == 1:
                return True
            if dr == direction and dc == 0:
                return True
            if from_r == (6 if self._color == WHITE_TURN else 1) and dr == 2 * direction and dc == 0:
                return True
            return False

        if move_type in ['slide', 'step']:
            dist = max(abs(dr), abs(dc))
            if dist == 0:
                return False

            step_r = dr // dist
            step_c = dc // dist
            if (step_r, step_c) not in rule['vectors']:
                return False
            if move_type == 'step' and dist > 1:
                return False
            return True

        if move_type == 'jump':
            return (dr, dc) in rule['vectors']

        return False
