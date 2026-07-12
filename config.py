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

PIECE_RULES = {
    'P': {'move_type': 'pawn'},
    'R': {'move_type': 'slide', 'vectors': [(0,1), (0,-1), (1,0), (-1,0)]},
    'B': {'move_type': 'slide', 'vectors': [(1,1), (1,-1), (-1,1), (-1,-1)]},
    'N': {'move_type': 'jump', 'vectors': [(1,2), (1,-2), (-1,2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]},
    'Q': {'move_type': 'slide', 'vectors': [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]},
    'K': {'move_type': 'step', 'vectors': [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]}
}