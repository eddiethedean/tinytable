from typing import Collection, List, Union

import tinytable as tt
from tinytable.functional.group import sum_groups, count_groups


class Group:
    """Returned by Column and Table groupby method.
       Acts like a list of tuple(key, Table)
       Can apply aggregation function to calculate new Table.
    """
    def __init__(self, groups: List[tuple], by: Union[str, Collection]):
        self.groups = groups
        self.by = by

    def __iter__(self):
        return iter(self.groups)

    def __repr__(self):
        return repr(self.groups)

    def __getitem__(self, i: int):
        return self.groups[i]
        
    def sum(self):
        labels, rows = sum_groups(self.groups, self.by)
        return tt.Table(rows, labels)

    def count(self):
        labels, rows = count_groups(self.groups, self.by)
        return tt.Table(rows, labels)

