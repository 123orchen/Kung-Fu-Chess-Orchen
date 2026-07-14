class MoveScheduler:
    def __init__(self):
        self._pending_moves = []

    def schedule(self, move):
        self._pending_moves.append(move)

    def is_piece_moving(self, piece):
        return any(m.piece == piece for m in self._pending_moves)

    def get_due_moves(self, current_time):
        due = [m for m in self._pending_moves if m.arrival_time <= current_time]

        # יוצרים רשימה חדשה ללא המהלכים שמסרנו
        self._pending_moves = [m for m in self._pending_moves if m.arrival_time > current_time]

        return due

    def is_route_blocked(self, piece, to_r, to_c):
        for move in self._pending_moves:
            # אם זה אותו כלי, אל תחסום את עצמך!
            if move.piece == piece: continue

            if move.to_r == to_r and move.to_c == to_c:
                return True
        return False

    def is_square_occupied_by_pending_move(self, r, c):
        return any(m.to_r == r and m.to_c == c for m in self._pending_moves)
