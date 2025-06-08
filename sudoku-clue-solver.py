"""
This script solves Sudoku puzzles using a backtracking algorithm combined with
a constraint propagation strategy.

The overall strategy is as follows:
1. Initialize the Sudoku grid: Cells can either contain a known digit (1-9) or a
   set of possible candidates for that cell. Initially, unknown cells contain
   all digits (1-9) as candidates.
2. Process initial clues: For each known digit in the input puzzle, treat it as a
   "clue".
3. Apply clues: When a cell's value is determined (either from input or deduction),
   remove that value from the candidate sets of all other cells in the same row,
   column, and 3x3 subgrid.
4. Constraint propagation: If removing a candidate from a cell results in that
   cell having only one possible candidate left, that cell's value is now determined.
   This new determined value becomes a new "clue" that is then processed.
5. Backtracking search: If, after processing all available clues, the puzzle is
   not yet solved (i.e., some cells still have multiple candidates), the algorithm
   selects an ambiguous cell (a cell with the fewest candidates) and tries each
   of its candidate values one by one.
   - For each tried value, a new Sudoku state is created, and the process_clues
     method is called recursively.
   - If a recursive call leads to a solution, that solution is propagated up.
   - If a recursive call leads to an invalid state (e.g., a cell has no possible
     candidates), that path is abandoned (backtracking), and the next candidate
     value is tried.
6. Solution detection: The puzzle is considered solved when all cells have a
   single, determined value. An exception (`Solution`) is used to signal that a
   solution has been found and to carry the solved grid.
7. Error handling: An `EmptyCell` exception is raised if a cell ends up with no
   valid candidates, indicating an invalid path in the backtracking search.
"""
import re
from collections import namedtuple
from copy import deepcopy
from pprint import pprint
from typing import Union, Set, List, Tuple, Optional

from tootools import EmptyCell, group_by, Solution, timeit

# Represents a determined value for a cell.
# x (int): The column index of the cell (0-8).
# y (int): The row index of the cell (0-8).
# value (int): The determined digit (1-9) for the cell.
Clue = namedtuple('Clue', 'x y value')

# Represents a cell that still has multiple possible candidates.
# Used to select the next cell for the backtracking search.
# x (int): The column index of the cell (0-8).
# y (int): The row index of the cell (0-8).
# values (Set[int]): The set of possible candidate digits for the cell.
AmbiguousCell = namedtuple('AmbiguousCell', 'x y values')


def clue_candidates_key(item: AmbiguousCell):
    return len(item.values), item.x, item.y

# Type alias for the Sudoku grid.
# It's a list of 9 rows, where each row is a list of 9 cells.
# Each cell can either be:
#   - An integer (1-9) if the value is determined.
#   - A set of integers (1-9) representing possible candidates for that cell.
#   - None, typically during initial setup before cells are populated with sets.
SolutionType = List[List[Optional[Union[Set[int], int]]]]

# Type alias for a list of clues.
# Each clue is a tuple (x, y, value) representing a determined cell.
CluesType = List[Tuple[int, int, int]]


