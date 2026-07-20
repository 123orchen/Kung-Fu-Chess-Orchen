from config import LONG_REST_MS, SHORT_REST_MS, STATE_LONG_REST, STATE_SHORT_REST


class MoveScheduler:
    def __init__(self):
        self._pending_moves = []
        self._rest_until = {}  # piece -> (rest_end_time_ms, rest_kind, rest_duration_ms)

    def schedule(self, move):
        self._pending_moves.append(move)
        # A jump costs less rest than a standard move (per the game design doc).
        duration = SHORT_REST_MS if move.is_jump() else LONG_REST_MS
        kind = STATE_SHORT_REST if move.is_jump() else STATE_LONG_REST
        self._rest_until[move.piece] = (move.arrival_time + duration, kind, duration)

    def is_piece_moving(self, piece):
        return any(m.piece == piece for m in self._pending_moves)

    def is_piece_on_cooldown(self, piece, current_time):
        """Check if piece is still resting (moving or post-move rest)."""
        entry = self._rest_until.get(piece)
        if entry is None:
            return False
        end_time, _kind, _duration = entry
        return current_time < end_time

    def get_rest_kind(self, piece, current_time):
        """Returns 'long_rest' / 'short_rest' while resting, else None - used to pick the right animation."""
        entry = self._rest_until.get(piece)
        if entry is None:
            return None
        end_time, kind, _duration = entry
        return kind if current_time < end_time else None

    def get_cooldown_remaining_ms(self, piece, current_time):
        """Get remaining cooldown time in milliseconds (0 if no cooldown)"""
        entry = self._rest_until.get(piece)
        if entry is None:
            return 0
        end_time, _kind, _duration = entry
        return max(0, end_time - current_time)

    def get_cooldown_alpha(self, piece, current_time):
        """Get alpha value for cooldown overlay (0.0 to 1.0, 0=transparent)"""
        entry = self._rest_until.get(piece)
        if entry is None:
            return 0.0
        _end_time, _kind, duration = entry
        remaining = self.get_cooldown_remaining_ms(piece, current_time)
        if remaining <= 0 or duration <= 0:
            return 0.0
        return remaining / duration

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
