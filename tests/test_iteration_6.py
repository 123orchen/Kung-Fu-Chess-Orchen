import pytest
from board import Board
from game_controller import GameController
from piece import Piece
from config import PAWN, WHITE_TURN, BLACK_TURN


# עזר: יצירת לוח פשוט
def create_board():
    # נשים את החייל בשורה 1 (הוא יוכל לעלות ל-0)
    grid = [[None, None],
            [Piece(WHITE_TURN, PAWN), None]]
    return Board(grid)


def test_move_pending_before_arrival():
    board = create_board()
    controller = GameController(board)

    # חייל ב-(1,0), row=1, col=0
    # נלחץ על הקואורדינטות בפיקסלים (x=50, y=150) שזה עמודה 0, שורה 1
    controller.handle_click(50, 150)

    # ננסה להזיז ל-(0,0), row=0, col=0
    # נלחץ על (x=50, y=50) שזה עמודה 0, שורה 0
    controller.handle_click(50, 50)

    controller.handle_wait(500)

    # בבדיקה: ב-row=1, col=0 עדיין צריך להיות החייל!
    assert board.get_piece(1, 0) is not None
    assert board.get_piece(0, 0) is None

def test_move_executes_after_arrival():
    board = create_board()
    controller = GameController(board)

    controller.handle_click(0, 0)
    controller.handle_click(1, 0)

    # מחכים 1000ms - המהלך חייב לקרות
    controller.handle_wait(1000)
    assert board.get_piece(0, 0) is None
    assert board.get_piece(1, 0) is not None


def test_moving_piece_ignores_redirect():
    board = create_board()
    controller = GameController(board)

    # מהלך ראשון
    controller.handle_click(0, 0)
    controller.handle_click(1, 0)  # יעד 1

    # ניסיון "להסיט" (Redirect) - אסור שזה יעבוד
    controller.handle_click(0, 0)  # הכלי כבר בתנועה
    controller.handle_click(1, 1)  # יעד חדש 2

    controller.handle_wait(1000)
    # הכלי צריך להיות ביעד המקורי (1,0) ולא ביעד החדש (1,1)
    assert board.get_piece(1, 0) is not None
    assert board.get_piece(1, 1) is None