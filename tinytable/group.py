from typing import Collection, List, Union

import tinytable as tt
from tinytable.functional.group import sum_groups, count_groups, mean_groups
from tinytable.functional.group import mode_groups, min_groups, max_groups
from tinytable.functional.group import stdev_groups, pstdev_groups, nunique_groups


class Group:
    """Returned by Column and Table groupby method.
       Acts like a list of tuple(key, Table)
       Can apply aggregation function to calculate new Table.
    """
    def __init__(self, groups: List[tuple], by: Union[str, Collection]):
        self.groups = groups
        self.by = [by] if isinstance(by, str) else by

    def __iter__(self):
        return iter(self.groups)

    def __repr__(self):
        return repr(self.groups)

    def __getitem__(self, i: int):
        return self.groups[i]
        
    def sum(self):
        labels, rows = sum_groups(self.groups)
        return tt.Table(rows, labels)

    def count(self):
        labels, rows = count_groups(self.groups)
        return tt.Table(rows, labels)

    def mean(self):
        labels, rows = mean_groups(self.groups)
        return tt.Table(rows, labels)

    def min(self):
        labels, rows = min_groups(self.groups)
        return tt.Table(rows, labels)

    def max(self):
        labels, rows = max_groups(self.groups)
        return tt.Table(rows, labels)

    def mode(self):
        labels, rows = mode_groups(self.groups)
        return tt.Table(rows, labels)

    def std(self):
        labels, rows = stdev_groups(self.groups)
        return tt.Table(rows, labels)

    def pstd(self):
        labels, rows = pstdev_groups(self.groups)
        return tt.Table(rows, labels)

    def nunique(self):
        labels, rows = nunique_groups(self.groups)
        return tt.Table(rows, labels)



