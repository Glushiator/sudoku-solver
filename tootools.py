"""
This module provides utility classes and functions used by the Sudoku solvers.

It includes:
- Custom exception classes for handling specific Sudoku-solving scenarios like
  an empty cell (no possible candidates) or finding a solution.
- A generic grouping function.
- A context manager for timing code execution.
"""
import contextlib
import time


class EmptyCell(Exception):
    """
    Exception raised when a cell in the Sudoku grid has no possible valid
    candidates left. This typically indicates an incorrect path in a
    backtracking algorithm.
    The arguments of the exception are usually the (x, y) coordinates of the cell.
    """
    pass


class IncompleteGroup(Exception):
    """
    Exception raised by the `group_by` function if the input collection
    cannot be evenly divided into groups of the specified size (i.e.,
    the last group is smaller than `group_size`).
    The argument of the exception is the incomplete last group.
    """
    pass


class Solution(Exception):
    """
    Exception raised when a solution to the Sudoku puzzle is found.
    This is used as a control flow mechanism to signal that a valid solution
    has been reached, often to unwind a recursion stack.
    The argument of the exception is typically the solved Sudoku grid.
    """
    pass


def group_by(collection, group_size: int):
    """
    Splits a collection into groups of a specified size.

    This is a generator function that yields each group as a list.

    Args:
        collection: An iterable collection to be grouped.
        group_size (int): The desired size of each group.

    Yields:
        list: A list containing `group_size` items from the collection.

    Raises:
        IncompleteGroup: If the total number of items in the collection is not
                         a multiple of `group_size`, meaning the last group
                         would be smaller than `group_size`. The exception
                         carries the incomplete last group as its argument.
    """
    result = []
    for _item in collection:
        result.append(_item)
        if len(result) == group_size:
            yield result
            result = [] # Reset for the next group
    # After the loop, if 'result' is not empty, it means the last group was incomplete.
    if result:
        raise IncompleteGroup(result)


@contextlib.contextmanager
def timeit(context: str):
    """
    A simple context manager for timing a block of code.

    It records the time at the beginning and end of the `with` block
    and prints the elapsed time along with a given context message.

    Args:
        context (str): A string message to print alongside the timing information,
                       describing what was being timed.

    Example:
        with timeit("Data processing"):
            # Code to measure
            time.sleep(1)
        # Output: Data processing: 1.000 sec (approximately)
    """
    _ts = time.time()  # Record start time
    yield  # Execute the code block within the 'with' statement
    _te = time.time()  # Record end time
    # Print the context and the difference between end and start time, formatted to 3 decimal places.
    print(f"{context}: {_te - _ts:.3f} sec")
