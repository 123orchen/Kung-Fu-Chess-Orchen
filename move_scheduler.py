class MoveScheduler:
    def __init__(self):
        self._pending_moves = []

    def schedule(self, move):
        self._pending_moves.append(move)

    def is_piece_moving(self, piece):
        return any(m.piece == piece for m in self._pending_moves)

    def get_due_moves(self, current_time):
        # 1. מוצאים את המהלכים שזמנם הגיע
        due = [m for m in self._pending_moves if m.arrival_time <= current_time]

        # 2. חשוב מאוד: מוחקים אותם מהרשימה כדי שהכלי יהיה "פנוי" למהלך הבא
        for m in due:
            self._pending_moves.remove(m)

        return due

    def is_route_blocked(self, piece, to_r, to_c):
        for move in self._pending_moves:
            if move.piece.color != piece.color:
                # בדיקת חפיפה בשורה או בטור
                if move.to_r == to_r or move.to_c == to_c:
                    return True
        return False
