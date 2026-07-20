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

# --- Rest / cooldown (Kung Fu Chess time-based logic) ---
# After a piece finishes a move it can't move again until its rest ends.
# A jump ("defensive ability") costs less rest than a standard move.
LONG_REST_MS = 10000   # rest after a standard move (kept as-is - existing tests depend on this value)
SHORT_REST_MS = 3000   # rest after a jump-in-place - shorter, per the game design doc

# Animation state names (must match the folder names under graphics/assets/pieces_mine/<piece>/states/)
STATE_IDLE = 'idle'
STATE_MOVE = 'move'
STATE_JUMP = 'jump'
STATE_LONG_REST = 'long_rest'
STATE_SHORT_REST = 'short_rest'

PIECE_RULES = {
    PAWN: {'move_type': PAWN_MOVE_TYPE},
    ROOK: {'move_type': 'slide', 'vectors': [(0,1), (0,-1), (1,0), (-1,0)]},
    BISHOP: {'move_type': 'slide', 'vectors': [(1,1), (1,-1), (-1,1), (-1,-1)]},
    KNIGHT: {'move_type': 'jump', 'vectors': [(1,2), (1,-2), (-1,2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]},
    QUEEN: {'move_type': 'slide', 'vectors': [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]},
    KING: {'move_type': 'step', 'vectors': [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]}
}