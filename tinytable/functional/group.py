from collections import namedtuple
from typing import Callable, Collection, Iterable, List, Union
from tinytable.datatypes import RowDict, TableMapping
from tinytable.functional.filter import column_filter, filter_data

from tinytable.utils import uniques


TableFilter = Iterable[bool]


def groupbycolumn(data: TableMapping, column: Collection) -> List[tuple]:
    keys = uniques(column)
    return [(k, filter_data(data, column_filter(column, lambda x: x == k)))
                for k in keys]


def groupbyone(data: TableMapping, column_name: str) -> List[tuple]:
    return groupbycolumn(data, data[column_name])


def row_value_tuples(data: TableMapping, column_names: Collection[str]) -> List[tuple]:
    return list(zip(*[data[col] for col in column_names]))


def groupbymulti(data: TableMapping, column_names: Collection[str]) -> List[tuple]:
    return groupbycolumn(data, row_value_tuples(data, column_names))


def groupby(data: TableMapping, by: Union[str, Collection[str]]) -> List[tuple]:
    if isinstance(by, str):
        return groupbyone(data, by)
    else:
        return groupbymulti(data, by)


def _keys(key, by) -> dict:
    keys = {}
    if isinstance(by, str):
        keys[by] = key
    else:
        for col, k in zip(by, key):
            keys[col] = k
    return keys


def aggregate_groups(groups: List[tuple], by: Collection[str], func: Callable, tuplename: str) -> dict:
    rows = {}
    for key, data in groups:
        row = func(data)
        if len(row):
            Agg = namedtuple(field_names=row.keys(), typename=tuplename)
            GroupbyKey = namedtuple(field_names=by, typename='GroupbyKey')
            keys = _keys(key, by)
            rows[GroupbyKey(*keys.values())] = Agg(*row.values())
    return rows


def sum_groups(groups: List[tuple], by: Collection[str]) -> dict:
    return aggregate_groups(groups, by, sum_data, 'Sums')


def count_groups(groups: List[tuple], by: Collection[str]) -> dict:
    return aggregate_groups(groups, by, count_data, 'Counts')


def aggregate_data(data: TableMapping, func: Callable) -> RowDict:
    out = {}
    for column_name in data.keys():
        try:
            col_sum = func(data[column_name])
        except TypeError:
            continue
        out[column_name] = col_sum
    return out


def sum_data(data: TableMapping) -> RowDict:
    return aggregate_data(data, sum)


def count_data(data: TableMapping) -> RowDict:
    return aggregate_data(data, len)


