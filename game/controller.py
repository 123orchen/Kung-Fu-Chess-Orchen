from .pixel_mapper import BoardMapper
from config import JUMP_DURATION_MS, MOVE_DURATION_MS
from .game_engine import GameEngine
from .move import Move
from .real_time_arbiter import MoveScheduler


class GameController:
    def __init__(self, board, engine=None, scheduler=None, on_local_move=None):
        self._board = board
        self._scheduler = scheduler if scheduler is not None else MoveScheduler()
        self._engine = engine if engine is not None else GameEngine(self._board, self._scheduler)

        self._current_time = 0
        self._time_ms = 0
        self._selected_piece = None
        self._pending_visual_move = None
        # Online play: called as on_local_move(piece, from_rc, to_rc, move_type)
        # right after a move made *by this client* is accepted, so it can be
        # sent to the server. Not called for moves applied via apply_remote_move.
        self._on_local_move = on_local_move
        # Online play: when set, handle_click/handle_jump ignore any piece
        # whose color isn't this one - a player can only move their own side.
        self.local_color = None

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def engine(self):
        return self._engine

    def _is_available(self, piece):
        """A piece can be selected/moved/jumped only if it isn't mid-move and isn't resting."""
        return not self._scheduler.is_piece_moving(piece) and \
            not self._scheduler.is_piece_on_cooldown(piece, self._current_time)

    def handle_wait(self, ms):
        self._current_time += ms
        self._time_ms = self._current_time

        if self._pending_visual_move:
            self._board.restore_state(self._pending_visual_move['snapshot'])
            self._pending_visual_move = None

        self._engine.process_time_step(self._current_time)

    def handle_click(self, x, y):
        if self._engine.is_game_over():
            return

        col, row = BoardMapper.pixel_to_coords(x, y)
        target = self._board.get_piece(row, col)
        if target and self.local_color is not None and target.color != self.local_color \
                and self._selected_piece is None:
            return  # online play: can't pick up the opponent's piece

        if self._selected_piece is not None:
            if target and target.color == self._selected_piece.color:
                if self._is_available(target):
                    self._selected_piece = target
                return

            self._attempt_move(row, col)
            self._selected_piece = None
            return

        if target and self._is_available(target):
            self._selected_piece = target

    def handle_jump(self, x, y):
        if self._engine.is_game_over():
            return

        col, row = BoardMapper.pixel_to_coords(x, y)
        target = self._board.get_piece(row, col)
        if not target or not self._is_available(target):
            return
        if self.local_color is not None and target.color != self.local_color:
            return  # online play: can't jump the opponent's piece

        self._do_jump(target, row, col)
        if self._on_local_move:
            from_r, from_c = self._board.find_piece(target)
            self._on_local_move(target, (from_r, from_c), (row, col), Move.MOVE_TYPE_JUMP)

    def apply_remote_move(self, from_rc, to_rc, move_type=Move.MOVE_TYPE_NORMAL):
        """Apply a move received from the network (the opponent's move)."""
        from_r, from_c = from_rc
        row, col = to_rc
        piece = self._board.get_piece(from_r, from_c)
        if piece is None or not self._is_available(piece):
            return False

        if move_type == Move.MOVE_TYPE_JUMP:
            self._do_jump(piece, row, col)
        else:
            self._do_move(piece, from_r, from_c, row, col)
        return True

    def _do_jump(self, piece, row, col):
        self._engine.request_move(piece, row, col, self._current_time + JUMP_DURATION_MS, move_type=Move.MOVE_TYPE_JUMP, current_time=self._current_time)

    def _do_move(self, piece, from_r, from_c, row, col):
        arrival_time = self._current_time + self._get_move_duration(from_r, from_c, row, col)

        if self._engine.request_move(piece, row, col, arrival_time, current_time=self._current_time):
            snapshot = self._board.snapshot_state()
            self._board.execute_move(from_r, from_c, row, col)
            self._pending_visual_move = {
                'snapshot': snapshot,
                'arrival_time': arrival_time,
            }
            return True
        return False

    def _attempt_move(self, row, col):
        if self._selected_piece is None:
            return
        if not self._is_available(self._selected_piece):
            return

        from_r, from_c = self._board.find_piece(self._selected_piece)
        if from_r is None or from_c is None:
            return

        piece = self._selected_piece
        if self._do_move(piece, from_r, from_c, row, col) and self._on_local_move:
            self._on_local_move(piece, (from_r, from_c), (row, col), Move.MOVE_TYPE_NORMAL)

    def _get_move_duration(self, from_r, from_c, to_r, to_c):
        dr = abs(to_r - from_r)
        dc = abs(to_c - from_c)
        distance = max(dr, dc)
        return distance * MOVE_DURATION_MS