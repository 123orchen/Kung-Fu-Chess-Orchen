# rule_engine.py
from config import PIECE_RULES, WHITE_TURN


class RuleEngine:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
        from_r, from_c = board.find_piece(piece)
        dr, dc = to_r - from_r, to_c - from_c
        rule = PIECE_RULES.get(piece.type)

        if rule['move_type'] == 'pawn':
            direction = -1 if piece.color == WHITE_TURN else 1
            is_capture = board.get_piece(to_r, to_c) is not None
            if is_capture: return dr == direction and abs(dc) == 1
            return dr == direction and dc == 0

        if rule['move_type'] in ['slide', 'step']:
            # לוגיקה של slide (צריח/רץ/מלכה) או step (מלך)
            # ב-slide אפשר לזוז מרחק גדול, ב-step רק 1
            dist = max(abs(dr), abs(dc))
            if rule['move_type'] == 'step' and dist > 1: return False

            # בדיקת וקטור (האם המהלך בקו ישר לאחד ה-vectors)
            # כאן צריך לוודא ש-(dr, dc) הוא כפולה של אחד הוקטורים
            return any((dr == v[0] * dist and dc == v[1] * dist) for v in rule['vectors'])

        if rule['move_type'] == 'jump':
            return (dr, dc) in rule['vectors']

        return False