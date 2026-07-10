from input_parser import InputParser


def test_parser_valid_input():
    data = "Board:\nwK . \n. bR\nCommands:"
    grid = InputParser.parse_board(data)

    assert grid[0][0]._type == 'K'
    assert grid[1][1]._type == 'R'
    assert grid[0][1] is None