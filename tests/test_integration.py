from runner.game_logic import GameLogic
import io
import sys


def test_vpl_scenario_1(capsys):
    input_data = """Board:
wK . .
. . .
. . .
Commands:
click 50 50
click 150 150
print board"""

    logic = GameLogic()
    logic.process_input(input_data)

    captured = capsys.readouterr()
    # מצפה להזזה של wK ל-(1,1)
    assert ". . ." in captured.out
    assert ". wK ." in captured.out