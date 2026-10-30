import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    "easy": 40,
    "medium": 32,
    "hard": 26,
}


def deep_copy(board):
    """Return an independent copy of a Sudoku board."""
    return copy.deepcopy(board)


def create_empty_board():
    """Create a blank 9x9 board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return whether ``num`` can be placed at the given board position."""
    # Check the row and column before scanning the containing box.
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    """Fill an incomplete board with a valid randomized Sudoku solution."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Count solutions up to ``limit`` without modifying the supplied board."""
    if (
        not isinstance(board, list)
        or len(board) != SIZE
        or any(
            not isinstance(row, list)
            or len(row) != SIZE
            or any(
                not isinstance(value, int)
                or isinstance(value, bool)
                or not EMPTY <= value <= SIZE
                for value in row
            )
            for row in board
        )
    ):
        return 0
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("Solution count limit must be a positive integer")

    working_board = deep_copy(board)

    # Reject duplicate givens before searching; the backtracker only fills blanks.
    for row in range(SIZE):
        for col in range(SIZE):
            value = working_board[row][col]
            if value != EMPTY:
                working_board[row][col] = EMPTY
                valid = is_safe(working_board, row, col, value)
                working_board[row][col] = value
                if not valid:
                    return 0

    def search():
        """Backtrack from the blank with the fewest legal values."""
        best_position = None
        best_candidates = None
        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] != EMPTY:
                    continue
                candidates = [
                    value
                    for value in range(1, SIZE + 1)
                    if is_safe(working_board, row, col, value)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_position = (row, col)
                    best_candidates = candidates
                    if len(candidates) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_position is None:
            return 1

        row, col = best_position
        solutions = 0
        for value in best_candidates:
            working_board[row][col] = value
            solutions += search()
            working_board[row][col] = EMPTY
            if solutions >= limit:
                return limit
        return solutions

    return search()


def remove_cells(board, clues):
    """Remove clues in place while preserving a unique solution.

    The requested clue count is a target; it may not be reachable for every
    solved board while retaining uniqueness.
    """
    if (
        not isinstance(clues, int)
        or isinstance(clues, bool)
        or not 0 <= clues <= SIZE * SIZE
    ):
        raise ValueError("Clues must be an integer between 0 and 81")

    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)
    remaining = SIZE * SIZE
    for row, col in positions:
        if remaining <= clues:
            break
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) == 1:
            remaining -= 1
        else:
            board[row][col] = value


def generate_puzzle(clues=DIFFICULTY_CLUES["medium"]):
    """Return a unique-solution puzzle and its complete solution."""
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
