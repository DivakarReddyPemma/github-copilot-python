// Client-side rendering and interaction for the Flask-backed Sudoku.
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let startedAt = null;
let hintsUsed = 0;
let gameFinished = false;

function getBoard() {
  const inputs = document.querySelectorAll('.sudoku-cell');
  return Array.from({length: SIZE}, (_, row) =>
    Array.from({length: SIZE}, (_, col) => {
      const value = inputs[row * SIZE + col].value;
      return value ? Number.parseInt(value, 10) : 0;
    })
  );
}

function clearCellFeedback() {
  document.querySelectorAll('.sudoku-cell').forEach((input) => {
    input.classList.remove('conflict', 'incorrect');
  });
}

function updateConflicts() {
  const inputs = document.querySelectorAll('.sudoku-cell');
  const board = getBoard();
  const conflicts = new Set();

  // Compare each filled cell with peers in its row, column, and 3x3 box.
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const value = board[row][col];
      if (!value) continue;

      for (let otherRow = 0; otherRow < SIZE; otherRow++) {
        for (let otherCol = 0; otherCol < SIZE; otherCol++) {
          if (otherRow === row && otherCol === col) continue;
          const sameRow = otherRow === row;
          const sameColumn = otherCol === col;
          const sameBox = Math.floor(otherRow / 3) === Math.floor(row / 3)
            && Math.floor(otherCol / 3) === Math.floor(col / 3);
          if ((sameRow || sameColumn || sameBox) && board[otherRow][otherCol] === value) {
            conflicts.add(row * SIZE + col);
            conflicts.add(otherRow * SIZE + otherCol);
          }
        }
      }
    }
  }

  inputs.forEach((input, index) => {
    input.classList.toggle('conflict', conflicts.has(index));
  });
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainder = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainder}`;
}

function updateTimer() {
  if (startedAt === null) return;
  const elapsed = Math.floor((Date.now() - startedAt) / 1000);
  document.getElementById('timer').innerText = formatTime(elapsed);
}

function startTimer() {
  if (timerInterval !== null) clearInterval(timerInterval);
  startedAt = Date.now();
  document.getElementById('timer').innerText = '00:00';
  timerInterval = setInterval(updateTimer, 1000);
}

function stopTimer() {
  updateTimer();
  if (timerInterval !== null) clearInterval(timerInterval);
  timerInterval = null;
}

function showError(error) {
  const message = document.getElementById('message');
  message.className = 'error';
  message.innerText = error.message;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.inputMode = 'numeric';
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      input.addEventListener('input', (event) => {
        const val = event.target.value.replace(/[^1-9]/g, '');
        event.target.value = val;
        clearCellFeedback();
        updateConflicts();
        document.getElementById('message').innerText = '';
        document.getElementById('message').className = '';
        if (getBoard().every((row) => row.every((value) => value !== 0))) {
          checkSolution();
        }
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.readOnly = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.readOnly = false;
        inp.disabled = false;
        inp.classList.remove('prefilled', 'hint');
      }
    }
  }
  gameFinished = false;
  clearCellFeedback();
}

async function newGame() {
  const message = document.getElementById('message');
  try {
    const difficulty = document.getElementById('difficulty').value;
    const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || 'Unable to start a new game.');
    }
    renderPuzzle(data.puzzle);
    hintsUsed = 0;
    document.getElementById('hints-used').innerText = '0';
    startTimer();
    message.innerText = '';
    message.className = '';
  } catch (error) {
    showError(error);
  }
}

async function checkSolution() {
  try {
    const board = getBoard();
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || 'Unable to check this puzzle.');
    }

    const incorrect = new Set(data.incorrect.map(([row, col]) => row * SIZE + col));
    const inputs = document.querySelectorAll('.sudoku-cell');
    inputs.forEach((input, index) => {
      input.classList.toggle('incorrect', incorrect.has(index));
    });

    const complete = board.every((row) => row.every((value) => value !== 0));
    const message = document.getElementById('message');
    if (complete && incorrect.size === 0) {
      if (!gameFinished) {
        stopTimer();
        gameFinished = true;
        inputs.forEach((input) => { input.disabled = true; });
      }
      message.className = 'success';
      message.innerText = `Congratulations! You solved it in ${document.getElementById('timer').innerText} with ${hintsUsed} hints used.`;
    } else {
      message.className = incorrect.size ? 'error' : '';
      message.innerText = incorrect.size ? 'Some cells are incorrect.' : 'No incorrect entries found yet.';
    }
  } catch (error) {
    showError(error);
  }
}

async function useHint() {
  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getBoard()})
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || 'Unable to get a hint.');
    }

    const {row, col, value} = data.hint;
    const input = document.querySelector(
      `.sudoku-cell[data-row="${row}"][data-col="${col}"]`
    );
    input.value = value;
    input.readOnly = true;
    input.classList.add('hint');
    hintsUsed++;
    document.getElementById('hints-used').innerText = String(hintsUsed);
    clearCellFeedback();
    updateConflicts();
    document.getElementById('message').innerText = '';
    document.getElementById('message').className = '';
  } catch (error) {
    showError(error);
  }
}

window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('get-hint').addEventListener('click', useHint);
  newGame();
});