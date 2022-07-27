from typing import Any, Generator, Iterable

from row import Row
from column import Column

class Data:
    """Data table organized into {column_name: list[values]}
    
       A pure Python version of Pandas DataFrame.
    """
    def __init__(self, data):
        self.data = data
        self._validate()
        
    def __len__(self) -> int:
        if len(self.data) == 0:
            return 0
        return len(self.data[self.column_names[0]])
        
    def __repr__(self) -> str:
        return f'Data({self.data})'
    
    def __iter__(self) -> Column:
        return self.itercolumns()
    
    def __getitem__(self, column_name: str) -> Column:
        return column(self.data, column_name)
    
    def __setitem__(self, column_name: str, values) -> None:
        self.edit_column(column_name, values)
        
    def _validate(self) -> bool:
        count = None
        for key in self.data:
            col_count = len(self.data[key])
            if count is None:
                count = col_count
            if count != col_count:
                raise ValueError('All columns must be of the same length')
            count = col_count
            
    def row(self, index: int) -> Row:
        return Row(row(self.data, index), index, self)
    
    @property
    def columns(self) -> list[str]:
        return list(self.data.keys())
    
    def itercolumns(self) -> Generator[Column, None, None]:
        for col in self.columns():
            yield {col: self.data[col]}
            
    def iterrows(self) -> Generator[Row, None, None]:
        return iterrows(self.data)
    
    @property
    def values(self) -> list[list]:
        return [list(row.values()) for row in self.iterrows()]
    
    def edit_row(self, row: Row) -> None:
        for col in row.columns:
            self.data[col][row.index] = row[col]
            
    def edit_column(self, column_name: str, values: Iterable) -> None:
        self.data[column_name] = list(values)
            
    def edit_value(self, column_name: str, index: int, value: Any) -> None:
        self.data[column_name][index] = value

    
def column(data, col: str) -> dict[str, list]:
    return {col: data[col]}


def row(data, index: int):
    return {col: data[col][index] for col in data}


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
