from config import KING, PAWN, QUEEN, WHITE_TURN


class Board:
    def __init__(self, grid):
        self._grid = grid
        self._rows = len(grid)
        self._cols = len(grid[0]) if self._rows > 0 else 0
        self._piece_locations = {}
        for r in range(self._rows):
            for c in range(self._cols):
                if self._grid[r][c]:
                    self._piece_locations[self._grid[r][c]] = (r, c)

    def execute_move(self, from_r, from_c, to_r, to_c):
        piece = self._grid[from_r][from_c]
        if not piece:
            return None

        target = self._grid[to_r][to_c]
        if target and target in self._piece_locations:
            del self._piece_locations[target]

        self._piece_locations[piece] = (to_r, to_c)

        self._grid[to_r][to_c] = piece
        self._grid[from_r][from_c] = None

        if piece.type == PAWN:
            last_row = 0 if piece.color == WHITE_TURN else (self._rows - 1)
            if to_r == last_row:
                piece.promote()

        return target

    def snapshot_state(self):
        return [row[:] for row in self._grid], dict(self._piece_locations)

    def restore_state(self, state):
        grid_snapshot, piece_locations_snapshot = state
        self._grid = [row[:] for row in grid_snapshot]
        self._piece_locations = dict(piece_locations_snapshot)

    def find_piece(self, piece):
        return self._piece_locations.get(piece)

    def get_piece(self, row, col):
        return self._grid[row][col] if 0 <= row < self._rows and 0 <= col < self._cols else None

    def remove_piece(self, row, col):
        piece = self.get_piece(row, col)
        if not piece:
            return None

        if piece in self._piece_locations:
            del self._piece_locations[piece]

        self._grid[row][col] = None
        return piece

    def display(self):
        for row in self._grid:
            print(" ".join([str(p) if p else "." for p in row]))

    def get_grid(self):
        return self._grid

    def is_king_on_board(self, color):
        for piece in self._piece_locations:
            if piece.type == KING and piece.color == color:
                return True
        return False
