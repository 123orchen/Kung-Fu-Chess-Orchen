from config import BLACK_TURN, PIECE_VALUES, WHITE_TURN
from .move import Move
from .move_history import MoveHistory
from rules.movement_rules import PathValidator
from rules.rule_engine import RuleEngine


class GameEngine:
    def __init__(self, board, scheduler):
        self._board = board
        self._scheduler = scheduler
        self._game_over = False
        self._move_history = MoveHistory()
        self._score = {WHITE_TURN: 0, BLACK_TURN: 0}

    def is_game_over(self):
        return self._game_over

    @property
    def move_history(self):
        return self._move_history

    def get_score(self):
        return dict(self._score)

    def get_score_text(self):
        return f"White: {self._score[WHITE_TURN]}  Black: {self._score[BLACK_TURN]}"

    def _award_capture(self, winner_color, captured_type):
        self._score[winner_color] += PIECE_VALUES.get(captured_type, 0)

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
                # Counter-capture: the defender was mid-jump, so the attacker
                # is destroyed instead - the defender's side scores the point.
                self._board.remove_piece(m.from_r, m.from_c)
                self._award_capture(airborne_piece.color, m.piece.type)
                continue

            captured_piece = self._board.execute_move(m.from_r, m.from_c, m.to_r, m.to_c)
            if captured_piece:
                self._award_capture(m.piece.color, captured_piece.type)
                if captured_piece.type == 'K':
                    self._game_over = True

    def request_move(self, piece, to_r, to_c, arrival_time, move_type=Move.MOVE_TYPE_NORMAL, current_time=None):
        if self._game_over or self._scheduler.is_piece_moving(piece):
            return False

        r, c = self._board.find_piece(piece)
        if r is None or c is None:
            return False

        # The elapsed-time shown in the move log is when the command was
        # received, not when the move lands - callers that track a real
        # clock (GameController) should pass it; direct/test callers fall
        # back to arrival_time (cosmetic only, doesn't affect gameplay).
        received_time = current_time if current_time is not None else arrival_time

        if move_type == Move.MOVE_TYPE_JUMP:
            if r != to_r or c != to_c:
                return False

            move = Move(piece, r, c, to_r, to_c, arrival_time, move_type=Move.MOVE_TYPE_JUMP)
            self._scheduler.schedule(move)
            self._move_history.record(piece.color, piece.type, r, c, to_r, to_c, move_type, received_time)
            return True

        if not RuleEngine.is_legal(self._board, piece, to_r, to_c):
            return False

        if not PathValidator.is_path_clear(self._board, self._scheduler, r, c, to_r, to_c):
            return False

        if self._scheduler.is_route_blocked(piece, to_r, to_c):
            return False

        move = Move(piece, r, c, to_r, to_c, arrival_time)
        self._scheduler.schedule(move)
        self._move_history.record(piece.color, piece.type, r, c, to_r, to_c, move_type, received_time)
        return True
