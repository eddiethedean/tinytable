from __future__ import annotations
from typing import Any, Callable, Sequence


class FilterIterator:
    """Passed when iterating through Filter
       Applies filter func to parent Column values.
    """
    def __init__(self, filter: Filter) -> None:
        self.filter = filter
        self.iter = iter(self.filter.column)

    def __next__(self) -> bool:
        return self.filter.func(next(self.iter))

    def __iter__(self):
        return self


class Filter(Sequence):
    """Object used to filter a Table by criteria.
       Returned when Column is used with boolean operator.
       Column == 1 or Column >= 10

       Pass as key in Table to filter to True rows.
       Table[Column > 1] -> Table where each row Column > 1
    """
    def __init__(self, column, func: Callable[[Any], bool]):
        self.column = column
        self.func = func

    def __iter__(self) -> FilterIterator:
        return FilterIterator(self)

    def __getitem__(self, key) -> bool:
        return self.func(self.column[key])

    def __len__(self) -> int:
        return len(self.column)

    def __contains__(self, item) -> bool:
        return item in list(iter(self))

    def __reversed__(self) -> Filter:
        return Filter(reversed(self.column), self.func)

    def index(self, value) -> int:
        return list(iter(self)).index(value)

    def count(self, value) -> int:
        return list(iter(self)).count(value)
