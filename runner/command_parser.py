from config import VALID_COLORS, VALID_PIECES
from model.piece import Piece


class InputParser:
    @staticmethod
    def is_valid_token(token):
        if token == '.':
            return True
        if not isinstance(token, str) or len(token) != 2:
            return False
        color, p_type = token[0], token[1]
        return color in VALID_COLORS and p_type in VALID_PIECES

    @staticmethod
    def parse_board(data):
        grid = []
        for line in data.splitlines():
            stripped = line.strip()
            if not stripped or "Board:" in stripped or "Commands:" in stripped:
                continue

            tokens = stripped.split()
            row = []
            for token in tokens:
                if token == '.':
                    row.append(None)
                else:
                    row.append(Piece(token[0], token[1]))
            grid.append(row)
        return grid

    @staticmethod
    def parse_board_from_list(board_data):
        grid = []
        for row_data in board_data:
            if "Board:" in row_data or "Commands:" in row_data:
                continue

            row = []
            for token in row_data:
                if token == '.':
                    row.append(None)
                else:
                    row.append(Piece(token[0], token[1]))
            grid.append(row)
        return grid
