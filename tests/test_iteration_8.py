import pytest
from model.board import Board
from model.piece import Piece
from game.game_engine import GameEngine
from game.real_time_arbiter import MoveScheduler
from rules.movement_rules import PathValidator


def test_no_premove():
    # בדיקת חובה: אי אפשר להזיז כלי שכבר זז
    grid = [[Piece('w', 'R'), None, None]]
    board = Board(grid)
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    wR = board.get_piece(0, 0)
    # מהלך ראשון - חוקי
    engine.request_move(wR, 0, 1, 1000)
    # מהלך שני על אותו כלי - חייב להיכשל (Premove)
    assert engine.request_move(wR, 0, 2, 2000) == False


def test_destination_collision():
    # בדיקה: אי אפשר ללכת למשבצת שמישהו אחר בדרך אליה
    grid = [[Piece('w', 'R'), None, None, Piece('b', 'R')]]
    board = Board(grid)
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    wR = board.get_piece(0, 0)
    bR = board.get_piece(0, 3)

    # wR זז ל-(0,2)
    engine.request_move(wR, 0, 2, 1000)
    # bR מנסה לזוז ל-(0,2) - חייב להיכשל (התנגשות ביעד)
    assert engine.request_move(bR, 0, 2, 1000) == False


def test_legal_move():
    # בדיקת מהלך חוקי פשוט
    grid = [[Piece('w', 'R'), None]]
    board = Board(grid)
    scheduler = MoveScheduler()
    engine = GameEngine(board, scheduler)

    wR = board.get_piece(0, 0)
    assert engine.request_move(wR, 0, 1, 1000) == True