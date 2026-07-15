from model.board import Board
from model.piece import Piece


def test_board_display(capsys):
    # יצירת לוח פשוט עם כלי אחד ומשבצת ריקה
    grid = [[Piece('w', 'K'), None], [None, Piece('b', 'R')]]
    board = Board(grid)
    board.display()

    captured = capsys.readouterr()
    assert captured.out.strip() == "wK .\n. bR"