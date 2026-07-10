import sys
from game_logic import GameLogic

URL = "https://github.com/123orchen/Kung-Fu-Chess-Orchen.git"

if __name__ == "__main__":
    input_text = sys.stdin.read()
    logic = GameLogic()
    logic.process_input(input_text)