# Copilot Instructions: Sudoku Flask App

## Project overview
This is a Python Flask Sudoku game with a plain HTML, CSS and vanilla JavaScript front end. All app code lives in the `starter` folder.

## Code style
- Write readable, consistent, maintainable code.
- Use clear names, small single-purpose functions, and comments or docstrings that explain why, not just what.
- Python: follow PEP 8. JavaScript: use const/let, never var.

## Structure
- `sudoku_logic.py`: all game logic (solver, puzzle generation, unique-solution check, validation).
- `app.py`: Flask routes only. No game logic here.
- `templates/`: HTML.
- `static/`: CSS (`styles.css`) and JavaScript (`main.js`).
- `tests/`: pytest tests.

## Error handling
- Validate all input in routes and return consistent JSON errors with a clear message and a proper HTTP status code.
- Never let the app crash on bad input.

## Game rules to respect
- Every puzzle must have exactly one solution.
- Prefilled cells are locked.
- Difficulty controls how many cells are prefilled (Easy, Medium, Hard).
- Hints fill one correct cell and lock it.
- The Top 10 fastest times are stored in localStorage.

## UI and accessibility
- Support light and dark mode, and phone and desktop screens.
- Use alternating colors for the 3x3 boxes.
- Keep text and buttons readable with good contrast, and keep the page keyboard-friendly.

## Testing
- Add or update pytest tests for any new backend logic.
- Run `python -m pytest` from the `starter` folder after every change.
- Don't change existing tests just to make them pass.

## Working rules
- Keep changes small and focused.
- Don't add features that weren't requested.
- Explain any non-obvious code in comments.