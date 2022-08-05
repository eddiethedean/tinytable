from typing import Any, Generator, List

from tabulate import tabulate


class Row:
    def __init__(self, data: dict[str, List], index: int, parent=None):
        self.data = data
        self.index = index
        self.parent = parent
        
    def __len__(self) -> int:
        return len(self.data)
    
    def __iter__(self):
        return row_values_generator(self.data)
    
    def __repr__(self) -> str:
        return tabulate([self], headers=self.columns, tablefmt='grid', showindex=[self.index])
    
    def __getitem__(self, column: str) -> Any:
        return self.data[column]
    
    def __setitem__(self, column: str, value: Any) -> None:
        self.data[column] = value
        if self.parent is not None:
            self.parent.edit_value(column, self.index, value)
    
    @property
    def columns(self) -> List[str]:
        return list(self.data.keys())

    def keys(self) -> List[str]:
        return list(self.data.keys())

    def drop(self) -> None:
        """drop Row from parent"""
        if self.parent is not None:
            self.parent.drop_row(self.index)
            self.parent = None

    def values(self) -> List[Any]:
        return list(self.data.values())


def row_dict(data, index: int):
    return {col: data[col][index] for col in data}


def row_values_generator(row: dict[str, Any]):
    for key in row:
        yield row[key]


def iterrows(data: dict[str, List], parent) -> Generator[Row, None, None]:
    if len(data) == 0:
        return
    i = 0
    while True:
        try:
            yield Row({col: data[col][i] for col in data}, i, parent)
        except IndexError:
            return
        i += 1

