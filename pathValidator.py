class PathValidator:
    @staticmethod
    def is_path_clear(board, scheduler, from_r, from_c, to_r, to_c):
        piece = board.get_piece(from_r, from_c)
        if piece.is_jumping(): return True

        dr = 0 if to_r == from_r else (1 if to_r > from_r else -1)
        dc = 0 if to_c == from_c else (1 if to_c > from_c else -1)

        curr_r, curr_c = from_r + dr, from_c + dc

        while (curr_r, curr_c) != (to_r, to_c):
            # אם יש כלי בדרך *לפני* שהגענו ליעד - זו חסימה
            if board.get_piece(curr_r, curr_c) is not None:
                return False
            # האם מישהו אחר כבר תזמן לעבור כאן בזמן הזה?
            if scheduler.is_square_occupied_by_pending_move(curr_r, curr_c):
                return False
            curr_r, curr_c = curr_r + dr, curr_c + dc

            # הגענו לכאן? הדרך פנויה.
        return True