from board_mapper import BoardMapper


class GameController:
    def __init__(self, board, engine, scheduler):
        self._board = board
        self._engine = engine
        self._scheduler = scheduler
        self._current_time = 0
        self._selected_piece = None

    def handle_wait(self, ms):
        self._current_time += ms
        self._engine.process_time_step(self._current_time)

    def handle_click(self, x, y):
        col, row = BoardMapper.pixel_to_coords(x, y)
        target = self._board.get_piece(row, col)

        if self._selected_piece:
            if not self._scheduler.is_piece_moving(self._selected_piece):
                # בקשה מהמנוע לבצע את המהלך
                self._engine.request_move(self._selected_piece, row, col, self._current_time + 1000)
            self._selected_piece = None
        else:
            if target and not self._scheduler.is_piece_moving(target):
                self._selected_piece = target
