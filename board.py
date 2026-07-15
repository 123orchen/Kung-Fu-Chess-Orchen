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
        if not piece: return

        # 1. ניקוי היעד במילון (אם יש שם כלי שנאכל)
        target = self._grid[to_r][to_c]
        if target and target in self._piece_locations:
            del self._piece_locations[target]

        # 2. עדכון המיקום של הכלי שזז במילון
        self._piece_locations[piece] = (to_r, to_c)

        # 3. הזזת הכלי בתוך הגריד עצמו
        self._grid[to_r][to_c] = piece
        self._grid[from_r][from_c] = None

        # 4. קידום חייל - זה החלק הקריטי ביותר
        if piece.type == 'P':
            last_row = 0 if piece.color == 'w' else (self._rows - 1)
            if to_r == last_row:
                piece.promote()
                # חשוב: אחרי פרומושן ה-type השתנה, וודאי שזה לא שובר את המילון
                # בדרך כלל אין צורך לעדכן את המפתח במילון כי האובייקט נשאר אותו אובייקט

    def find_piece(self, piece):
        return self._piece_locations.get(piece)

    def get_piece(self, row, col):
        return self._grid[row][col] if 0 <= row < self._rows and 0 <= col < self._cols else None

    def display(self):
        for row in self._grid: print(" ".join([str(p) if p else "." for p in row]))

        # נוסיף מתודה שתבדוק אם המלך עדיין קיים על הלוח

    def is_king_on_board(self, color):
        for piece in self._piece_locations:
            if piece.type == 'K' and piece.color == color:
                return True
        return False
