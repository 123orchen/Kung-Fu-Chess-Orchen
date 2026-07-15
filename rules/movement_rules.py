class PathValidator:
    @staticmethod
    def is_path_clear(board, scheduler, from_r, from_c, to_r, to_c):
        piece = board.get_piece(from_r, from_c)
        if not piece or piece.is_jumping():
            return True

        # חישוב הכיוון (צעד יחיד)
        dr = 0 if to_r == from_r else (1 if to_r > from_r else -1)
        dc = 0 if to_c == from_c else (1 if to_c > from_c else -1)

        curr_r, curr_c = from_r + dr, from_c + dc

        # לולאה שעוברת על כל המשבצות עד היעד (לא כולל היעד)
        while curr_r != to_r or curr_c != to_c:
            if board.get_piece(curr_r, curr_c) is not None:
                return False
            # בדיקת pending moves
            if scheduler and scheduler.is_square_occupied_by_pending_move(curr_r, curr_c):
                return False

            curr_r += dr
            curr_c += dc

        return True
