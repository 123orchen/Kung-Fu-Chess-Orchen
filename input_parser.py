from piece import Piece


class InputParser:
    @staticmethod
    def parse_board_from_list(board_data):
        grid = []
        for row_data in board_data:
            # בודקים אם השורה היא מילת מפתח
            if "Board:" in row_data or "Commands:" in row_data: continue

            row = []
            for token in row_data:
                if token == '.':
                    row.append(None)
                else:
                    row.append(Piece(token[0], token[1]))
            grid.append(row)
        return grid