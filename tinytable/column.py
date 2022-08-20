from __future__ import annotations
from typing import Any, Callable, MutableSequence, Generator, List, Sequence, Union

from tabulate import tabulate
import tinytim.functions as tim

import tinytable.datatypes as dt
from tinytable.filter import Filter
from tinytable.group import Group


class Column:
    def __init__(self, data: Sequence, name: Union[str, None], parent=None, labels=None):
        self.data = list(data)
        self.name = name
        self.parent = parent
        self.labels = labels

        
    def __len__(self) -> int:
        return len(self.data)
    
    def __repr__(self) -> str:
        header = 'index' if self.name is None else self.name
        index = True if self.labels is None else self.labels
        return tabulate({header: self.data}, headers=[header], tablefmt='grid', showindex=index)
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index: int) -> Any:
        return self.data[index]
    
    def __setitem__(self, index: int, value: Any) -> None:
        self.data[index] = value
        if self.parent is not None:
            self.parent.edit_value(self.name, index, value)

    def __eq__(self, value: Any) -> Filter:
        return Filter(self, lambda x: x == value)

    def __ne__(self, value: Any) -> Filter:
        return Filter(self, lambda x: x != value)

    def __gt__(self, value: Any) -> Filter:
        return Filter(self, lambda x: x > value)

    def __lt__(self, value: Any) -> Filter:
        return Filter(self, lambda x: x < value)

    def __ge__(self, value: Any) -> Filter:
        return Filter(self, lambda x: x >= value)

    def __le__(self, value: Any) -> Filter:
        return Filter(self, lambda x: x <= value)

    def isin(self, values: MutableSequence) -> Filter:
        return Filter(self, lambda x: x in values)

    def notin(self, values: MutableSequence) -> Filter:
        return Filter(self, lambda x: x not in values)

    def drop(self):
        """drop Column from parent"""
        if self.parent is not None:
            self.parent.drop_column(self.name)
            self.parent = None

    def cast_as(self, data_type: Callable) -> None:
        self.data = [data_type(item) for item in self.data]
        if self.parent is not None:
            self.parent.cast_column_as(self.name, data_type)

    def value_counts(self) -> dict:
        return {value: self.data.count(value) for value in self.data}

    def sum(self) -> Union[float, int]:
        return sum(self.data)

    def groupby(self) -> Group:
        name = str(self.name)
        groups = tim.groupby({name: self.data}, by=str(name))
        return Group(groups, by=name)


def itercolumns(data: dt.TableMapping, parent, labels=None) -> Generator[Column, None, None]:
    for col in data.keys():
        yield Column(data[col], col, parent, labels)


def iteritems(data: dt.TableMapping, parent) -> Generator[tuple[str, Column], None, None]:
    for col in data.keys():
        yield col, Column(data[col], col, parent)


def cast_column_as(data: dt.TableMapping, column_name: str, data_type: Callable) -> dt.TableMapping:
    """Return a new dict with named column cast as data_type."""
    new_data = tim.copy_table(data)
    new_data[column_name] = [data_type(value) for value in new_data[column_name]]
    return new_data