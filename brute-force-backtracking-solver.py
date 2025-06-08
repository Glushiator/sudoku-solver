"""
This script solves a Sudoku puzzle using a brute-force backtracking algorithm.

The Sudoku puzzle is represented as a 9x9 grid, where 0 indicates an empty cell.
The script attempts to fill in the empty cells with digits from 1 to 9,
respecting the Sudoku rules:
- Each digit must appear exactly once in each row.
- Each digit must appear exactly once in each column.
- Each digit must appear exactly once in each 3x3 subgrid.

The script uses a global variable `table` to store the Sudoku grid.
While this is functional, a potential improvement would be to pass the table
as a parameter to the functions, making the code more modular and testable.
"""
from pprint import pprint

from tootools import timeit

# Initialize an empty Sudoku grid. This will be overwritten by the actual puzzle.
# Note: Using `[[0] * 9] * 9` creates a list of 9 references to the *same* list,
# which is not suitable for a Sudoku grid where rows must be distinct.
# However, this initial table is immediately overwritten by the actual puzzle input.
table = [[0] * 9] * 9


def is_valid(x, y, value):
    """
    Checks if placing a given value in a specific cell (x, y) is valid
    according to Sudoku rules.

    Args:
        x (int): The column index of the cell (0-8).
        y (int): The row index of the cell (0-8).
        value (int): The value (1-9) to check.

    Returns:
        bool: True if the placement is valid, False otherwise.

    Note:
        This function uses the global `table` variable to access the current
        state of the Sudoku grid.
    """
    global table
    # Check if the value already exists in the current row
    for n in range(9):
        if table[y][n] == value:
            return False
    # Check if the value already exists in the current column
    for n in range(9):
        if table[n][x] == value:
            return False
    # Check if the value already exists in the current 3x3 subgrid
    _b_x = x // 3 * 3  # Starting x-coordinate of the 3x3 subgrid
    _b_y = y // 3 * 3  # Starting y-coordinate of the 3x3 subgrid
    for _x in range(_b_x, _b_x + 3):
        for _y in range(_b_y, _b_y + 3):
            if table[_y][_x] == value:
                return False
    return True


def solve():
    """
    Solves the Sudoku puzzle using a brute-force backtracking algorithm.

    The function iterates through each cell of the grid. If a cell is empty (0),
    it tries to place digits from 1 to 9. If a digit is valid (according to
    Sudoku rules), it places the digit and recursively calls `solve` to continue
    solving the puzzle.

    If the recursive call returns True (meaning a solution is found), this
    function also returns True. If no valid digit can be placed in the current
    cell, or if the recursive call returns False, the function backtracks by
    resetting the cell to 0 and trying the next digit or returning False.

    Returns:
        bool: True if the puzzle is solved, False if no solution is found for
              the current path.

    Note:
        This function uses and modifies the global `table` variable.
        The algorithm will find the first solution it encounters.
    """
    global table
    for _y in range(9):  # Iterate through rows
        for _x in range(9):  # Iterate through columns
            if table[_y][_x] == 0:  # Found an empty cell
                for _value in range(1, 10):  # Try numbers 1 through 9
                    if is_valid(_x, _y, _value):
                        table[_y][_x] = _value  # Place the valid number
                        # Recursively try to solve the rest of the puzzle
                        if solve():
                            return True  # Puzzle solved
                        # Backtrack: if the recursive call didn't lead to a solution,
                        # reset the cell and try the next number
                        table[_y][_x] = 0
                # If no number from 1-9 works in this cell, this path is invalid
                return False
    # If all cells are filled (no cell is 0), the puzzle is solved
    return True


table = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 3, 0, 8, 5],
    [0, 0, 1, 0, 2, 0, 0, 0, 0],
    [0, 0, 0, 5, 0, 7, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 1, 0, 0],
    [0, 9, 0, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0, 0, 7, 3],
    [0, 0, 2, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 9],
]


with timeit("runtime"):
    solve()
    pprint(table)
