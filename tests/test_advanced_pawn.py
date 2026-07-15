import pytest
from board import Board
from game_engine import GameEngine
from move_scheduler import MoveScheduler
from piece import Piece


@pytest.fixture
def setup_full_game():
    grid = [[None for _ in range(8)] for _ in range(8)]
    # מלכים בשביל שלא יסתיים המשחק בטעות
    grid[7][4] = Piece('w', 'K')
    grid[0][4] = Piece('b', 'K')
    # חייל שלנו
    grid[6][0] = Piece('w', 'P')
    board = Board(grid)
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)
    return engine, board


# 1. בדיקה שחייל עושה צעד כפול מההתחלה
def test_pawn_double_move(setup_full_game):
    engine, board = setup_full_game
    pawn = board.get_piece(6, 0)
    assert engine.request_move(pawn, 4, 0, 1000) is True


# 2. בדיקה שחייל לא יכול לעשות צעד כפול אם הוא לא בשורה 6
def test_pawn_no_double_move_after_start(setup_full_game):
    engine, board = setup_full_game
    pawn = board.get_piece(6, 0)
    # מהלך ראשון ל-5,0
    engine.request_move(pawn, 5, 0, 1000)
    engine.process_time_step(1000)
    # עכשיו מנסה שוב צעד כפול - אמור להיכשל
    assert engine.request_move(pawn, 3, 0, 2000) is False


# 3. בדיקת קידום מלא (הטסט הקודם שעבד לנו)
def test_pawn_promotion_success(setup_full_game):
    engine, board = setup_full_game
    pawn = board.get_piece(6, 0)
    moves = [(4, 0), (3, 0), (2, 0), (1, 0), (0, 0)]
    time = 1000
    for r, c in moves:
        assert engine.request_move(pawn, r, c, time) is True
        engine.process_time_step(time)
        time += 1000
    assert board.get_piece(0, 0).type == 'Q'


# 4. בדיקה שחייל לא יכול לזוז אחורה
def test_pawn_cannot_move_backwards(setup_full_game):
    engine, board = setup_full_game
    pawn = board.get_piece(6, 0)
    # מנסה לזוז אחורה ל-7,0
    assert engine.request_move(pawn, 7, 0, 1000) is False


def test_pawn_capture_diagonal(setup_full_game):
    engine, board = setup_full_game
    # החייל שלנו ב-6,0
    pawn = board.get_piece(6, 0)

    # 1. נוסיף חייל שחור באלכסון (5,1)
    board._grid[5][1] = Piece('b', 'P')

    # 2. ננסה לאכול אותו (לזוז ל-5,1)
    # זה אמור להצליח כי זו אכילה חוקית
    assert engine.request_move(pawn, 5, 1, 1000) is True

    # 3. נבדוק מקרה הפוך: משבצת ריקה באלכסון (5,1)
    # נחזיר את החייל להתחלה או ניצור חייל חדש ב-4,0 ללא שום דבר באלכסון
    # ניסיון לזוז ל-3,1 כשהמשבצת ריקה - אמור להיכשל!
    assert engine.request_move(pawn, 3, 1, 2000) is False