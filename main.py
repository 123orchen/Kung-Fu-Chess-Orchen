import sys
from game_logic import GameLogic

if __name__ == "__main__":
    input_text = sys.stdin.read()
    logic = GameLogic()
    logic.process_input(input_text)