class PathValidator:
    @staticmethod
    def is_path_clear(board, from_r, from_c, to_r, to_c):
        piece = board.get_piece(from_r, from_c)
        if piece.is_jumping(): return True  # סוס לא נחסם

        dr, dc = piece.get_delta(to_r - from_r, to_c - from_c)
        curr_r, curr_c = from_r + dr, from_c + dc

        while (curr_r, curr_c) != (to_r, to_c):
            if board.get_piece(curr_r, curr_c) is not None:
                return False
            curr_r, curr_c = curr_r + dr, curr_c + dc
        return True