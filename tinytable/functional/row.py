
from typing import Any, Generator

import tinytable.datatypes as dt


def row_values_generator(row: dt.TableMapping) -> Generator[Any, None, None]:
    for key in row:
        yield row[key]