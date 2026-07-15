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
        active_airborne = self._scheduler.get_active_airborne_positions(current_time)

        due_moves = self._scheduler.get_due_moves(current_time)
        due_moves.sort(key=lambda m: (m.arrival_time, 1 if m.is_jump() else 0))

        for m in due_moves:
            if self._game_over:
                break

            if m.is_jump():
                continue

            airborne_piece = active_airborne.get((m.to_r, m.to_c))
            if airborne_piece and airborne_piece.color != m.piece.color:
                self._board.remove_piece(m.from_r, m.from_c)
                continue

            captured_piece = self._board.execute_move(m.from_r, m.from_c, m.to_r, m.to_c)
            if captured_piece and captured_piece.type == 'K':
                self._game_over = True

    def request_move(self, piece, to_r, to_c, arrival_time, move_type=Move.MOVE_TYPE_NORMAL):
        if self._game_over or self._scheduler.is_piece_moving(piece):
            return False

        r, c = self._board.find_piece(piece)
        if r is None or c is None:
            return False

        if move_type == Move.MOVE_TYPE_JUMP:
            if r != to_r or c != to_c:
                return False

            move = Move(piece, r, c, to_r, to_c, arrival_time, move_type=Move.MOVE_TYPE_JUMP)
            self._scheduler.schedule(move)
            return True

        if not RuleEngine.is_legal(self._board, piece, to_r, to_c):
            return False

        if not PathValidator.is_path_clear(self._board, self._scheduler, r, c, to_r, to_c):
            return False

        if self._scheduler.is_route_blocked(piece, to_r, to_c):
            return False

        move = Move(piece, r, c, to_r, to_c, arrival_time)
        self._scheduler.schedule(move)
        return True
