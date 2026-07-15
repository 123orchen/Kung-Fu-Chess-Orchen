from runner.game_logic import GameLogic


def _run_vpl_input(input_data):
    logic = GameLogic()
    logic.process_input(input_data)


def test_jump_lands_same_square(capsys):
    input_data = """Board:
. . .
wK . .
. . .
Commands:
jump 150 150
wait 1000
print board"""

    _run_vpl_input(input_data)
    captured = capsys.readouterr()
    assert captured.out == ". . .\nwK . .\n. . .\n"


def test_airborne_piece_captures_arriving_enemy(capsys):
    input_data = """Board:
. . .
wK bR .
. . .
Commands:
jump 50 150
click 150 150
click 50 150
wait 1000
print board"""

    _run_vpl_input(input_data)
    captured = capsys.readouterr()
    assert captured.out == ". . .\nwK . .\n. . .\n"


def test_jump_too_late_does_not_save_piece(capsys):
    input_data = """Board:
. . .
wK bR .
. . .
Commands:
click 150 150
click 50 150
wait 1000
jump 50 150
print board"""

    _run_vpl_input(input_data)
    captured = capsys.readouterr()
    assert captured.out == ". . .\nbR . .\n. . .\n"


def test_enemy_arrives_after_landing_captures_normally(capsys):
    input_data = """Board:
. . . .
wK . . bR
. . . .
Commands:
jump 50 150
wait 1000
click 350 150
click 50 150
wait 3000
print board"""

    _run_vpl_input(input_data)
    captured = capsys.readouterr()
    assert captured.out == ". . . .\nbR . . .\n. . . .\n"


def test_cannot_jump_while_moving(capsys):
    input_data = """Board:
wR . .
. . .
Commands:
click 50 50
click 250 50
wait 500
jump 50 50
wait 1500
print board"""

    _run_vpl_input(input_data)
    captured = capsys.readouterr()
    assert captured.out == ". . wR\n. . .\n"


def test_airborne_capture_only_enemy(capsys):
    input_data = """Board:
. . .
wK wR .
. . .
Commands:
jump 50 150
click 150 150
click 50 150
wait 1000
print board"""

    _run_vpl_input(input_data)
    captured = capsys.readouterr()
    assert captured.out == ". . .\nwK wR .\n. . .\n"
