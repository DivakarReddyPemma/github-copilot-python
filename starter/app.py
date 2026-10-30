"""Flask routes for the Sudoku game."""

from flask import Flask, jsonify, render_template, request

import sudoku_logic

app = Flask(__name__)

# Keep the active puzzle and solution in memory, as in the original app.
CURRENT = {
    "puzzle": None,
    "solution": None,
}


def _error_response(message):
    """Return a consistently shaped client-error response."""
    return jsonify({"error": message}), 400


def _is_valid_board(board):
    """Check that a submitted board is a 9x9 grid of Sudoku values."""
    return (
        isinstance(board, list)
        and len(board) == sudoku_logic.SIZE
        and all(
            isinstance(row, list)
            and len(row) == sudoku_logic.SIZE
            and all(
                isinstance(value, int)
                and not isinstance(value, bool)
                and sudoku_logic.EMPTY <= value <= sudoku_logic.SIZE
                for value in row
            )
            for row in board
        )
    )


@app.route("/")
def index():
    """Render the game page."""
    return render_template("index.html")


@app.route("/new")
def new_game():
    """Create and store a puzzle for the selected difficulty."""
    difficulty = request.args.get("difficulty")
    if difficulty is not None:
        difficulty = difficulty.lower()
        if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
            return _error_response("Difficulty must be easy, medium, or hard")
        clues = sudoku_logic.DIFFICULTY_CLUES[difficulty]
    else:
        raw_clues = request.args.get("clues")
        if raw_clues is None:
            clues = 35
        else:
            try:
                clues = int(raw_clues)
            except (TypeError, ValueError):
                return _error_response("Clues must be an integer between 0 and 81")

    if not 0 <= clues <= sudoku_logic.SIZE * sudoku_logic.SIZE:
        return _error_response("Clues must be an integer between 0 and 81")

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT["puzzle"] = puzzle
    CURRENT["solution"] = solution
    return jsonify({"puzzle": puzzle})


@app.route("/check", methods=["POST"])
def check_solution():
    """Return the coordinates whose submitted values do not match the solution."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Request body must be a JSON object")

    board = data.get("board")
    solution = CURRENT.get("solution")
    if solution is None:
        return _error_response("No game in progress")
    if not _is_valid_board(board):
        return _error_response(
            "Board must be a 9x9 grid containing integers from 0 to 9"
        )

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({"incorrect": incorrect})


if __name__ == "__main__":
    app.run(debug=True)
