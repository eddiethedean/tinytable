from typing import Any, Mapping, MutableSequence

import tinytable.datatypes as dt
import tinytable.functional.table as func


def edit_row_items(data: dt.TableMapping, index: int, items: Mapping) -> None:
    """Changes row index to mapping items values."""
    for col in items:
        data[col][index] = items[col]


def edit_row_values(data: dt.TableMapping, index: int, values: MutableSequence) -> None:
    """Changed row index to values."""
    if len(values) != func.column_count(data):
        raise AttributeError('values length must match columns length.')
    for col, value in zip(func.column_names(data), values):
        data[col][index] = value


def edit_column(data: dt.TableMapping, column_name: str, values: MutableSequence) -> None:
    """Add values to data in named column.
       Overrides existing values if column exists,
       Created new column with values if column does not exist.
    """
    if len(values) != func.row_count(data):
        raise ValueError('values length must match data rows count.')
    data[column_name] = values


def drop_row(data: dt.TableMapping, index: int) -> None:
    """Remove index row from data."""
    for col in func.column_names(data):
        data[col].pop(index)


def drop_column(data: dt.TableMapping, column_name: str) -> None:
    """Return a new dict with the named column removed from data."""
    del data[column_name]


def edit_value(data: dt.TableMapping, column_name: str, index: int, value: Any) -> None:
    """Edit the value in named column as row index."""
    data[column_name][index] = value