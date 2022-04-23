from pprint import pprint

from tootools import timeit

table = [[0] * 9] * 9


def is_valid(x, y, value):
    global table
    for n in range(9):
        if table[y][n] == value:
            return False
    for n in range(9):
        if table[n][x] == value:
            return False
    _b_x = x // 3 * 3
    _b_y = y // 3 * 3
    for _x in range(_b_x, _b_x + 3):
        for _y in range(_b_y, _b_y + 3):
            if table[_y][_x] == value:
                return False
    return True


class Found(Exception):
    pass


def solve():
    global table
    for _y in range(9):
        for _x in range(9):
            if table[_y][_x] == 0:
                for _value in range(1, 10):
                    if is_valid(_x, _y, _value):
                        table[_y][_x] = _value
                        _solved = solve()
                        if _solved:
                            return True
                        table[_y][_x] = 0
                return False
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
