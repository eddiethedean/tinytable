from array import array
from numbers import Number
from typing import Iterable

from more_itertools import minmax


def is_array_type(iterable: Iterable, type_code: str):
    try:
        return array(type_code, iterable)
    except (OverflowError, TypeError):
        return False

    
def all_numeric(iterable: Iterable) -> bool:
    return all(isinstance(x, Number) for x in iterable)


def is_float_array(iterable: Iterable, min_max: tuple) -> bool:
    min_num, max_num = min_max
    return (abs(min_num) >= 1.2E-38 and max_num <= 3.4E+38)


def is_double_array(iterable: Iterable, min_max: tuple) -> bool:
    min_num, max_num = min_max
    return (abs(min_num) >= 2.3E-308 and max_num <= 1.7E+308)


def is_string_array(iterable: Iterable):
    return is_array_type(iterable, 'u')


def get_array(iterable: Iterable):
    """find C array type and return array
       If no C type is found, return list
    """
    if len(iterable) == 0:
        print('empty iterable')
        return []
    
    # check for unicode type
    a = is_array_type(iterable, 'u')
    if a: return a
    
    # check if all values are numeric
    if not all_numeric(iterable):
        return list(iterable)
    
    # check for unsigned char type
    a = is_array_type(iterable, 'B')
    # Fits int 0 to 255.
    if a: return a
    
    # check for signed char type
    a = is_array_type(iterable, 'b')
    # Fits int -128 to 128.
    if a: return a
    
    # check for unsigned int type
    # Fits int 0 to 4,294,967,295.
    a = is_array_type(iterable, 'I')
    if a: return a
    
    # check for int type
    # Fits int -2,147,483,648 to 2,147,483,647.
    a = is_array_type(iterable, 'i')
    if a: return a
    
    # check for unsigned short type
    a = is_array_type(iterable, 'H')
    # Fits int 0 to 65,535.
    if a: return a
    
    # check for short type
    a = is_array_type(iterable, 'h')
    # Fits int -32,768 to 32,767.
    if a: return a
    
    # check for unsigned long type
    a = is_array_type(iterable, 'L')
    # Fits int 0 to 18,446,744,073,709,551,615.
    if a: return a
    
    # check for long type
    a = is_array_type(iterable, 'l')
    # Fits int -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807.
    if a: return a
    
    # check for float type
    min_max = minmax(iterable)
    if is_float_array(iterable, min_max):
        return array('f', iterable)
        
    # check for double type
    if is_double_array(iterable, min_max):
        return array('d', iterable)
    
    return list(iterable)