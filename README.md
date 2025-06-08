# Sudoku Solver

This project presents two Python scripts designed to solve Sudoku puzzles, each employing a different algorithmic approach. Whether you prefer a straightforward brute-force method or a more sophisticated constraint-based technique, these solvers offer insights into tackling Sudoku challenges programmatically.

## Solver Approaches

This repository includes two distinct Sudoku solver implementations:

### 1. Brute-Force Backtracking Solver (`brute-force-backtracking-solver.py`)

This solver uses a classic brute-force backtracking algorithm. The core idea is:
- Iterate through empty cells one by one.
- For each empty cell, try placing digits from 1 to 9.
- If a digit is valid according to Sudoku rules (no conflicts in the row, column, or 3x3 subgrid), place it and recursively move to the next empty cell.
- If the recursive call finds a solution, propagate it back.
- If no digit from 1 to 9 works for the current cell, or if a recursive call returns without a solution, backtrack by resetting the cell and trying a different digit in the previous cell.
- The process continues until a complete and valid solution is found or all possibilities have been exhausted.

This method is guaranteed to find a solution if one exists, but it can be slow for harder puzzles.

### 2. Clue-Based Constraint Propagation Solver (`sudoku-clue-solver.py`)

This solver employs a more advanced strategy that combines constraint propagation with backtracking for efficiency:
- **Initialization**: The grid is initialized where each unknown cell holds a set of all possible candidates (digits 1-9). Known cells are assigned their given values.
- **Clue Processing**: Each known or deduced cell value is treated as a "clue".
- **Constraint Propagation**: When a cell's value is determined, this value is removed as a candidate from all other cells in the same row, column, and 3x3 subgrid.
    - If this removal causes another cell to have only one remaining candidate, that cell's value is now determined, and it becomes a new clue to be processed. This chain reaction continues until no more immediate deductions can be made.
- **Backtracking Search**: If, after processing all clues, the puzzle is not yet solved (some cells still have multiple candidates), the algorithm intelligently selects an ambiguous cell (typically one with the fewest candidates). It then tries each of its candidate values one by one:
    - A new solver state is created for each candidate.
    - The clue processing and constraint propagation steps are recursively applied.
    - If a path leads to an invalid state (e.g., a cell has no possible candidates), that path is abandoned (backtracking), and the next candidate is tried.
- The first complete and valid solution found is returned.

This approach is generally much faster for complex Sudoku puzzles as it significantly prunes the search space.

## Usage

### Running the Solvers

Both scripts can be run directly from the command line:

- **Brute-Force Backtracking Solver**:
  ```bash
  python brute-force-backtracking-solver.py
  ```
  This script contains a hardcoded Sudoku puzzle example within the file itself. It will print the solution to the console.

- **Clue-Based Constraint Propagation Solver (`sudoku-clue-solver.py`)**:
  This script now uses a command-line interface (CLI) to solve Sudoku puzzles provided as a string.

  **Installation for CLI:**
  The CLI requires the `click` library. You can install it using pip:
  ```bash
  pip install click
  ```

  **Running the Solver via CLI:**
  You can solve a puzzle by providing the puzzle string directly as an argument or by specifying a file that contains the puzzle string.

  1.  **Using a direct puzzle string:**
      ```bash
      python sudoku-clue-solver.py solve "PUZZLE_STRING"
      ```
      -   The `PUZZLE_STRING` must be exactly 81 characters long.
      -   Use digits `1` through `9` for known values and `+` for empty cells.
      -   The string represents the 9x9 Sudoku grid row by row, from left to right.
      -   Example: `python sudoku-clue-solver.py solve "53++7+++++6++195+++++98++++6+8+++6+++3+4++8+3++17+++2+++6+6++++28++++419++5++++8"`

  2.  **Using a file input:**
      Use the `--file` (or `-f`) option to specify a path to a text file containing the puzzle.
      ```bash
      python sudoku-clue-solver.py solve --file path/to/your/puzzle.txt
      ```
      -   The file should contain a single line with the 81-character puzzle string.
      -   The format of the puzzle string within the file is the same as described above.

  **Input Requirements:**
  -   You must provide either a direct puzzle string argument or use the `--file` option.
  -   If both a direct puzzle string and a `--file` option are provided, the puzzle from the file specified by `--file` will be used.

  The solver will print the solution to the console, along with the runtime. The `sudokus.txt` file is no longer directly used by this script for input but can serve as a source for puzzle strings.

## Dependencies

- The `brute-force-backtracking-solver.py` script is written in standard Python and does not require any external libraries beyond those included in the Python Standard Library.
- The `sudoku-clue-solver.py` script requires the `click` library for its command-line interface.
  ```bash
  pip install click
  ```
The `tootools.py` file contains helper classes and functions used by the solvers and is part of this repository.
