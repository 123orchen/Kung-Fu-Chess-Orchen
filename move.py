class Move:
    MOVE_TYPE_NORMAL = 'normal'
    MOVE_TYPE_JUMP = 'jump'

    def __init__(self, piece, from_r, from_c, to_r, to_c, arrival_time, move_type=MOVE_TYPE_NORMAL):
        self.piece = piece
        self.from_r, self.from_c = from_r, from_c
        self.to_r, self.to_c = to_r, to_c
        self.arrival_time = arrival_time
        self.move_type = move_type

    def is_jump(self):
        return self.move_type == Move.MOVE_TYPE_JUMP
