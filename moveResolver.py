from pathValidator import PathValidator


class MoveResolver:
    @staticmethod
    def is_legal(board, piece, to_r, to_c):
        r, c = board.find_piece(piece)
        dr, dc = to_r - r, to_c - c
        target = board.get_piece(to_r, to_c)
        is_capture = target is not None

        # בדיקה צורנית + מסלול + חוקי צבע
        if not piece.is_valid_move(dr, dc, is_capture): return False
        if not PathValidator.is_path_clear(board, r, c, to_r, to_c): return False
        if is_capture and target.color == piece.color: return False

        return True
