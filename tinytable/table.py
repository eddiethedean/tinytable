from __future__ import annotations
from typing import Iterable, List, Mapping, Optional, Union, Iterator
from typing import Any, Callable, MutableSequence, Generator

from tabulate import tabulate


import tinytable.functional.table as func
import tinytable.functional.inplace as ip
import tinytable.datatypes as dt
import tinytable.column as column
import tinytable.row as row

from tinytable.csv import read_csv_file
from tinytable.excel import read_excel_file
from tinytable.sqlite import read_sqlite_table
from tinytable.utils import all_bool, slice_to_range
from tinytable.filter import Filter




class Table:
    """Data table organized into {column_name: list[values]}
    
       A pure Python version of Pandas DataFrame.
    """
    def __init__(self, data: dt.TableMapping = {}) -> None:
        self.data = data
        self._store_data()
        self._validate()

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
        return tabulate(self, headers=self.columns, tablefmt='grid')
    
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
        return column.Column(func.index(self.data), None, self)

    @property
    def values(self) -> tuple[tuple]:
        return func.values(self.data)

    def filter(self, f: Filter) -> Table:
        indexes = self.indexes_from_filter(f)
        return self.filter_by_indexes(indexes)

    def indexes_from_filter(self, f: Filter) -> List[int]:
        return [i for i, b in enumerate(f) if b]

    def only_columns(self, column_names: MutableSequence[str]) -> Table:
        """Return new Table with only column_names Columns."""
        d = func.only_columns(self.data, column_names)
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
   
    def row(self, index: int) -> row.Row:
        return row.Row(func.row_dict(self.data, index), index, self)

    def column(self, column_name: str) -> column.Column:
        return column.Column(func.column_values(self.data, column_name), column_name, self)

    def drop_column(self, column_name: str, inplace=True) -> Union[None, Table]:
        if inplace:
            ip.drop_column(self.data, column_name)
        else:
            return Table(func.drop_column(self.data, column_name))

    def drop_row(self, index: int, inplace=True) -> Union[None, Table]:
        if inplace:
            ip.drop_row(self.data, index)
        else:
            return Table(func.drop_row(self.data, index))

    def keys(self) -> tuple[str]:
        return self.columns
    
    def itercolumns(self) -> Generator[column.Column, None, None]:
        return column.itercolumns(self.data, self)
            
    def iterrows(self) -> Generator[tuple[int, row.Row], None, None]:
        return row.iterrows(self.data, self)

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
            return Table(data)
            
    def edit_column(self, column_name: str, values: MutableSequence, inplace=True) ->Union[None, Table]:
        return self._store_column(column_name, values, inplace)

    def edit_value(self, column_name: str, index: int, value: Any, inplace=True) -> Union[None, Table]:
        if inplace:
            ip.edit_value(self.data, column_name, index, value)
        else:
            return Table(func.edit_value(self.data, column_name, index, value))

    def copy(self, deep=False) -> Table:
        if deep:
             return Table(func.deepcopy_table(self.data))
        return Table(func.copy_table(self.data))

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

    def head(self, n: int = 5) -> Table:
        return Table(func.head(self.data, n))

    def tail(self, n: int = 5) -> Table:
        return Table(func.tail(self.data, n))

    def nunique(self) -> dict[str, int]:
        """Count number of distinct values in each column.
           Return dict with number of distinct values.
        """
        return func.nunique(self.data)

    def filter_by_indexes(self, indexes: MutableSequence[int]) -> Table:
        """return only rows in indexes"""
        d = func.filter_by_indexes(self.data, indexes)
        return Table(d)

    def sample(self, n, random_state=None) -> Table:
        """return random sample of rows"""
        return Table(func.sample(self.data, n, random_state))
    

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





