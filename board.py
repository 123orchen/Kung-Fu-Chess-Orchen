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
        target = self._grid[to_r][to_c]
        if target:
            del self._piece_locations[target]
        self._grid[to_r][to_c] = piece
        self._grid[from_r][from_c] = None
        self._piece_locations[piece] = (to_r, to_c)

    def find_piece(self, piece):
        return self._piece_locations.get(piece)

    def get_piece(self, row, col):
        return self._grid[row][col] if 0 <= row < self._rows and 0 <= col < self._cols else None

    def display(self):
        for row in self._grid: print(" ".join([str(p) if p else "." for p in row]))
