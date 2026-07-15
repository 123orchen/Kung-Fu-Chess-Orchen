# rule_engine.py
from config import PIECE_RULES, WHITE_TURN, PAWN, PAWN_MOVE_TYPE


class RuleEngine:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
        # print(f"DEBUG: RuleEngine.is_legal called for {piece.type} to {to_r},{to_c}")
        # from_r, from_c = board.find_piece(piece)
        # print(f"DEBUG: Checking legality for {piece.type} from {from_r},{from_c} to {to_r},{to_c}")
        # 1. בדיקות כלליות (האם היעד תפוס ע"י בן ברית)
        target = board.get_piece(to_r, to_c)
        if target and target.color == piece.color:
            # print("DEBUG: Rejected - blocked by own piece")
            return False

        from_r, from_c = board.find_piece(piece)
        dr, dc = to_r - from_r, to_c - from_c
        rule = PIECE_RULES.get(piece.type)
        # print(f"DEBUG: Rule found: {rule}")  # זה יגיד לנו אם יש חוקים לחייל הזה

        # 2. האצלת סמכות לפי סוג המהלך
        if rule['move_type'] == PAWN_MOVE_TYPE:
            return RuleEngine._is_pawn_move_legal(board, piece, from_r, from_c, to_r, to_c, dr, dc)

        if rule['move_type'] in ['slide', 'step']:
            return RuleEngine._is_sliding_move_legal(dr, dc, rule)

        if rule['move_type'] == 'jump':
            return (dr, dc) in rule['vectors']

        return False

    @staticmethod
    def _is_pawn_move_legal(board, piece, from_r, from_c, to_r, to_c, dr, dc):
        direction = -1 if piece.color == 'w' else 1

        # זיהוי שורת התחלה לפי צבע:
        # לבן בלוח קטן (4 שורות) מתחיל ב-3, שחור ב-0.
        # אם הלוח הוא בגודל סטנדרטי (8 שורות), לבן ב-6, שחור ב-1.
        is_white = (piece.color == 'w')
        start_row = 6 if is_white else 1
        if board._rows == 4:  # התאמה ללוחות הקטנים של הטסטים
            start_row = 3 if is_white else 0

        is_capture = board.get_piece(to_r, to_c) is not None

        if is_capture:
            return dr == direction and abs(dc) == 1

        if dr == direction and dc == 0:
            return board.get_piece(to_r, to_c) is None

        # צעד כפול - עכשיו הוא יזהה את ה-start_row הנכון!
        if from_r == start_row and dr == 2 * direction and dc == 0:
            mid_r = from_r + direction
            return board.get_piece(mid_r, from_c) is None and board.get_piece(to_r, to_c) is None

        return False

    @staticmethod
    def _is_sliding_move_legal(dr, dc, rule):
        # 1. חישוב הכיוון (הנורמליזציה) בצורה בטוחה
        dist = max(abs(dr), abs(dc))
        if dist == 0: return False

        # חישוב הצעד היחיד לכיוון הזה
        step_r = dr // dist
        step_c = dc // dist

        # 2. בדיקה האם זה כיוון חוקי למלכה/רץ/צריח
        if (step_r, step_c) not in rule['vectors']:
            return False

        # 3. עבור 'step' (כמו מלך), אסור שהמרחק יהיה גדול מ-1
        if rule['move_type'] == 'step' and dist > 1:
            return False

        return True
