from typing import Callable, Iterable, List, Collection
from tinytable.datatypes import TableMapping


TableFilter = Iterable[bool]


def column_filter(column: Iterable, func: Callable) -> List[bool]:
    return [func(item) for item in column]


def indexes_from_filter(f: TableFilter) -> List[int]:
    return [i for i, b in enumerate(f) if b]


def filter_by_indexes(data: TableMapping, indexes: Collection[int]) -> TableMapping:
    """return only rows in indexes"""
    return {col: [values[i] for i in indexes] for col, values in data.items()}
    

def filter_data(data: TableMapping, f: TableFilter) -> TableMapping:
    indexes = indexes_from_filter(f)
    return filter_by_indexes(data, indexes)


def filter_by_column_func(data: TableMapping, column_name: str, func) -> TableMapping:
    """Return only rows of data where named column equals value."""
    indexes = [i for i, val in enumerate(data[column_name]) if func(val)]
    return filter_by_indexes(data, indexes)


def filter_by_column_eq(data: TableMapping, column_name: str, value) -> TableMapping:
    """Return only rows of data where named column equals value."""
    return filter_by_column_func(data, column_name, lambda x: x == value)


def filter_by_column_ne(data: TableMapping, column_name: str, value) -> TableMapping:
    """Return only rows of data where named column does not equal value."""
    return filter_by_column_func(data, column_name, lambda x: x != value)


def filter_by_column_gt(data: TableMapping, column_name: str, value) -> TableMapping:
    """Return only rows of data where named column is greater than value."""
    return filter_by_column_func(data, column_name, lambda x: x > value)


def filter_by_column_lt(data: TableMapping, column_name: str, value) -> TableMapping:
    """Return only rows of data where named column is less than value."""
    return filter_by_column_func(data, column_name, lambda x: x < value)


def filter_by_column_ge(data: TableMapping, column_name: str, value) -> TableMapping:
    """Return only rows of data where named column is greater than or equal value."""
    return filter_by_column_func(data, column_name, lambda x: x >= value)


def filter_by_column_le(data: TableMapping, column_name: str, value) -> TableMapping:
    """Return only rows of data where named column is less than or equal value."""
    return filter_by_column_func(data, column_name, lambda x: x <= value)


def filter_by_column_isin(data: TableMapping, column_name: str, values) -> TableMapping:
    """Return only rows of data where named column is in values."""
    return filter_by_column_func(data, column_name, lambda x: x in values)


def filter_by_column_notin(data: TableMapping, column_name: str, values) -> TableMapping:
    """Return only rows of data where named column is not in values."""
    return filter_by_column_func(data, column_name, lambda x: x not in values)


