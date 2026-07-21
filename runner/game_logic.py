from config import COMMAND_CLICK, COMMAND_JUMP, COMMAND_PRINT, COMMAND_PRINT_BOARD, COMMAND_PRINT_HISTORY, COMMAND_PRINT_SCORE, COMMAND_WAIT
from .command_parser import InputParser
from model.board import Board
from game.controller import GameController
from model.piece import Piece


class GameLogic:
    def process_input(self, input_text):
        lines = [line.strip() for line in input_text.split('\n') if line.strip()]

        # 1. מציאת גבול הלוח
        board_lines = []
        commands = []
        is_commands = False
        for line in lines:
            if line == "Commands:":
                is_commands = True
                continue
            if not is_commands and line != "Board:":
                board_lines.append(line.split())
            elif is_commands:
                commands.append(line)

        # 2. בדיקות תקינות (הכי חשוב!)
        width = len(board_lines[0])
        for row in board_lines:
            if len(row) != width:
                print("ERROR ROW_WIDTH_MISMATCH")
                return  # עוצרים!
            for token in row:
                if token != '.' and not InputParser.is_valid_token(token):
                    print("ERROR UNKNOWN_TOKEN")
                    return  # עוצרים!

        # 3. אתחול
        # במקום לשלוח board_lines, נשלח אותו כפי שהוא למתודה שתומכת ברשימות
        board = Board(InputParser.parse_board_from_list(board_lines))
        controller = GameController(board)

        # 4. ביצוע פקודות
        for cmd in commands:
            p = cmd.split()
            if not p:
                continue
            if p[0] == COMMAND_CLICK:
                controller.handle_click(int(p[1]), int(p[2]))
            elif p[0] == COMMAND_JUMP:
                controller.handle_jump(int(p[1]), int(p[2]))
            elif p[0] == COMMAND_WAIT:
                controller.handle_wait(int(p[1]))
            elif p[0] == COMMAND_PRINT and p[1] == COMMAND_PRINT_BOARD:
                board.display()
            elif p[0] == COMMAND_PRINT and p[1] == COMMAND_PRINT_SCORE:
                print(controller.engine.get_score_text())
            elif p[0] == COMMAND_PRINT and p[1] == COMMAND_PRINT_HISTORY:
                for entry in controller.engine.move_history.all():
                    print(entry)
