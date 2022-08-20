from __future__ import annotations
import copy
from typing import Collection, Iterable, List, Mapping, Optional, Union, Iterator
from typing import Any, Callable, MutableSequence, Generator

from tabulate import tabulate
from tinytim.functional.filter import filter_by_indexes, filter_list_by_indexes, indexes_from_filter
import tinytim.functional.table as func
import tinytim.functional.inplace as ip
from tinytim.functional.group import count_data, groupby, sum_data
from tinytim.functional.utils import all_bool, slice_to_range

import tinytable.datatypes as dt
import tinytable.column as column
from tinytable.group import Group
import tinytable.row as row
from tinytable.csv import read_csv_file
from tinytable.excel import read_excel_file
from tinytable.sqlite import read_sqlite_table
from tinytable.filter import Filter


class Table:
    """Data table organized into {column_name: list[values]}
    
       A pure Python version of Pandas DataFrame.
    """
    def __init__(self, data: dt.TableMapping = {}, labels=None) -> None:
        self.data = data
        self._store_data()
        self._validate()
        self.labels = labels if labels is None else list(labels)

    def _store_data(self):
        for col in self.data:
            self._store_column(col, self.data[col])

    def _store_column(self, column_name: str, values: Iterable, inplace=True) -> Union[None, Table]:
        values = list(values)
        if inplace:
            ip.edit_column(self.data, column_name, values)
        else:
            return Table(func.edit_column(self.data, column_name, values))
        
    def __len__(self) -> int:
        return func.row_count(self.data)
        
    def __repr__(self) -> str:
        index = True if self.labels is None else self.labels
        return tabulate(self, headers=self.columns, tablefmt='grid', showindex=index)
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.data)
    
    def __getitem__(self, key: Union[str, int]) -> Union[column.Column, row.Row, Table]:
        """
           Use str key for Column selection. Setting Column items changes parent Table.
           Use int key for Row selection. Setting Row items changes parent Table.

           Selecting subset of Table returns new Table,
           changes do not change original Table.
           Use int:int:int for index slice of Table rows.
           Use list of bool values to filter to Table of True rows.
           Use Filter to filter to Table of True rows.
        """
        # tbl['id'] -> Column
        if isinstance(key, str):
            return self.column(str(key))
        # tbl[1] -> Row
        if isinstance(key, int):
            index: int = self._convert_index(key)
            self._validate_index(index)
            return self.row(index)
        # tbl[1:4] -> Table
        if isinstance(key, slice):
            validate_int_slice(key)
            return self.filter_by_indexes(list(slice_to_range(key, len(self))))
        if isinstance(key, list):
            if all_bool(key):
                # tbl[[True, False, True, True]] -> Table
                return self.filter(key)
            # tbl[['id', 'name']] -> Table
            validate_list_key(key)
            return self.only_columns(key)
        if isinstance(key, Filter):
            # tbl[tbl['age'] >= 18] -> Table
            return self.filter(key)
        if isinstance(key, tuple):
            # tble[1, 2] or tbl[(1, 2)] -> labeled Row
            if self.labels is None:
                raise ValueError('Table must have labels to use tuple as key.')
            else:
                if key not in self.labels:
                    raise KeyError('tuple key is not in Table labels.')
                labels = self.labels
                if isinstance(labels, list):
                    index = labels.index(key)
                return self[index]
        raise TypeError('key must be str for column selection, int for row selection or slice for subset of Table rows.')
    
    def __setitem__(self, key: Union[str, int], values: MutableSequence) -> None:
        if type(key) == str:
            column_name: str = str(key)
            self.edit_column(column_name, values)
        elif type(key) == int:
            index: int = int(key)
            self.edit_row(index, values)

    def __delitem__(self, key: Union[str, int]) -> None:
        if type(key) == str:
            column_name: str = str(key)
            self.drop_column(column_name)
        elif type(key) == int:
            index: int = int(key)
            self.drop_row(index)

    @property
    def shape(self) -> tuple[int, int]:
        return func.shape(self.data)

    @property
    def size(self) -> int:
        return func.size(self.data)

    @property
    def columns(self) -> tuple[str]:
        """Column names."""
        return func.column_names(self.data)

    @columns.setter
    def columns(self, values: MutableSequence) -> None:
        """Set the value of the column names."""
        self.replace_column_names(values)

    @property
    def index(self) -> column.Column:
        return column.Column(func.index(self.data), None, self, self.labels)

    @property
    def values(self) -> tuple[tuple]:
        return func.values(self.data)

    def filter(self, f: Filter) -> Table:
        indexes = indexes_from_filter(f)
        return self.filter_by_indexes(indexes)

    def only_columns(self, column_names: MutableSequence[str]) -> Table:
        """Return new Table with only column_names Columns."""
        d = func.only_columns(self.data, column_names)
        return Table(d, self.labels)

    def _convert_index(self, index: int) -> int:
        if index < 0:
            return len(self) + index
        return index

    def _validate_index(self, index: int) -> None:
        if len(self) == 0:
            raise IndexError('row index out of range (empty Table)')
        upper_range = len(self) - 1
        if index > len(self) - 1 or index < 0:
            raise IndexError(f'row index {index} out of range (0-{upper_range})')
        
    def _validate(self) -> bool:
        count = None
        for key in self.data:
            col_count = len(self.data[key])
            if count is None:
                count = col_count
            if count != col_count:
                raise ValueError('All columns must be of the same length')
            count = col_count
        return True

    def _get_label(self, index: int) -> Union[None, List]:
        return None if self.labels is None else self.labels[index]
   
    def row(self, index: int) -> row.Row:
        label = self._get_label(index)
        return row.Row(func.row_dict(self.data, index), index, self, label)

    def column(self, column_name: str) -> column.Column:
        return column.Column(func.column_values(self.data, column_name), column_name, self, self.labels)

    def drop_column(self, column_name: str, inplace=True) -> Union[None, Table]:
        if inplace:
            ip.drop_column(self.data, column_name)
        else:
            return Table(func.drop_column(self.data, column_name), self.labels)

    def drop_row(self, index: int, inplace=True) -> Union[None, Table]:
        if inplace:
            ip.drop_row(self.data, index)
            ip.drop_label(self.labels, index)
        else:
            return Table(func.drop_row(self.data, index), func.drop_label(self.labels, index))

    def keys(self) -> tuple[str]:
        return self.columns
    
    def itercolumns(self) -> Generator[column.Column, None, None]:
        return column.itercolumns(self.data, self, self.labels)
            
    def iterrows(self) -> Generator[tuple[int, row.Row], None, None]:
        return row.iterrows(self.data, self, self.labels)

    def iteritems(self) -> Generator[tuple[str, column.Column], None, None]:
        return column.iteritems(self.data, self)

    def itertuples(self) -> Generator[tuple, None, None]:
        return func.itertuples(self.data)
    
    def edit_row(self, index: int, values: Union[Mapping, MutableSequence], inplace=True) -> Union[None, Table]:
        if inplace:
            if isinstance(values, Mapping):
                ip.edit_row_items(self.data, index, values)
            elif isinstance(values, MutableSequence):
                ip.edit_row_values(self.data, index, values)
        else:
            if isinstance(values, Mapping):
                data = func.edit_row_items(self.data, index, values)
            elif isinstance(values, MutableSequence):
                data = func.edit_row_values(self.data, index, values)
            return Table(data, copy.copy(self.labels))
            
    def edit_column(self, column_name: str, values: MutableSequence, inplace=True) ->Union[None, Table]:
        return self._store_column(column_name, values, inplace)

    def edit_value(self, column_name: str, index: int, value: Any, inplace=True) -> Union[None, Table]:
        if inplace:
            ip.edit_value(self.data, column_name, index, value)
        else:
            return Table(func.edit_value(self.data, column_name, index, value), copy.copy(self.labels))

    def copy(self, deep=False) -> Table:
        if deep:
             return Table(func.deepcopy_table(self.data), copy.deepcopy(self.labels))
        return Table(func.copy_table(self.data), copy.copy(self.labels))

    def cast_column_as(self, column_name: str, data_type: Callable) -> None:
        self.data[column_name] = [data_type(value) for value in self.data[column_name]]

    def replace_column_names(self, new_keys: MutableSequence[str]) -> None:
        if len(new_keys) != len(self.data.keys()):
            raise ValueError('new_keys must be same len as dict keys.')
        for new_key, old_key in zip(new_keys, self.data.keys()):
            if new_key != old_key:
                self.data[new_key] = self.data[old_key]
                del self.data[old_key]

    def to_csv(self, path: str) -> None:
        """Save Table as csv at path."""
        ...

    def to_excel(self, path: str) -> None:
        """Save Table in Excel Workbook."""
        ...

    def to_sqlite(self, path: str, table_name: str) -> None:
        """Save Table in sqlite database."""
        ...

    def label_head(self, n: int = 5) -> Union[None, List]:
        return None if self.labels is None else self.labels[:5]

    def label_tail(self, n: int = 5) -> Union[None, List]:
        return None if self.labels is None else self.labels[5:]

    def head(self, n: int = 5) -> Table:
        return Table(func.head(self.data, n), self.label_head(n))

    def tail(self, n: int = 5) -> Table:
        return Table(func.tail(self.data, n), self.label_tail(n))

    def nunique(self) -> dict[str, int]:
        """Count number of distinct values in each column.
           Return dict with number of distinct values.
        """
        return func.nunique(self.data)

    def filter_by_indexes(self, indexes: MutableSequence[int]) -> Table:
        """return only rows in indexes"""
        labels = None if self.labels is None else filter_list_by_indexes(self.labels, indexes)
        return Table(filter_by_indexes(self.data, indexes), labels=labels)

    def sample(self, n, random_state=None) -> Table:
        """return random sample of rows"""
        indexes = func.sample_indexes(self.data, n, random_state)
        labels = None if self.labels is None else filter_list_by_indexes(self.labels, indexes)
        return Table(filter_by_indexes(self.data, indexes), labels=labels)

    def groupby(self, by: Union[str, Collection]) -> Group:
        return Group([(value, Table(data)) for value, data in groupby(self.data, by)], by)

    def sum(self) -> dt.RowDict:
        return sum_data(self.data)

    def count(self) -> dt.RowDict:
        return count_data(self.data)


def read_csv(path: str):
    return Table(read_csv_file(path))


def read_excel(path: str, sheet_name: Optional[str] = None) -> Table:
    return Table(read_excel_file(path, sheet_name))


def read_sqlite(path: str, table_name: str) -> Table:
    return Table(read_sqlite_table(path, table_name))


def validate_int_slice(s: slice) -> None:
    if s.start is not None:
        if type(s.start) is not int:
            raise ValueError('slice start must be None or int')
    if s.stop is not None:
        if type(s.stop) is not int:
            raise ValueError('slice stop must be None or int')
    if s.step is not None:
        if type(s.step) is not int:
            raise ValueError('slice step must be None or int')


def validate_list_key(l: List) -> None:
    if not all(isinstance(item, str) for item in l):
        raise ValueError('All list items bust be str to use as key.')





