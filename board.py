class Board:
    def __init__(self, grid):
        self._grid = grid
        self._rows = len(grid)
        self._cols = len(grid[0]) if self._rows > 0 else 0
        self._piece_locations = {}  # מילון לשמירת מיקומים

        # סריקה ראשונית בלבד
        for r in range(self._rows):
            for c in range(self._cols):
                if self._grid[r][c]:
                    self._piece_locations[self._grid[r][c]] = (r, c)

    def execute_move(self, from_r, from_c, to_r, to_c):
        piece = self._grid[from_r][from_c]
        target = self._grid[to_r][to_c]

        # אם יש תפיסה, נקה מהמילון
        if target:
            del self._piece_locations[target]

        self._grid[to_r][to_c] = piece
        self._grid[from_r][from_c] = None
        self._piece_locations[piece] = (to_r, to_c)

    def find_piece(self, piece):
        return self._piece_locations.get(piece)

    def move_piece(self, from_r, from_c, to_r, to_c):
        piece = self._grid[from_r][from_c]
        # עדכון המטריצה
        self._grid[to_r][to_c] = piece
        self._grid[from_r][from_c] = None
        # עדכון המיקום במילון (פעולה של O(1))
        self._piece_locations[piece] = (to_r, to_c)
        # אם הייתה שם תפיסה, נמחק את הכלי מהמילון
        # (זה יקרה בשיפור נוסף ב-GameController)

    def get_piece(self, row, col):
        if 0 <= row < self._rows and 0 <= col < self._cols:
            return self._grid[row][col]
        return None

    def is_inside(self, row, col):
        return 0 <= row < self._rows and 0 <= col < self._cols

    def display(self):
        for row in self._grid:
            print(" ".join([str(p) if p else "." for p in row]))

