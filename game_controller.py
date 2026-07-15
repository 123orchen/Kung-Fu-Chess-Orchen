from board_mapper import BoardMapper
from config import JUMP_DURATION_MS, MOVE_DURATION_MS
from game_engine import GameEngine
from move import Move
from move_scheduler import MoveScheduler


class GameController:
    def __init__(self, board, engine=None, scheduler=None):
        self._board = board
        self._scheduler = scheduler if scheduler is not None else MoveScheduler()
        self._engine = engine if engine is not None else GameEngine(self._board, self._scheduler)

        self._current_time = 0
        self._time_ms = 0
        self._selected_piece = None
        self._pending_visual_move = None

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

        if self._selected_piece is not None:
            if target and target.color == self._selected_piece.color:
                if not self._scheduler.is_piece_moving(target):
                    self._selected_piece = target
                return

            self._attempt_move(row, col)
            self._selected_piece = None
            return

        if target and not self._scheduler.is_piece_moving(target):
            self._selected_piece = target

    def handle_jump(self, x, y):
        if self._engine.is_game_over():
            return

        col, row = BoardMapper.pixel_to_coords(x, y)
        target = self._board.get_piece(row, col)
        if not target:
            return

        self._engine.request_move(target, row, col, self._current_time + JUMP_DURATION_MS, move_type=Move.MOVE_TYPE_JUMP)

    def _attempt_move(self, row, col):
        if self._selected_piece is None:
            return
        if self._scheduler.is_piece_moving(self._selected_piece):
            return

        from_r, from_c = self._board.find_piece(self._selected_piece)
        if from_r is None or from_c is None:
            return

        arrival_time = self._current_time + self._get_move_duration(from_r, from_c, row, col)

        if self._engine.request_move(self._selected_piece, row, col, arrival_time):
            snapshot = self._board.snapshot_state()
            self._board.execute_move(from_r, from_c, row, col)
            self._pending_visual_move = {
                'snapshot': snapshot,
                'arrival_time': arrival_time,
            }

    def _get_move_duration(self, from_r, from_c, to_r, to_c):
        dr = abs(to_r - from_r)
        dc = abs(to_c - from_c)
        distance = max(dr, dc)
        return distance * MOVE_DURATION_MS