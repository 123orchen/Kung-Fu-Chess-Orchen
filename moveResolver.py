from config import PAWN
from pathValidator import PathValidator


class MoveResolver:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
        r, c = board.find_piece(piece)
        dr, dc = to_r - r, to_c - c
        target = board.get_piece(to_r, to_c)
        is_capture = target is not None

        # 1. בדיקה צורנית בסיסית
        if not piece.is_valid_move(dr, dc, is_capture):
            return False

        # 2. חוקים מחמירים לחיילים
        if piece.type == PAWN:
            # חייל לא זז 2 משבצות (לפחות לא כרגע)
            if abs(dr) > 1: return False

            # אם הוא מנסה לזוז ישר (dc == 0), חייב להיות ריק
            if dc == 0 and is_capture: return False

            # אם הוא מנסה לתפוס (abs(dc) == 1), חייב להיות כלי
            if abs(dc) == 1 and not is_capture: return False

            # חייל לא יכול לתפוס ישר (זה כבר מכוסה ב-is_valid_move אבל נוודא)
            if dc == 0 and is_capture: return False

        # 3. בדיקת מסלול (לכלים שמחליקים)
        if not PathValidator.is_path_clear(board, r, c, to_r, to_c):
            return False

        # 4. לא תופסים חברים
        if is_capture and target.color == piece.color:
            return False

        return True
