# rule_engine.py
from config import PAWN_MOVE_TYPE, PIECE_RULES, WHITE_TURN


class RuleEngine:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
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
        start_row = 6 if is_white else 1
        if board._rows == 4:
            start_row = 3 if is_white else 0

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

        step_r = dr // dist
        step_c = dc // dist

        if (step_r, step_c) not in rule['vectors']:
            return False

        if rule['move_type'] == 'step' and dist > 1:
            return False

        return True
