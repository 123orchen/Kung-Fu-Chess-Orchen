from move import Move
from moveResolver import MoveResolver


class GameEngine:
    def __init__(self, board, scheduler):
        self._board = board
        self._scheduler = scheduler

    def process_time_step(self, current_time):
        due_moves = self._scheduler.get_due_moves(current_time)
        for m in due_moves:
            self._board.execute_move(m.from_r, m.from_c, m.to_r, m.to_c)

    def request_move(self, piece, to_r, to_c, arrival_time):
        # 1. בדיקה אם הכלי כבר בתנועה (No Premove)
        if self._scheduler.is_piece_moving(piece):
            return False

        # 2. בדיקת התנגשות (Test 1)
        if self._scheduler.is_route_blocked(piece, to_r, to_c):
            return False

        # 3. בדיקת חוקיות
        if MoveResolver.is_legal(self._board, piece, to_r, to_c):
            r, c = self._board.find_piece(piece)
            move = Move(piece, r, c, to_r, to_c, arrival_time)
            self._scheduler.schedule(move)
            return True
        return False
