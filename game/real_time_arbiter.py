class MoveScheduler:
    def __init__(self):
        self._pending_moves = []

    def schedule(self, move):
        self._pending_moves.append(move)

    def is_piece_moving(self, piece):
        return any(m.piece == piece for m in self._pending_moves)

    def get_due_moves(self, current_time):
        due = [m for m in self._pending_moves if m.arrival_time <= current_time]
        self._pending_moves = [m for m in self._pending_moves if m.arrival_time > current_time]
        return due

    def get_airborne_piece_at(self, r, c, current_time):
        for move in self._pending_moves:
            if move.is_jump() and move.arrival_time >= current_time:
                if move.from_r == r and move.from_c == c:
                    return move.piece
        return None

    def get_active_airborne_positions(self, current_time):
        return {
            (move.from_r, move.from_c): move.piece
            for move in self._pending_moves
            if move.is_jump() and move.arrival_time >= current_time
        }

    def is_route_blocked(self, piece, to_r, to_c):
        for move in self._pending_moves:
            if move.piece == piece or move.is_jump():
                continue

            if move.to_r == to_r and move.to_c == to_c:
                return True

            if move.from_r == move.to_r and to_r == move.from_r:
                if min(move.from_c, move.to_c) <= to_c <= max(move.from_c, move.to_c):
                    return True

            if move.from_c == move.to_c and to_c == move.from_c:
                if min(move.from_r, move.to_r) <= to_r <= max(move.from_r, move.to_r):
                    return True

        return False

    def is_square_occupied_by_pending_move(self, r, c):
        return any(m.to_r == r and m.to_c == c for m in self._pending_moves)
