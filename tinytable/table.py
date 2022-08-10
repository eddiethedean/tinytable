from __future__ import annotations
from typing import List, Mapping, Optional, Union, Iterator
from typing import Any, Callable, Collection, Generator
from copy import copy, deepcopy
import random

from tabulate import tabulate

from tinytable.functions import column_names, index, only_columns, row_count, row_dict, shape, size, values
from tinytable.row import Row, iterrows
from tinytable.column import Column, ittercolumns
from tinytable.csv import read_csv_file
from tinytable.excel import read_excel_file
from tinytable.sqlite import read_sqlite_table
from tinytable.utils import all_bool, uniques, slice_to_range
from tinytable.filter import Filter


class Table:
    """Data table organized into {column_name: list[values]}
    
       A pure Python version of Pandas DataFrame.
    """
    def __init__(self, data: Mapping[str, Collection] = {}) -> None:
        self.data = data
        self._store_data()
        self._validate()

    def _store_data(self):
        for col in self.data:
            self._store_column(col, self.data[col])

    def _store_column(self, column_name: str, values: Collection) -> None:
        self.data[column_name] = list(values)
        
    def __len__(self) -> int:
        return row_count(self.data)
        
    def __repr__(self) -> str:
        return tabulate(self, headers=self.columns, tablefmt='grid')
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.data)
    
    def __getitem__(self, key: Union[str, int]) -> Union[Column, Row, Table]:
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
            return self.filter_by_indexes(slice_to_range(key, len(self)))
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
        raise TypeError('key must be str for column selection, int for row selection or slice for subset of Table rows.')
    
    def __setitem__(self, key: Union[str, int], values: Collection) -> None:
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
        return shape(self.data)

    @property
    def size(self) -> int:
        return size(self.data)

    @property
    def columns(self) -> tuple[str]:
        """Column names."""
        return column_names(self.data)

    @columns.setter
    def columns(self, values: Collection) -> None:
        """Set the value of the column names."""
        self.replace_column_names(values)

    @property
    def index(self) -> Column:
        return Column(index(self.data), None, self)

    @property
    def values(self) -> tuple[tuple]:
        return values(self.data)

    def filter(self, f: Filter) -> Table:
        indexes = self.indexes_from_filter(f)
        return self.filter_by_indexes(indexes)

    def indexes_from_filter(self, f: Filter) -> List[int]:
        return [i for i, b in enumerate(f) if b]

    def only_columns(self, column_names: Collection[str]) -> Table:
        """Return new Table with only column_names Columns."""
        d = only_columns(self.data)
        return Table(d)

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
   
    def row(self, index: int) -> Row:
        return Row(row_dict(self.data, index), index, self)

    def column(self, column_name: str) -> Column:
        return Column(self.data[column_name], column_name, self)

    def drop_column(self, column_name: str) -> None:
        del self.data[column_name]

    def drop_row(self, index: int) -> None:
        for col in self.columns:
            self.data[col].pop(index)

    def keys(self) -> List[str]:
        return self.columns
    
    def itercolumns(self) -> Generator[Column, None, None]:
        return ittercolumns(self.data, self)
            
    def iterrows(self) -> Generator[Row, None, None]:
        return iterrows(self.data, self)
    
    def edit_row(self, index: int, values: Union[Mapping, Collection]) -> None:
        if isinstance(values, Mapping):
            for col in values:
                self.data[col][index] = values[col]
        elif isinstance(values, Collection):
            if len(values) != len(self.columns):
                raise AttributeError('values length must match columns length.')
            for col, value in zip(self.columns, values):
                self.data[col][index] = value
            
    def edit_column(self, column_name: str, values: Collection) -> None:
        self._store_column(column_name, values)
            
    def edit_value(self, column_name: str, index: int, value: Any) -> None:
        self.data[column_name][index] = value

    def copy(self, deep=False) -> Table:
        if deep:
             return type(self)({key: deepcopy(values) for key, values in self.data.items()})
        return Table({key: copy(values) for key, values in self.data.items()})

    def cast_column_as(self, column_name: str, data_type: Callable) -> None:
        self.data[column_name] = [data_type(value) for value in self.data[column_name]]

    def replace_column_names(self, new_keys: Collection[str]) -> None:
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

    def head(self, n: int = 5) -> Table:
        return Table({col: values[:n] for col, values in self.data.items()})

    def tail(self, n: int = 5) -> Table:
        return Table({col: values[-n:] for col, values in self.data.items()})

    def nunique(self) -> dict[str, int]:
        """Count number of distinct values in each column.
           Return dict with number of distinct values.
        """
        return {col: len(uniques(values)) for col, values in self.data.items()}

    def filter_by_indexes(self, indexes: Collection[int]) -> Table:
        """return only rows in indexes"""
        d = {col: [values[i] for i in indexes] for col, values in self.data.items()}
        return Table(d)

    def sample(self, n, random_state=None) -> Table:
        """return random sample of rows"""
        if random_state is not None:
            random.seed(random_state)
        indexes = random.sample(range(len(self)), n)
        return self.filter_by_indexes(indexes)
    

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



