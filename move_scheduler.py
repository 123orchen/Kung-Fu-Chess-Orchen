class MoveScheduler:
    def __init__(self):
        self._pending_moves = []

    def schedule(self, move):
        self._pending_moves.append(move)

    def is_piece_moving(self, piece):
        return any(m.piece == piece for m in self._pending_moves)

    def get_due_moves(self, current_time):
        due = [m for m in self._pending_moves if m.arrival_time < current_time]
        for m in due: self._pending_moves.remove(m)
        return due