class Sudoku:
    """
    Represents a Sudoku puzzle and provides methods to solve it using
    constraint propagation and backtracking.
    """

    solution: SolutionType
    clues: CluesType # Stores clues to be processed. A clue is (x, y, value)

    def __init__(self, previous_state: SolutionType = None, clue: Optional[Clue] = None):
        """
        Initializes a Sudoku grid.

        If `previous_state` is None, it's an initial run, and the grid is
        initialized with all cells as None (will be populated with sets or numbers
        by `process_input`).

        If `previous_state` is provided (typically during a recursive call),
        it deepcopies the `previous_state` and applies the given `clue`.
        Applying a clue means setting the cell's value to the clue's value
        and adding this clue to the list of clues to be processed.

        Args:
            previous_state (SolutionType, optional): The state of the Sudoku grid
                from a previous step, used for recursive calls. Defaults to None.
            clue (Clue, optional): A specific clue (x, y, value) to apply to the
                newly created Sudoku state. Used in recursive calls when trying
                a candidate for an ambiguous cell. Defaults to None.
        """
        self.clues = []
        if previous_state is None:
            # Initial setup: create a 9x9 grid.
            # Cells will be filled by `process_input`.
            self.solution = [[None] * 9 for _ in range(9)]
        else:
            self.solution = deepcopy(previous_state)
            _x, _y, _value = clue
            self.solution[_y][_x] = {_value}
            self.clues.append(clue)

    def _remove(self, x: int, y: int, value: int):
        """
        Removes a `value` from the set of candidates for the cell at (x, y).

        This is a core part of the constraint propagation.
        - If the cell's value is already determined (an int), do nothing.
        - If `value` is in the cell's candidate set, remove it.
        - If removing `value` makes the candidate set empty, it means there's no
          valid number for this cell in the current path, so raise `EmptyCell`
          exception to signal a conflict.
        - If removing `value` leaves only one candidate in the set, this cell's
          value is now determined. Convert the cell to this single value and
          add it as a new `Clue` to `self.clues` for further processing.

        Args:
            x (int): The column index of the cell.
            y (int): The row index of the cell.
            value (int): The candidate value to remove from the cell.

        Raises:
            EmptyCell: If removing `value` results in the cell having no
                       possible candidates.
        """
        _cell = self.solution[y][x]
        if isinstance(_cell, int): # Cell value is already determined
            return

        if value in _cell: # Check if the value is a candidate
            _cell.remove(value)
            if not _cell: # No candidates left
                raise EmptyCell(x, y)
            if len(_cell) == 1: # Only one candidate left, cell is now determined
                determined_value = tuple(_cell)[0]
                self.solution[y][x] = determined_value # Update cell to the determined value
                self.clues.append(Clue(x, y, determined_value)) # Add as a new clue

    def _apply_clue(self, x: int, y: int, value: int):
        """
        Applies a confirmed `clue` (a cell at (x,y) has a definite `value`).

        This involves:
        1. Setting the cell (x,y) to `value`. (This should ideally be done
           before calling, or ensured by `_remove` if it's a deduction)
        2. Removing `value` as a candidate from all other cells in the same row,
           column, and 3x3 subgrid by calling `_remove`.

        Args:
            x (int): The column index of the determined cell.
            y (int): The row index of the determined cell.
            value (int): The determined value of the cell.
        """
        # Remove 'value' from other cells in the same row
        for _y_peer in range(9):
            if _y_peer != y:
                self._remove(x, _y_peer, value)

        # Remove 'value' from other cells in the same column
        for _x_peer in range(9):
            if _x_peer != x:
                self._remove(_x_peer, y, value)

        # Remove 'value' from other cells in the same 3x3 subgrid
        _base_x = x // 3 * 3 # Top-left x-coordinate of the 3x3 subgrid
        _base_y = y // 3 * 3 # Top-left y-coordinate of the 3x3 subgrid
        for _y_sub in range(_base_y, _base_y + 3):
            for _x_sub in range(_base_x, _base_x + 3):
                # Check if it's not the cell itself
                # (though _remove handles cells that are already int)
                if (_x_sub != x or _y_sub != y): # Ensure not to remove from the clue cell itself
                    self._remove(_x_sub, _y_sub, value)

    def process_input(self, clues_input: str):
        """
        Parses the input string representing a Sudoku puzzle and initializes the grid.

        The input string is expected to be a sequence of digits (1-9) for
        determined cells and '+' for unknown cells. The string is read row by row.

        - Determined cells are stored as integers.
        - Unknown cells (represented by '+') are initialized with a set of all
          possible candidates {1, 2, ..., 9}.
        - All initially determined cells are added to `self.clues` to be
          processed by `_apply_clue` later.

        Args:
            clues_input (str): A string representing the Sudoku puzzle.
                               Example: "++3+2++++1..."
        """
        # `re.findall` extracts all digits and '+' characters.
        # `group_by` splits this flat list into groups of 9, representing rows.
        for _y, _values_in_row in enumerate(group_by(re.findall('[\\d+]', clues_input), 9)):
            for _x, _value_char in enumerate(_values_in_row):
                if _value_char != '+':
                    _value = int(_value_char)
                    self.solution[_y][_x] = _value # Set determined value
                    self.clues.append(Clue(_x, _y, _value)) # Add as an initial clue
                else:
                    # For unknown cells, initialize with all candidates {1..9}
                    self.solution[_y][_x] = set(range(1, 10))

    def process_clues(self):
        """
        Processes all queued clues using constraint propagation. If the puzzle
        is not solved after this, it initiates a backtracking search.

        Logic flow:
        1. Clue Propagation Loop:
           - Continuously takes a clue from `self.clues` and applies it using
             `_apply_clue`. Applying a clue might trigger `_remove`, which in
             turn might discover new determined cells and add them to `self.clues`.
           - This loop continues until `self.clues` is empty, meaning all direct
             deductions from the current state have been made.

        2. Check if Solved:
           - After the clue propagation loop, it checks if the puzzle is solved
             using `_solved()`.
           - If solved, it raises a `Solution` exception, passing the solved grid.
             This exception is used to unwind the recursion and signal success.

        3. Backtracking Search (if not solved):
           - If the puzzle is not solved, it means there are still cells with
             multiple candidates (ambiguous cells).
           - It calls `_candidates()` to get a list of candidate values to try for
             the "best" ambiguous cell (typically the one with the fewest options).
           - It iterates through these candidate values:
             - For each candidate `_clue` (representing a potential value for the
               chosen ambiguous cell):
               - It creates a new `Sudoku` instance (`_sudoku`) as a deep copy of
                 the current state, but with the candidate `_clue` applied.
               - It recursively calls `_sudoku.process_clues()`.
               - Exception Handling for Recursion:
                 - `try...except EmptyCell`: If the recursive call raises
                   `EmptyCell`, it means that trying that particular candidate
                   `_clue` led to an invalid state (a cell with no options).
                   The exception is caught, and the loop continues to try the
                   next candidate for the ambiguous cell (this is the "backtracking" step).
                 - If `_sudoku.process_clues()` completes without `EmptyCell` and
                   eventually raises `Solution` from a deeper recursive call,
                   that `Solution` exception will naturally propagate upwards, as
                   it's not caught here.

        Raises:
            Solution: If the puzzle is solved at any point (either after initial
                      clue propagation or during a recursive call).
            EmptyCell: (implicitly, can be raised by _apply_clue->_remove) if applying
                       a clue directly leads to an invalid state in the current instance.
        """
        # --- 1. Clue Propagation Loop ---
        while self.clues:
            _x, _y, _value = self.clues.pop(0) # Process clues in FIFO order for broader search first
            self._apply_clue(_x, _y, _value)

        # --- 2. Check if Solved ---
        if self._solved():
            # If solved, raise Solution exception to carry the result up the recursion stack.
            raise Solution(self.solution)
        else:
            # --- 3. Backtracking Search ---
            # If not solved, find the cell with the minimum number of candidates.
            _next_candidate_clues = self._candidates()

            # Iterate through each candidate for the chosen ambiguous cell.
            for _clue_to_try in _next_candidate_clues:
                # print("trying", _clue_to_try) # For debugging
                # Create a new Sudoku state by deepcopying the current grid
                # and applying the candidate clue.
                _sudoku_branch = Sudoku(self.solution, _clue_to_try)
                try:
                    # Recursively call process_clues on the new state.
                    _sudoku_branch.process_clues()
                except EmptyCell:
                    # This branch led to an invalid state (a cell has no candidates).
                    # Backtrack: print("failure", _clue_to_try) # For debugging
                    pass # Try the next candidate for the ambiguous cell.

    def _solved(self) -> bool:
        """
        Checks if the Sudoku puzzle is solved.

        The puzzle is solved if every cell contains a single integer value (not a set
        of candidates).

        Returns:
            bool: True if the puzzle is solved, False otherwise.
        """
        for y, row in enumerate(self.solution):
            for x, _cell in enumerate(row):
                # If a cell is still a set, or if it's a set with not exactly one item
                # (though after processing, sets should ideally become single ints or stay >1)
                if isinstance(_cell, set): # or (isinstance(_cell, set) and len(_cell) != 1):
                    return False
        return True

    def _candidates(self) -> List[Clue]:
        """
        Finds the "best" ambiguous cell to try next for backtracking and returns
        its candidate values as a list of `Clue` objects.

        The "best" cell is chosen as the one with the fewest candidate values.
        If multiple cells have the same minimum number of candidates, the one
        with the lower row index, then lower column index, is preferred (due to
        `clue_candidates_key` sorting).

        Returns:
            List[Clue]: A list of `Clue` objects, each representing one of the
                        candidate values for the chosen ambiguous cell. The list
                        is sorted by the candidate value itself.
                        Returns an empty list if no ambiguous cells are found (e.g., if solved
                        or in an error state, though `_solved` should catch the solved case).
        """
        _ambiguities: List[AmbiguousCell] = []
        # Iterate through all cells to find those with multiple candidates.
        for y, row in enumerate(self.solution):
            for x, _cell in enumerate(row):
                if isinstance(_cell, set) and len(_cell) > 1: # Only consider sets with >1 candidates
                    _ambiguities.append(AmbiguousCell(x, y, _cell))

        if not _ambiguities:
            return [] # Should not happen if called after _solved() returns False

        # Sort ambiguous cells: first by the number of candidates (ascending),
        # then by y, then by x, to ensure deterministic behavior.
        _ambiguities = sorted(_ambiguities, key=clue_candidates_key)

        # Choose the first cell from the sorted list (the "best" one).
        _chosen_ambiguous_cell = _ambiguities[0]
        _x, _y, _candidate_values = _chosen_ambiguous_cell

        # Create a list of Clue objects for each candidate value in the chosen cell,
        # sorted by the value itself for deterministic trial order.
        return [Clue(_x, _y, _value) for _value in sorted(list(_candidate_values))]


def _main():
    with open('sudokus.txt') as _clues:
        for _clues_input in _clues.read().split('--'):
            with timeit("runtime"):
                _sudoku = Sudoku()
                _sudoku.process_input(_clues_input)
                try:
                    _sudoku.process_clues()
                    print("NO SOLUTION")
                except Solution as e:
                    print("SOLVED")
                    pprint(e.args[0])
                except EmptyCell as e:
                    print(f"ERROR: empty call at: {e.args}")


if __name__ == '__main__':
    # import cProfile
    _main()
    # cProfile.run('_main()')
