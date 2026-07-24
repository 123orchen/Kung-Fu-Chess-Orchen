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
        online = "--online" in sys.argv
        server_uri = "ws://localhost:8000/ws"
        for arg in sys.argv:
            if arg.startswith("--server="):
                server_uri = arg.split("=", 1)[1]

        username = None
        password = None
        for arg in sys.argv:
            if arg.startswith("--user="):
                username = arg.split("=", 1)[1]
            elif arg.startswith("--pass="):
                password = arg.split("=", 1)[1]

        if online:
            # Stage B/C: login with username + password, done in the shell
            # (not the GUI). First login for a username registers it.
            # Can be passed as --user=NAME --pass=SECRET to skip the prompts.
            if username is None:
                username = input("Enter username: ").strip() or "Player"
            if password is None:
                try:
                    import getpass
                    password = getpass.getpass("Enter password: ")
                except Exception:
                    password = input("Enter password: ")

        run_graphics(online=online, server_uri=server_uri, username=username, password=password)
    else:
        input_text = sys.stdin.read()
        logic = GameLogic()
        logic.process_input(input_text)
