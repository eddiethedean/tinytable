from __future__ import annotations
from typing import Callable


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


class Filter:
    """Object used to filter a Table by criteria.
       Returned when Column is used with boolean operator.
       Column == 1 or Column >= 10

       Pass as key in Table to filter to True rows.
       Table[Column > 1] -> Table where each row Column > 1
    """
    def __init__(self, column, func: Callable):
        self.column = column
        self.func = func

    def __iter__(self) -> FilterIterator:
        return FilterIterator(self)
