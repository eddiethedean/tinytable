from typing import Any, Collection, Generator, Iterable, Mapping, Union
from copy import copy, deepcopy

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
        self._validate()
        
    def __len__(self) -> int:
        if len(self.data) == 0:
            return 0
        return len(self.data[self.columns[0]])
        
    def __repr__(self) -> str:
        return f'Table({self.data})'
    
    def __iter__(self) -> Generator[dict, None, None]:
        return self.itercolumns()
    
    def __getitem__(self, key: Union[str, int]) -> Union[Column, Row]:
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
            
    def row(self, index: int) -> Row:
        return Row(row_dict(self.data, index), index, self)

    def column(self, column_name: str) -> Column:
        return Column(self.data[column_name], column_name, self)

    def rows_slice(self, slc: slice):
        ...

    def columns_subset(self, column_names: Iterable[str]):
        ...

    def drop_column(self, column_name: str) -> None:
        del self.data[column_name]

    def drop_row(self, index: int) -> None:
        for col in self.columns:
            self.data[col].pop(index)
    
    @property
    def columns(self) -> list[str]:
        """Column names."""
        return list(self.data.keys())
    
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
        self.data[column_name] = list(values)
            
    def edit_value(self, column_name: str, index: int, value: Any) -> None:
        self.data[column_name][index] = value

    def copy(self, deep=False):
        if deep:
             return type(self)({key: deepcopy(values) for key, values in self.data.items()})
        return type(self)({key: copy(values) for key, values in self.data.items()})

    
def iterrows(data):
    if len(data) == 0:
        return
    i = 0
    while True:
        try:
            yield {col: data[col][i] for col in data}
        except IndexError:
            return
        i += 1
