import copy

import pytest

import app
import sudoku_logic


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    app.CURRENT["puzzle"] = None
    app.CURRENT["solution"] = None

    with app.app.test_client() as test_client:
        yield test_client

    app.CURRENT["puzzle"] = None
    app.CURRENT["solution"] = None


def test_index_route_renders_game_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b'<form id="score-form"' in response.data
    assert b'aria-labelledby="score-entry-title" hidden' in response.data
    assert b'id="player-name"' in response.data
    assert b'<button type="submit">Save</button>' in response.data


@pytest.mark.parametrize(
    ("query", "expected_clues"),
    [
        ("", 35),
        ("?clues=40", 40),
        ("?difficulty=easy", 40),
        ("?difficulty=medium", 32),
        ("?difficulty=hard", 26),
    ],
)
def test_new_game_route_generates_and_stores_puzzle(
    client, monkeypatch, query, expected_clues
):
    puzzle = sudoku_logic.create_empty_board()
    solution = copy.deepcopy(puzzle)
    generated_arguments = []

    def fake_generate_puzzle(clues):
        generated_arguments.append(clues)
        return puzzle, solution

    monkeypatch.setattr(sudoku_logic, "generate_puzzle", fake_generate_puzzle)

    response = client.get(f"/new{query}")

    assert response.status_code == 200
    assert response.get_json() == {"puzzle": puzzle}
    assert generated_arguments == [expected_clues]
    assert app.CURRENT == {"puzzle": puzzle, "solution": solution}


def test_new_game_route_rejects_unknown_difficulty(client):
    response = client.get("/new?difficulty=expert")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Difficulty must be easy, medium, or hard"}


@pytest.mark.parametrize("query", ["?clues=invalid", "?clues=-1", "?clues=82"])
def test_new_game_route_returns_a_json_error_for_invalid_clue_count(client, query):
    response = client.get(f"/new{query}")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Clues must be an integer between 0 and 81"
    }


def test_check_route_returns_bad_request_when_no_game_is_in_progress(client):
    response = client.post("/check", json={"board": sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_check_route_returns_coordinates_of_incorrect_cells(client):
    solution = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]
    board = copy.deepcopy(solution)
    board[0][2] = 2
    board[8][7] = 3
    app.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": [[0, 2], [8, 7]]}


def test_check_route_ignores_empty_cells(client):
    app.CURRENT["solution"] = copy.deepcopy(sudoku_logic.create_empty_board())
    app.CURRENT["solution"][0][0] = 1
    board = sudoku_logic.create_empty_board()

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_check_route_returns_no_incorrect_cells_for_matching_solution(client):
    solution = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]
    app.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": copy.deepcopy(solution)})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}


def test_hint_route_returns_one_correct_empty_non_given_cell(client):
    solution = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]
    puzzle = copy.deepcopy(solution)
    puzzle[0][0] = sudoku_logic.EMPTY
    app.CURRENT["puzzle"] = puzzle
    app.CURRENT["solution"] = solution

    response = client.post("/hint", json={"board": copy.deepcopy(puzzle)})

    assert response.status_code == 200
    assert response.get_json() == {"hint": {"row": 0, "col": 0, "value": 1}}


def test_hint_route_rejects_requests_when_no_empty_cells_are_available(client):
    solution = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]
    app.CURRENT["puzzle"] = copy.deepcopy(solution)
    app.CURRENT["solution"] = solution

    response = client.post("/hint", json={"board": copy.deepcopy(solution)})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No empty cells available for a hint"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"board": [[0] * sudoku_logic.SIZE]},
        {
            "board": [[True] + [0] * (sudoku_logic.SIZE - 1)]
            + [[0] * sudoku_logic.SIZE] * (sudoku_logic.SIZE - 1)
        },
    ],
)
def test_check_route_returns_a_json_error_for_invalid_board(client, payload):
    app.CURRENT["solution"] = sudoku_logic.create_empty_board()

    response = client.post("/check", json=payload)

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Board must be a 9x9 grid containing integers from 0 to 9"
    }


def test_check_route_returns_a_json_error_for_invalid_json_body(client):
    response = client.post("/check", data="{")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Request body must be a JSON object"}
