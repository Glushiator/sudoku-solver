import re
from collections import namedtuple
from copy import deepcopy
from pprint import pprint
from typing import Union, Set, List, Tuple, Optional

from tootools import EmptyCell, group_by, Solution, timeit

Clue = namedtuple('Clue', 'x y value')
AmbiguousCell = namedtuple('AmbiguousCell', 'x y values')


def clue_candidates_key(item: AmbiguousCell):
    return len(item.values), item.x, item.y


SolutionType = List[List[Optional[Union[Set, int]]]]
CluesType = List[Tuple[int, int, int]]


class Sudoku:

    solution: SolutionType
    clues: CluesType

    def __init__(self, previous_state: SolutionType = None, clue: Optional[Clue] = None):
        """
        if it's an initial run, then fill the grid with None
        if it's a recursive run then deepcopy the source grid
        and apply possible clue to try it
        :param previous_state:
        :param clue:
        """
        self.clues = []
        if previous_state is None:
            self.solution = [[None] * 9 for _ in range(9)]
        else:
            self.solution = deepcopy(previous_state)
            _x, _y, _value = clue
            self.solution[_y][_x] = {_value}
            self.clues.append(clue)

    def _remove(self, x, y, value):
        """
        removes a value from a cell,
        if the cell becomes empty throws an error
        if the cell becomes single value cell then queues that number as a new clue
        :param x:
        :param y:
        :param value:
        :return:
        """
        _cell = self.solution[y][x]
        if isinstance(_cell, int):
            return
        if value in _cell:
            _cell.remove(value)
            if not _cell:
                raise EmptyCell(x, y)
            if len(_cell) == 1:
                self.clues.append(Clue(x, y, tuple(_cell)[0]))

    def _apply_clue(self, x, y, value):
        """
        applies a clue to the grid removing that number from
        the rest of the affected cells
        :param x:
        :param y:
        :param value:
        :return:
        """
        for _y in range(9):
            if _y != y:
                self._remove(x, _y, value)
        for _x in range(9):
            if _x != x:
                self._remove(_x, y, value)
        _base_x = x // 3 * 3
        _base_y = y // 3 * 3
        for _x in range(_base_x, _base_x + 3):
            for _y in range(_base_y, _base_y + 3):
                if _x != x and _y != y:
                    self._remove(_x, _y, value)

    def process_input(self, clues_input):
        """
        reads input text and loads all known numbers and queues them as clues
        :param clues_input:
        :return:
        """
        for _y, _values in enumerate(group_by(re.findall('[\\d+]', clues_input), 9)):
            for _x, _value in enumerate(_values):
                if _value != '+':
                    _value = int(_value)
                    self.solution[_y][_x] = _value
                    self.clues.append((_x, _y, _value))
                else:
                    self.solution[_y][_x] = set(range(1, 10))

    def process_clues(self):
        """
        processes all queued clues and if not solved
        searches for a cell with multiple possibilities
        and iterates through them recursively trying
        to find a solution, if a grid is solved than throws
        a Solution exception that caries out the solution
        :return:
        """
        while self.clues:
            _x, _y, _value = self.clues.pop()
            self._apply_clue(_x, _y, _value)
        if self._solved():
            raise Solution(self.solution)
        else:
            _next_clues = self._candidates()
            for _clue in _next_clues:
                # print("trying", _clue)
                _sudoku = Sudoku(self.solution, _clue)
                try:
                    _sudoku.process_clues()
                except EmptyCell:
                    # print("failure", _clue)
                    pass

    def _solved(self):
        """
        checks if the game is solved
        :return:
        """
        for y, row in enumerate(self.solution):
            for x, _cell in enumerate(row):
                if isinstance(_cell, set) and len(_cell) != 1:
                    return False
        return True

    def _candidates(self):
        """
        looks for a cell that has the lowest number of possible candidates,
        preferring those in the upper left corner of the grid
        :return:
        """
        _ambiguities: List[AmbiguousCell] = []
        for y, row in enumerate(self.solution):
            for x, _cell in enumerate(row):
                if isinstance(_cell, set) and len(_cell) != 1:
                    _ambiguities.append(AmbiguousCell(x, y, _cell))
        _ambiguities = sorted(_ambiguities, key=clue_candidates_key)
        # print(f"{_ambiguities=}")
        # raise Exception("STOP")
        # _ambiguities = sorted(_ambiguities, key=lambda i: len(i[-1]))
        _x, _y, _values = _ambiguities[0]
        return [Clue(_x, _y, _value) for _value in sorted(_values)]


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
