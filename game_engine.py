from move import Move
from pathValidator import PathValidator
from rule_engine import RuleEngine


class GameEngine:
    def __init__(self, board, scheduler):
        self._board = board
        self._scheduler = scheduler
        self._game_over = False  # הוספת דגל סטטוס

    def is_game_over(self):
        return self._game_over

    def process_time_step(self, current_time):
        due_moves = self._scheduler.get_due_moves(current_time + 100)
        due_moves.sort(key=lambda m: m.arrival_time)

        for m in due_moves:
            # אם המשחק כבר נגמר, לא מבצעים מהלכים נוספים מהתור
            if self._game_over: break

            self._board.execute_move(m.from_r, m.from_c, m.to_r, m.to_c)

            # בדיקה אם המלך נאכל
            # נניח שהיריב הוא הצבע השני. אפשר לזהות זאת לפי piece.color
            opponent_color = 'b' if m.piece.color == 'w' else 'w'
            if not self._board.is_king_on_board(opponent_color):
                self._game_over = True

    def request_move(self, piece, to_r, to_c, arrival_time):
        # print(f"DEBUG: request_move called for {piece.type} to {to_r},{to_c}")
        # print(f"DEBUG: Game over status is: {self._game_over}")
        if self._game_over:
            # print("DEBUG: Request rejected because game is over!")
            return False

        # 1. בדיקת חוקיות
        if not RuleEngine.is_legal(self._board, piece, to_r, to_c):
            # print(f"DEBUG: FAILED at RuleEngine for move to {to_r},{to_c}")
            return False

        # 2. בדיקת מסלול
        r, c = self._board.find_piece(piece)
        if not PathValidator.is_path_clear(self._board, self._scheduler, r, c, to_r, to_c):
            # print(f"DEBUG: FAILED at PathValidator for move to {to_r},{to_c}")
            return False

        # 3. בדיקת תזמון
        if self._scheduler.is_route_blocked(piece, to_r, to_c):
            # print(f"DEBUG: FAILED at Scheduler for move to {to_r},{to_c}")
            return False

        # ביצוע
        move = Move(piece, r, c, to_r, to_c, arrival_time)
        self._scheduler.schedule(move)
        return True
