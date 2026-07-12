# piece.py
from config import KNIGHT


class Piece:
    def __init__(self, color, type):
        self._color = color
        self._type = type

    @property
    def color(self): return self._color

    @property
    def type(self): return self._type

    def is_jumping(self):
        return self._type == KNIGHT  # השתמשי בקבוע KNIGHT מה-config



