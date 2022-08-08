from typing import Iterable, List, Optional


def combine_names_rows(column_names, rows) -> dict[str, List]:
    return dict(zip(column_names, map(list, zip(*rows))))


def uniques(values: Iterable) -> List:
    out = []
    for value in values:
        if value not in out:
            out.append(value)
    return out

# TODO: make slice_to_range work with negative steps
# slice_to_range(slice(None, None, -1), 4) -> range(-1, 4, -1)

def slice_to_range(s: slice, stop: Optional[int] = None) -> range:
    """Convert an int:int:int slice object to a range object.
       Needs stop if s.stop is None since range is not allowed to have stop=None.
    """
    
    step = 1 if s.step is None else s.step
    if step == 0:
        raise ValueError('step must not be zero')

    if step > 0:
        start = 0 if s.start is None else s.start
        stop = s.stop if s.stop is not None else stop
    else:
        start = stop if s.start is None else s.start
        if isinstance(start, int):
            start -= 1
        stop = -1 if s.stop is None else s.stop

        if start is None:
            raise ValueError('start cannot be None is range with negative step')

    if stop is None:
        raise ValueError('stop cannot be None in range')
    
    return range(start, stop, step)