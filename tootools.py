import contextlib
import time


class EmptyCell(Exception):
    pass


class IncompleteGroup(Exception):
    pass


class Solution(Exception):
    pass


def group_by(collection, group_size):
    result = []
    for _item in collection:
        result.append(_item)
        if len(result) == group_size:
            yield result
            result = []
    if result:
        raise IncompleteGroup(result)


@contextlib.contextmanager
def timeit(context):
    _ts = time.time()
    yield
    _te = time.time()
    print(f"{context}: {_te - _ts:.3f} sec")
