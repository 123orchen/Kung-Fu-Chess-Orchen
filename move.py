class Move:
    def __init__(self, piece, from_r, from_c, to_r, to_c, arrival_time):
        self.piece = piece
        self.from_r, self.from_c = from_r, from_c
        self.to_r, self.to_c = to_r, to_c
        self.arrival_time = arrival_time
