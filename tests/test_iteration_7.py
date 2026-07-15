import pytest
from model.board import Board
from game.game_engine import GameEngine
from game.real_time_arbiter import MoveScheduler
from model.piece import Piece
from config import PAWN, ROOK, WHITE_TURN, BLACK_TURN


def create_board_two_rooks():
    # שני צריחים על הלוח: לבן ב-(0,0), שחור ב-(2,0)
    grid = [[Piece(WHITE_TURN, ROOK), None, None],
            [None, None, None],
            [Piece(BLACK_TURN, ROOK), None, None]]
    return Board(grid)


def test_no_cooldown_and_can_move_again():
    board = create_board_two_rooks()
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    rook = board.get_piece(0, 0)

    # מהלך ראשון - חוקי
    assert engine.request_move(rook, 0, 1, 1000) == True

    # עדכון זמן והשלמת מהלך
    engine.process_time_step(1001)

    # וודא שהכלי פנוי למהלך שני מיד (No Cooldown)
    assert scheduler.is_piece_moving(rook) == False
    assert engine.request_move(rook, 0, 2, 2000) == True


def test_no_redirect_while_moving():
    board = create_board_two_rooks()
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    rook = board.get_piece(0, 0)

    # תזמון מהלך ראשון
    engine.request_move(rook, 0, 1, 1000)

    # ניסיון "להסיט" (Redirect) בזמן שהוא בתנועה - חייב להיכשל
    assert engine.request_move(rook, 0, 2, 1000) == False


def test_opposite_colors_do_not_move_concurrently():
    # בלוח: לבן ב-(0,0), שחור ב-(2,0)
    board = create_board_two_rooks()
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    white_rook = board.get_piece(0, 0)
    black_rook = board.get_piece(2, 0)

    # הלבן זז ל-(0, 2) - הוא "תופס" את השורה 0
    engine.request_move(white_rook, 0, 2, 1000)

    # השחור מנסה לזוז ל-(0, 2) או לכל משבצת בשורה 0 - זה חייב להיכשל!
    # כי הלבן כבר "חוסם" את השורה הזו (או הטור, תלוי במימוש שלך)
    assert engine.request_move(black_rook, 0, 1, 1000) == False


def test_premove_prevention():
    board = create_board_two_rooks()
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    rook = board.get_piece(0, 0)

    # מהלך ראשון
    engine.request_move(rook, 0, 1, 1000)

    # ניסיון לתזמן מהלך שני לפני שהראשון הסתיים (Premove)
    assert engine.request_move(rook, 0, 2, 2000) == False
