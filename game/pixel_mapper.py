from config import CELL_SIZE


class BoardMapper:
    @staticmethod
    def pixel_to_coords(x, y):
        return x // CELL_SIZE, y // CELL_SIZE
