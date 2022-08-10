"""Functional programming functions.
   Always returns a value without changing anything outside function.
"""


from typing import Any, Callable, Collection, Generator, List, Mapping, Optional
import random
import copy

from tinytable.utils import uniques


TableMapping = Mapping[str, Collection]
TableDict = dict[str, Collection]
RowDict = dict[str, Any]


def first_column_name(data: TableMapping) -> str:
    """Return the name of the first column.
       Raises StopIteration if data has zero columns.
    """
    return next(iter(data))


def column_count(data: TableMapping) -> int:
    """Return the number of columns in data."""
    return len(data)


def row_count(data: TableMapping) -> int:
    """Return the number of rows in data."""
    if column_count(data) == 0: return 0
    return len(data[first_column_name(data)])


def shape(data: TableMapping) -> tuple[int, int]:
    """Return data row count, column count tuple."""
    col_count = column_count(data)
    if col_count == 0: return 0, 0
    return row_count(data), col_count


def size(data: TableMapping) -> int:
    """Return data row count multiplied by column count."""
    rows, columns = shape(data)
    return rows * columns


def column_names(data: TableMapping) -> tuple[str]:
    """Return data column names."""
    return tuple(data)


def replace_column_names(data: TableMapping, new_names: Collection[str]) -> TableDict:
    """Return a new dict same column data but new column names."""
    old_names = column_names(data)
    if len(new_names) != len(old_names):
        raise ValueError('new_names must be same size as data column_count.')
    return {new_name: data[old_name] for new_name, old_name in zip(new_names, old_names)}


def index(data: TableMapping) -> tuple[int]:
    """Return tuple of data column indexes."""
    return tuple(range(row_count(data)))


def has_mapping_attrs(obj: Any) -> bool:
    """Check if object has all Mapping attrs."""
    mapping_attrs = ['__getitem__', '__iter__', '__len__',
                     '__contains__', 'keys', 'items', 'values',
                     'get', '__eq__', '__ne__']
    return all(hasattr(obj, a) for a in mapping_attrs)


def data_columns_same_len(data: TableMapping) -> bool:
    """Check if data columns are all the same len."""
    if column_count(data) == 0: return True
    it = iter(data.values())
    the_len = len(next(it))
    return all(len(l) == the_len for l in it)


def valid_table_mapping(data: TableMapping) -> bool:
    """Check if data is a true TableMapping."""
    if not has_mapping_attrs(data): return False
    return data_columns_same_len(data)


def table_value(data: TableMapping, column_name: str, index: int) -> Any:
    """Return one value from column at row index."""
    return data[column_name][index]


def row_dict(data: TableMapping, index: int) -> RowDict: 
    """Return one row from data at index."""
    return {col: table_value(col, index) for col in column_names(data)}


def row_values(data: TableMapping, index: int) -> tuple:
    """Return a tuple of the values at row index."""
    return tuple(values[index] for values in data.values())


def itercolumns(data: TableMapping) -> Generator[tuple[str, tuple], None, None]:
    """Return a generator of tuple column name, column values."""
    for col in column_names(data):
        yield col, tuple(data[col])
            

def iterrows(data: TableMapping) -> Generator[tuple[int, RowDict], None, None]:
    """Return a generator of tuple row index, row dict values."""
    for i in index(data):
        yield i, row_dict(data, i)


def itervalues(data: TableMapping) -> Generator[tuple, None, None]:
    """Return a generator of tuple row values."""
    for _, row in iterrows(data):
        yield tuple(row.values())


def values(data: TableMapping) -> tuple[tuple]:
    """Return tuple of tuple row values."""
    return tuple(itervalues(data))


def filter_by_indexes(data: TableMapping, indexes: Collection[int]) -> TableDict:
    """return only rows in indexes"""
    return {col: [values[i] for i in indexes] for col, values in data.items()}


def only_columns(data: TableMapping, column_names: Collection[str]) -> TableDict:
    """Return new TableDict with only column_names."""
    return {col: data[col] for col in column_names}


def sample(data: TableMapping, n: int, random_state: Optional[int] = None) -> TableDict:
    """return random sample of n rows"""
    if random_state is not None:
        random.seed(random_state)
    indexes = random.sample(range(row_count(data)), n)
    return filter_by_indexes(data, indexes)


def nunique(data: TableMapping) -> dict[str, int]:
    """Count number of distinct values in each column.
       Return dict with number of distinct values.
    """
    return {col: len(uniques(values)) for col, values in data.items()}


def head(data: TableMapping, n: int = 5) -> TableDict:
    """Return the first n rows of data."""
    return {col: values[:n] for col, values in data.items()}


def tail(data: TableMapping, n: int = 5) -> TableDict:
    """Return the last n rows of data."""
    return {col: values[-n:] for col, values in data.items()}


def edit_row_items(data: TableMapping, index: int, items: Mapping) -> TableDict:
    """Return a new dict with row index changed to mapping items values."""
    new_data = copy.copy(data)
    for col in items:
        new_data[col][index] = items[col]
    return new_data


def edit_row_values(data: TableMapping, index: int, values: Collection) -> TableDict:
    """Return a new dict with row index changed to values."""
    if len(values) != column_count(data):
        raise AttributeError('values length must match columns length.')
    new_data = copy_table(data)
    for col, value in zip(column_names(data), values):
        new_data[col][index] = value
    return new_data


def edit_column(data: TableMapping, column_name: str, values: Collection) -> TableDict:
    """Returns a new dict with values added to data in named column.
       Overrides existing values if column exists,
       Created new column with values if column does not exist.
    """
    if len(values) != row_count(data):
        raise ValueError('values length must match data rows count.')
    new_data = copy_table(data)
    new_data[column_name] = values


def copy_table(data: TableMapping) -> TableDict:
    return copy.copy(data)


def deepcopy_table(data: TableMapping) -> TableDict:
    return copy.deepcopy(data)


def cast_column_as(data: TableMapping, column_name: str, data_type: Callable) -> TableDict:
    """Return a new dict with named column cast as data_type."""
    new_data = copy_table(data)
    new_data[column_name] = [data_type(value) for value in new_data[column_name]]
    return new_data


def drop_row(data: TableMapping, index: int) -> TableDict:
    """Return a new dict with index row removed from data."""
    new_data = copy_table(data)
    for col in column_names(data):
        new_data[col].pop(index)
    return new_data


def drop_column(data: TableMapping, column_name: str) -> TableDict:
    """Return a new dict with the named column removed from data."""
    new_data = copy_table(data)
    del new_data[column_name]
    return new_data
