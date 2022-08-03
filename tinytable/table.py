from typing import Any, Callable, Collection, Generator, Iterable, Iterator, List, Mapping, Union
from copy import copy, deepcopy
import csv

from tabulate import tabulate

from tinytable.row import Row
from tinytable.column import Column
from tinytable.row import row_dict


class Table:
    """Data table organized into {column_name: list[values]}
    
       A pure Python version of Pandas DataFrame.
    """
    def __init__(self, data, deep_copy=False):
        if deep_copy:
            self.data = deepcopy(data)
        else:
            self.data = data
        self._store_data()
        self._validate()

    def _store_data(self):
        for col in self.data:
            self._store_column(col, self.data[col])

    def _store_column(self, column_name: str, values: Collection) -> None:
        self.data[column_name] = list(values)
        
    def __len__(self) -> int:
        if len(self.data) == 0:
            return 0
        return len(self.data[self.columns[0]])
        
    def __repr__(self) -> str:
        return tabulate(self, headers=self.columns, tablefmt='grid')
    
    def __iter__(self) -> Iterator[str]:
        return iter(self.data)
    
    def __getitem__(self, key: Union[str, int]) -> Union[Column, Row]:
        """Use str key for Column selection.
           Use int key for Row selection.

           Use int:int:int for slice of rows selection.
        """
        if type(key) == str:
            return self.column(str(key))
        if type(key) == int:
            index: int = self._convert_index(key)
            self._validate_index(index)
            return self.row(index)
        raise TypeError('key must be str for column selection or int for row selection.')

    def _convert_index(self, index) -> int:
        index = int(index)
        if index < 0:
            return len(self) + index
        return index

    def _validate_index(self, index: int) -> None:
        if len(self) == 0:
            raise IndexError('row index out of range (empty Table)')
        upper_range = len(self) - 1
        if index > len(self) - 1 or index < 0:
            raise IndexError(f'row index {index} out of range (0-{upper_range})')
    
    def __setitem__(self, key: Union[str, int], values: Union[Collection, Mapping]) -> None:
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

    def shape(self) -> tuple[int, int]:
        return len(self.index), len(self.columns)

    def head(self, n=5):
        ...

    def tail(self, n=5):
        ...
            
    def row(self, index: int) -> Row:
        return Row(row_dict(self.data, index), index, self)

    def column(self, column_name: str) -> Column:
        return Column(self.data[column_name], column_name, self)

    def rows_slice(self, slc: slice):
        for i in range(slc.start, slc.stop, slc.step):
            ...
        
    def columns_subset(self, column_names: Iterable[str]):
        ...

    def drop_column(self, column_name: str) -> None:
        del self.data[column_name]

    def drop_row(self, index: int) -> None:
        for col in self.columns:
            self.data[col].pop(index)
    
    @property
    def columns(self) -> List[str]:
        """Column names."""
        return list(self.data.keys())

    @columns.setter
    def columns(self, values: Collection) -> None:
        """Set the value of the column names."""
        self.replace_column_names(values)

    def keys(self) -> List[str]:
        return self.columns

    @property
    def index(self) -> Column:
        return Column(range(len(self)), name=None)
    
    def itercolumns(self) -> Generator[dict, None, None]:
        for col in self.columns:
            yield {col: self.data[col]}
            
    def iterrows(self) -> Generator[dict, None, None]:
        return iterrows(self.data)
    
    @property
    def values(self) -> list[list]:
        return [list(row.values()) for row in self.iterrows()]
    
    def edit_row(self, index: int, values: Union[Mapping, Collection]) -> None:
        if isinstance(values, Mapping):
            for col in values:
                self.data[col][index] = values[col]
        elif isinstance(values, Collection):
            if len(values) != len(self.columns):
                raise AttributeError('values length must match columns length.')
            for col, value in zip(self.columns, values):
                self.data[col][index] = value
            
    def edit_column(self, column_name: str, values: Iterable) -> None:
        self._store_column(column_name, values)
            
    def edit_value(self, column_name: str, index: int, value: Any) -> None:
        self.data[column_name][index] = value

    def copy(self, deep=False):
        if deep:
             return type(self)({key: deepcopy(values) for key, values in self.data.items()})
        return type(self)({key: copy(values) for key, values in self.data.items()})

    def cast_column_as(self, column_name: str, data_type: Callable) -> None:
        self.data[column_name] = [data_type(value) for value in self.data[column_name]]

    def replace_column_names(self, new_keys: Collection) -> None:
        if len(new_keys) != len(self.keys()):
            raise ValueError('new_keys must be same len as dict keys.')
        for new_key, old_key in zip(new_keys, self.keys()):
            if new_key != old_key:
                self[new_key] = self[old_key]
                del self[old_key]

    def to_csv(self, path: str) -> None:
        """Save Table as csv at path."""
        ...

    
def iterrows(data) -> Generator[dict, None, None]:
    if len(data) == 0:
        return
    i = 0
    while True:
        try:
            yield {col: data[col][i] for col in data}
        except IndexError:
            return
        i += 1


def read_csv(path: str, chunk=None) -> Table:
    """
    Reads a table object from given CSV file.
    """
    columnNames = []
    matrix = []
    first = True
    with open(path, 'r', newline='') as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        for row in csv.reader(f, dialect):
            if first:
                columnNames = row
                first = False
            else:
                matrix.append(list(row))
        return Table(dict(zip(columnNames, matrix)))