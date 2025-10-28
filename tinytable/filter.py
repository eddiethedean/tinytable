from __future__ import annotations

from typing import Any, Callable, Iterator


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

    def __init__(self, column, func: Callable[[Any], bool]):
        self.column = column
        self.func = func

    def __iter__(self) -> FilterIterator:
        return FilterIterator(self)

    def __getitem__(self, key: int) -> bool:
        return self.func(self.column[key])

    def __len__(self) -> int:
        return len(self.column)

    def __contains__(self, item) -> bool:
        return item in list(iter(self))

    def __reversed__(self) -> Iterator[bool]:
        return iter(reversed(list(self)))

    def __and__(self, other) -> ChainFilter:
        """
        Use to chain filters.
        [False, True, True] & [True, False, True] -> [False, False True]

        Example
        -------
        >>> from tinytable import Table
        >>> tbl = Table({'x': [0, 1, 2], 'y': [11, 11, 0])
        >>> f = tbl['x'] > 1 & tbl['y'] < 10
        >>> tbl[f].data
        {'x': [2], 'y': [0]}
        """
        return ChainFilter(list(x & y for x, y in zip(self, other)))

    def __or__(self, other: Filter) -> ChainFilter:
        """
        Use to chain filters.
        [False, True, True] | [True, False, True] -> [True, True True]

        Example
        -------
        >>> from tinytable import Table
        >>> tbl = Table({'x': [0, 1, 2], 'y': [11, 11, 0])
        >>> f = tbl['x'] < 1 | tbl['y'] < 10
        >>> tbl[f].data
        {'x': [0, 1], 'y': [11, 11]}
        """
        return ChainFilter(list(x | y for x, y in zip(self, other)))

    def index(self, value: Any, start: int = 0, stop: int = -1) -> int:
        if stop == -1:
            return list(iter(self))[start:].index(value) + start
        return list(iter(self))[start:stop].index(value) + start

    def count(self, value) -> int:
        return list(iter(self)).count(value)


class ChainFilter(Filter):
    def __init__(self, values: list[bool]):
        self.values = values

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, i: int) -> bool:
        return self.values[i]

    def __len__(self) -> int:
        return len(self.values)

    def __contains__(self, value) -> bool:
        return value in self.values

    def __reversed__(self) -> Iterator[bool]:
        return iter(reversed(self.values))
