import pytest
from config import LONG_REST_MS, SHORT_REST_MS
from model.board import Board
from model.piece import Piece
from game.controller import GameController


@pytest.fixture
def setup_controller():
    grid = [[None for _ in range(8)] for _ in range(8)]
    grid[7][4] = Piece('w', 'K')
    grid[0][4] = Piece('b', 'K')
    grid[7][0] = Piece('w', 'R')
    board = Board(grid)
    controller = GameController(board)
    return controller, board


def click_cell(controller, row, col):
    controller.handle_click(col * 100 + 50, row * 100 + 50)


def test_jump_rest_is_shorter_than_move_rest():
    assert SHORT_REST_MS < LONG_REST_MS


def test_cannot_select_resting_piece(setup_controller):
    controller, board = setup_controller
    rook = board.get_piece(7, 0)

    click_cell(controller, 7, 0)
    click_cell(controller, 7, 1)
    controller.handle_wait(1000)  # move lands, long_rest starts

    # Selecting the resting rook should silently fail (no crash, no selection).
    click_cell(controller, 7, 1)
    click_cell(controller, 7, 2)
    controller.handle_wait(1)
    assert board.get_piece(7, 2) is None
    assert board.get_piece(7, 1) is rook


def test_cannot_jump_resting_piece(setup_controller):
    controller, board = setup_controller
    rook = board.get_piece(7, 0)

    controller.handle_jump(0 * 100 + 50, 7 * 100 + 50)   # jump in place
    controller.handle_wait(1000)                          # jump lands, short_rest starts

    assert controller.scheduler.is_piece_on_cooldown(rook, controller._current_time)

    # A second jump attempt during short_rest must be ignored.
    before = controller.scheduler.is_piece_moving(rook)
    controller.handle_jump(0 * 100 + 50, 7 * 100 + 50)
    assert controller.scheduler.is_piece_moving(rook) == before


def test_piece_available_again_after_short_rest(setup_controller):
    controller, board = setup_controller
    rook = board.get_piece(7, 0)

    controller.handle_jump(0 * 100 + 50, 7 * 100 + 50)
    controller.handle_wait(1000)                # jump lands
    controller.handle_wait(SHORT_REST_MS)       # short_rest fully elapses

    click_cell(controller, 7, 0)
    click_cell(controller, 7, 1)
    controller.handle_wait(1000)
    assert board.get_piece(7, 1) is rook


def test_rest_animation_state_matches_move_type(setup_controller):
    controller, board = setup_controller
    rook = board.get_piece(7, 0)

    click_cell(controller, 7, 0)
    click_cell(controller, 7, 1)
    controller.handle_wait(1000)
    assert controller.scheduler.get_rest_kind(rook, controller._current_time) == 'long_rest'
