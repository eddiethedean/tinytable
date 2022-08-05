from typing import List


def combine_names_rows(column_names, rows) -> dict[str, List]:
    return dict(zip(column_names, map(list, zip(*rows))))