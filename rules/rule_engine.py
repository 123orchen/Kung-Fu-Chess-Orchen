# rule_engine.py
from config import PAWN_MOVE_TYPE, PIECE_RULES, WHITE_TURN


class RuleEngine:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
        if to_r < 0 or to_r >= board._rows or to_c < 0 or to_c >= board._cols:
            return False

        target = board.get_piece(to_r, to_c)
        if target and target.color == piece.color:
            return False

        from_r, from_c = board.find_piece(piece)
        if from_r is None or from_c is None:
            return False

        dr, dc = to_r - from_r, to_c - from_c
        rule = PIECE_RULES.get(piece.type)
        if not rule:
            return False

        if rule['move_type'] == PAWN_MOVE_TYPE:
            return RuleEngine._is_pawn_move_legal(board, piece, from_r, from_c, to_r, to_c, dr, dc)

        if rule['move_type'] in ['slide', 'step']:
            return RuleEngine._is_sliding_move_legal(dr, dc, rule)

        if rule['move_type'] == 'jump':
            return (dr, dc) in rule['vectors']

        return False

    @staticmethod
    def _is_pawn_move_legal(board, piece, from_r, from_c, to_r, to_c, dr, dc):
        direction = -1 if piece.color == WHITE_TURN else 1

        is_white = piece.color == WHITE_TURN
        start_row = board._rows - 2 if is_white else 1

        is_capture = board.get_piece(to_r, to_c) is not None

        if is_capture:
            return dr == direction and abs(dc) == 1

        if dr == direction and dc == 0:
            return board.get_piece(to_r, to_c) is None

        if from_r == start_row and dr == 2 * direction and dc == 0:
            mid_r = from_r + direction
            return board.get_piece(mid_r, from_c) is None and board.get_piece(to_r, to_c) is None

        return False

    @staticmethod
    def _is_sliding_move_legal(dr, dc, rule):
        dist = max(abs(dr), abs(dc))
        if dist == 0:
            return False

        # Both components must divide evenly by dist, or this isn't actually
        # a straight/diagonal line (e.g. dr=2,dc=1 is knight-shaped, not a
        # rook/bishop move - plain integer division was silently accepting it).
        if dr % dist != 0 or dc % dist != 0:
            return False

        step_r = dr // dist
        step_c = dc // dist

        if (step_r, step_c) not in rule['vectors']:
            return False

        # 'step' pieces (e.g. King) are implicitly capped at distance 1.
        # Any move_type can also declare an explicit 'max_distance' (e.g. a
        # Drone that reaches 2 squares) without needing a new move_type.
        max_distance = rule.get('max_distance')
        if max_distance is None and rule['move_type'] == 'step':
            max_distance = 1
        if max_distance is not None and dist > max_distance:
            return False

        return True
