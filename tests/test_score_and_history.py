import pytest
from model.board import Board
from model.piece import Piece
from game.controller import GameController


@pytest.fixture
def setup_controller():
    grid = [[None for _ in range(8)] for _ in range(8)]
    grid[7][4] = Piece('w', 'K')
    grid[0][4] = Piece('b', 'K')
    grid[3][3] = Piece('w', 'R')
    grid[3][4] = Piece('b', 'P')  # one square away, capturable
    board = Board(grid)
    controller = GameController(board)
    return controller, board


def click_cell(controller, row, col):
    controller.handle_click(col * 100 + 50, row * 100 + 50)


def test_capturing_a_pawn_awards_one_point(setup_controller):
    controller, board = setup_controller
    click_cell(controller, 3, 3)   # select white rook
    click_cell(controller, 3, 4)   # capture black pawn
    controller.handle_wait(1000)

    score = controller.engine.get_score()
    assert score['w'] == 1
    assert score['b'] == 0


def test_score_text_reflects_captures(setup_controller):
    controller, board = setup_controller
    click_cell(controller, 3, 3)
    click_cell(controller, 3, 4)
    controller.handle_wait(1000)

    assert controller.engine.get_score_text() == "White: 1  Black: 0"


def test_move_history_records_both_players(setup_controller):
    controller, board = setup_controller
    click_cell(controller, 3, 3)   # white rook selects
    click_cell(controller, 3, 4)   # white rook captures (also moves black king separately)
    controller.handle_wait(1)

    click_cell(controller, 0, 4)   # select black king
    click_cell(controller, 1, 4)   # move it
    controller.handle_wait(1)

    history = controller.engine.move_history.all()
    colors = [entry.color for entry in history]
    assert 'w' in colors
    assert 'b' in colors
    assert len(history) == 2


def test_move_history_entry_has_correct_fields(setup_controller):
    controller, board = setup_controller
    click_cell(controller, 3, 3)
    click_cell(controller, 3, 4)
    controller.handle_wait(1)

    entry = controller.engine.move_history.all()[0]
    assert entry.color == 'w'
    assert entry.piece_type == 'R'
    assert (entry.from_r, entry.from_c) == (3, 3)
    assert (entry.to_r, entry.to_c) == (3, 4)
    assert entry.received_at > 0


def test_jump_counter_capture_awards_score_to_defender():
    grid = [[None for _ in range(8)] for _ in range(8)]
    grid[7][4] = Piece('w', 'K')
    grid[0][4] = Piece('b', 'K')
    defender = Piece('w', 'N')
    attacker = Piece('b', 'R')
    grid[4][4] = defender
    grid[4][3] = attacker  # one square away -> 1000ms move, same arrival tick as the 1000ms jump
    board = Board(grid)
    controller = GameController(board)

    # Defender jumps in place.
    controller.handle_jump(4 * 100 + 50, 4 * 100 + 50)
    # Attacker tries to capture the same square while defender is airborne.
    click_cell(controller, 4, 3)
    click_cell(controller, 4, 4)
    controller.handle_wait(1000)  # both land at the same tick

    score = controller.engine.get_score()
    assert score['w'] == 5  # defender's side scored the attacking Rook's value
    assert board.get_piece(4, 4) is defender
