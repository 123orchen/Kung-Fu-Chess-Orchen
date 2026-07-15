from board_mapper import BoardMapper
from game_engine import GameEngine
from move_scheduler import MoveScheduler


class GameController:
    def __init__(self, board, engine=None, scheduler=None):
        self._board = board
        self._scheduler = scheduler if scheduler is not None else MoveScheduler()
        self._engine = engine if engine is not None else GameEngine(self._board, self._scheduler)

        self._current_time = 0
        self._time_ms = 0
        self._selected_piece = None

    def handle_wait(self, ms):
        self._current_time += ms
        self._time_ms = self._current_time
        self._engine.process_time_step(self._current_time)

    def handle_click(self, x, y):
        if self._engine.is_game_over():
            return

        col, row = BoardMapper.pixel_to_coords(x, y)
        target = self._board.get_piece(row, col)

        if self._selected_piece:
            if not self._scheduler.is_piece_moving(self._selected_piece):
                if self._engine.request_move(self._selected_piece, row, col, self._current_time + 1000):
                    self._engine.process_time_step(self._current_time)

            self._selected_piece = None
        else:
            if target and not self._scheduler.is_piece_moving(target):
                self._selected_piece = target