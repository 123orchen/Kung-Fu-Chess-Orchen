# config.py
CELL_SIZE = 100
WHITE_TURN = 'w'
BLACK_TURN = 'b'

# Piece Types
PAWN = 'P'
ROOK = 'R'
KNIGHT = 'N'
BISHOP = 'B'
QUEEN = 'Q'
KING = 'K'

VALID_COLORS = [WHITE_TURN, BLACK_TURN]
VALID_PIECES = [KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN]

PAWN_MOVE_TYPE = 'pawn'
JUMP_DURATION_MS = 1000
MOVE_DURATION_MS = 1000
COMMAND_CLICK = 'click'
COMMAND_JUMP = 'jump'
COMMAND_WAIT = 'wait'
COMMAND_PRINT = 'print'
COMMAND_PRINT_BOARD = 'board'

PIECE_RULES = {
    PAWN: {'move_type': PAWN_MOVE_TYPE},
    ROOK: {'move_type': 'slide', 'vectors': [(0,1), (0,-1), (1,0), (-1,0)]},
    BISHOP: {'move_type': 'slide', 'vectors': [(1,1), (1,-1), (-1,1), (-1,-1)]},
    KNIGHT: {'move_type': 'jump', 'vectors': [(1,2), (1,-2), (-1,2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]},
    QUEEN: {'move_type': 'slide', 'vectors': [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]},
    KING: {'move_type': 'step', 'vectors': [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]}
}