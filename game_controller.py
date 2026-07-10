from moveResolver import MoveResolver
from config import CELL_SIZE, WHITE_TURN


class GameController:
    def __init__(self, board):
        self._board = board
        self._selected_piece = None

    def handle_click(self, x, y):
        col, row = x // CELL_SIZE, y // CELL_SIZE
        target = self._board.get_piece(row, col)

        if self._selected_piece:
            if MoveResolver.is_legal(self._board, self._selected_piece, row, col):
                r, c = self._board.find_piece(self._selected_piece)
                self._board.execute_move(r, c, row, col)
            self._selected_piece = None
        else:
            if target and target.color == WHITE_TURN:
                self._selected_piece = target

    def handle_wait(self, ms):
        pass  # לא עושה כלום בלוח, רק מקדם זמן
