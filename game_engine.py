from config import BLACK_TURN, WHITE_TURN
from move import Move
from pathValidator import PathValidator
from rule_engine import RuleEngine


class GameEngine:
    def __init__(self, board, scheduler):
        self._board = board
        self._scheduler = scheduler
        self._game_over = False

    def is_game_over(self):
        return self._game_over

    def process_time_step(self, current_time):
        due_moves = self._scheduler.get_due_moves(current_time)
        due_moves.sort(key=lambda m: m.arrival_time)

        for m in due_moves:
            if self._game_over:
                break

            self._board.execute_move(m.from_r, m.from_c, m.to_r, m.to_c)
            opponent_color = BLACK_TURN if m.piece.color == WHITE_TURN else WHITE_TURN
            if not self._board.is_king_on_board(opponent_color):
                self._game_over = True

    def request_move(self, piece, to_r, to_c, arrival_time):
        if self._game_over or self._scheduler.is_piece_moving(piece):
            return False

        if not RuleEngine.is_legal(self._board, piece, to_r, to_c):
            return False

        r, c = self._board.find_piece(piece)
        if r is None or c is None:
            return False

        if not PathValidator.is_path_clear(self._board, self._scheduler, r, c, to_r, to_c):
            return False

        if self._scheduler.is_route_blocked(piece, to_r, to_c):
            return False

        move = Move(piece, r, c, to_r, to_c, arrival_time)
        self._scheduler.schedule(move)
        return True
