# rule_engine.py
from config import PIECE_RULES, WHITE_TURN, PAWN


class RuleEngine:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
        target = board.get_piece(to_r, to_c)
        if target and target.color == piece.color:
            return False
        from_r, from_c = board.find_piece(piece)
        dr, dc = to_r - from_r, to_c - from_c
        rule = PIECE_RULES.get(piece.type)

        if rule['move_type'] == PAWN:
            direction = -1 if piece.color == WHITE_TURN else 1
            is_capture = board.get_piece(to_r, to_c) is not None
            if is_capture: return dr == direction and abs(dc) == 1
            return dr == direction and dc == 0

        if rule['move_type'] in ['slide', 'step']:
            dist = max(abs(dr), abs(dc))
            if dist == 0: return False
            if rule['move_type'] == 'step' and dist > 1: return False

            # החלק החדש: חישוב הכיוון המדויק (step_r, step_c)
            # אם נחלק את השינוי במרחק, נקבל את הווקטור היחידה
            step_r = dr // dist
            step_c = dc // dist

            # עכשיו נבדוק אם כיוון הצעד הזה קיים ברשימת הווקטורים המותרים
            return (step_r, step_c) in rule['vectors']
        if rule['move_type'] == 'jump':
            return (dr, dc) in rule['vectors']

        return False
