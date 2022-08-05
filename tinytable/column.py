from typing import Any, Callable, Generator, List, Union

from tabulate import tabulate


class Column:
    def __init__(self, data: List, name: Union[str, None], parent=None):
        self.data = list(data)
        self.name = name
        self.parent = None
        
    def __len__(self) -> int:
        return len(self.data)
    
    def __repr__(self) -> str:
        header = 'index' if self.name is None else self.name
        return tabulate({header: self.data}, headers=[header], tablefmt='grid', showindex=True)
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index: int) -> Any:
        return self.data[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        self.data[index] = value
        if self.parent is not None:
            self.parent.edit_value(self.name, index, value)

    def drop(self):
        """drop Column from parent"""
        if self.parent is not None:
            self.parent.drop_column(self.name)
            self.parent = None

    def cast_as(self, data_type: Callable) -> None:
        self.data = [data_type(item) for item in self.data]
        if self.parent is not None:
            self.parent.cast_column_as(self.name, data_type)


def column_dict(data, col: str) -> dict[str, List]:
    return {col: data[col]}


def ittercolumns(data: dict[str, List], parent) -> Generator[Column, None, None]:
    for col in data.keys():
        yield Column(data[col], col, parent)