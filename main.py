import sys
from runner.game_logic import GameLogic

try:
    from graphics.app import run as run_graphics
except ImportError:
    run_graphics = None

URL = "https://github.com/123orchen/Kung-Fu-Chess-Orchen.git"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        if run_graphics is None:
            raise RuntimeError("Graphics app cannot be imported. Check that the graphics package exists.")
        run_graphics()
    else:
        input_text = sys.stdin.read()
        logic = GameLogic()
        logic.process_input(input_text)
