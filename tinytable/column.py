from typing import Any, List


class Column:
    def __init__(self, data: List, name: str, parent=None):
        self.data = list(data)
        self.name = name
        self.parent = None
        
    def __len__(self) -> int:
        return len(self.data)
    
    def __repr__(self) -> str:
        return f'Column({self.data}, name={self.name})'
    
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


def column_dict(data, col: str) -> dict[str, List]:
    return {col: data[col]}