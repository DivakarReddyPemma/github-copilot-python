import copy

import sudoku_logic


SOLVED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def assert_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(set(row) == expected for row in board)
    assert all(
        {board[row][col] for row in range(sudoku_logic.SIZE)} == expected
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            board[row + row_offset][col + col_offset]
            for row_offset in range(3)
            for col_offset in range(3)
        }
        == expected
        for row in range(0, sudoku_logic.SIZE, 3)
        for col in range(0, sudoku_logic.SIZE, 3)
    )


def test_create_empty_board_has_expected_dimensions_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(value == sudoku_logic.EMPTY for row in board for value in row)


def test_deep_copy_is_independent_of_original_board():
    board = sudoku_logic.create_empty_board()

    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 5

    assert board[0][0] == sudoku_logic.EMPTY


def test_is_safe_accepts_a_value_not_present_in_row_column_or_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert sudoku_logic.is_safe(board, 1, 1, 5)


def test_is_safe_rejects_values_present_in_row_column_or_box():
    row_conflict = sudoku_logic.create_empty_board()
    row_conflict[0][1] = 5
    column_conflict = sudoku_logic.create_empty_board()
    column_conflict[1][0] = 5
    box_conflict = sudoku_logic.create_empty_board()
    box_conflict[1][1] = 5

    assert not sudoku_logic.is_safe(row_conflict, 0, 0, 5)
    assert not sudoku_logic.is_safe(column_conflict, 0, 0, 5)
    assert not sudoku_logic.is_safe(box_conflict, 0, 0, 5)


def test_fill_board_completes_puzzle_without_changing_given_values():
    puzzle = copy.deepcopy(SOLVED_BOARD)
    puzzle[0][0] = sudoku_logic.EMPTY
    puzzle[4][4] = sudoku_logic.EMPTY
    puzzle[8][8] = sudoku_logic.EMPTY
    given_values = {
        (row, col): value
        for row, values in enumerate(puzzle)
        for col, value in enumerate(values)
        if value != sudoku_logic.EMPTY
    }

    assert sudoku_logic.fill_board(puzzle)

    assert_valid_solution(puzzle)
    assert all(puzzle[row][col] == value for (row, col), value in given_values.items())


def test_remove_cells_leaves_the_requested_number_of_clues():
    board = copy.deepcopy(SOLVED_BOARD)

    sudoku_logic.remove_cells(board, clues=30)

    assert sum(value != sudoku_logic.EMPTY for row in board for value in row) == 30


def test_generate_puzzle_returns_consistent_puzzle_and_valid_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=30)

    assert_valid_solution(solution)
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(value != sudoku_logic.EMPTY for row in puzzle for value in row) == 30
    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )
