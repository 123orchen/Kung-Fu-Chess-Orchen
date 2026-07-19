class MoveScheduler:
    COOLDOWN_MS = 10000  # 10 seconds cooldown after moving
    
    def __init__(self):
        self._pending_moves = []
        self._piece_last_move_time = {}  # Track last move time for cooldown

    def schedule(self, move):
        self._pending_moves.append(move)
        # Record when this piece is scheduled to move
        self._piece_last_move_time[move.piece] = move.arrival_time

    def is_piece_moving(self, piece):
        return any(m.piece == piece for m in self._pending_moves)

    def is_piece_on_cooldown(self, piece, current_time):
        """Check if piece is still in cooldown period after moving"""
        if piece not in self._piece_last_move_time:
            return False
        last_move_time = self._piece_last_move_time[piece]
        return current_time - last_move_time < self.COOLDOWN_MS
    
    def get_cooldown_remaining_ms(self, piece, current_time):
        """Get remaining cooldown time in milliseconds (0 if no cooldown)"""
        if piece not in self._piece_last_move_time:
            return 0
        last_move_time = self._piece_last_move_time[piece]
        elapsed = current_time - last_move_time
        remaining = self.COOLDOWN_MS - elapsed
        return max(0, remaining)
    
    def get_cooldown_alpha(self, piece, current_time):
        """Get alpha value for cooldown overlay (0.0 to 1.0, 0=transparent)"""
        remaining = self.get_cooldown_remaining_ms(piece, current_time)
        if remaining <= 0:
            return 0.0
        return remaining / self.COOLDOWN_MS

    def get_move_for_piece(self, piece):
        for move in self._pending_moves:
            if move.piece == piece:
                return move
        return None

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
