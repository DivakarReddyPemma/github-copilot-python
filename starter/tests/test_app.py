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


@pytest.mark.parametrize(("query", "expected_clues"), [("", 35), ("?clues=40", 40)])
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


def test_check_route_returns_no_incorrect_cells_for_matching_solution(client):
    solution = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]
    app.CURRENT["solution"] = solution

    response = client.post("/check", json={"board": copy.deepcopy(solution)})

    assert response.status_code == 200
    assert response.get_json() == {"incorrect": []}
