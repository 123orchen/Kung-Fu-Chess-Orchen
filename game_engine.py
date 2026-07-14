from move import Move
from pathValidator import PathValidator
from rule_engine import RuleEngine


class GameEngine:
    def __init__(self, board, scheduler):
        self._board = board
        self._scheduler = scheduler

    def process_time_step(self, current_time):
        due_moves = self._scheduler.get_due_moves(current_time)

        # מיון מהלכים לפי זמן הגעה - קריטי!
        due_moves.sort(key=lambda m: m.arrival_time)

        for m in due_moves:
            # בדיקה: האם הכלי המבצע עדיין נמצא בנקודת המוצא?
            # (יכול להיות שהוא כבר נאכל ע"י מהלך אחר שקרה ב-Time Step הזה)
            current_pos = self._board.find_piece(m.piece)
            if current_pos == (m.from_r, m.from_c):
                self._board.execute_move(m.from_r, m.from_c, m.to_r, m.to_c)

    def request_move(self, piece, to_r, to_c, arrival_time):
        # print(f"DEBUG: Trying move {piece} to {to_r}, {to_c}")

        # 1. בדיקת חוקיות בסיסית
        if not RuleEngine.is_legal(self._board, piece, to_r, to_c):
            # print("DEBUG: RuleEngine failed")
            return False

        # 2. בדיקת מסלול
        r, c = self._board.find_piece(piece)
        if not PathValidator.is_path_clear(self._board, self._scheduler, r, c, to_r, to_c):
            # print("DEBUG: PathValidator failed")
            return False

        # 3. בדיקת התנגשות
        if self._scheduler.is_route_blocked(piece, to_r, to_c):
            # print("DEBUG: Scheduler blocked the move")
            return False

        # 4. ביצוע
        # print("DEBUG: Move accepted!")
        move = Move(piece, r, c, to_r, to_c, arrival_time)
        self._scheduler.schedule(move)
        return True
