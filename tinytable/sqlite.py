import sqlite3
from typing import List, Mapping, MutableMapping, Optional

from tinytable.functional.utils import combine_names_rows
from tinytable.functional.copy import copy_table


def _table_names(conn) -> List[str]:
    cursor = conn.cursor()
    cursor.execute('SELECT name from sqlite_master where type= "table"')
    return [x[0] for x in cursor.fetchall()]


def get_table_names(path: str) -> List[str]:
    with sqlite3.connect(path) as con:
        return _table_names(con)


def _table_column_names(conn, table_name):
    cursor = conn.execute(f'select * from {table_name}')
    return list(map(lambda x: x[0], cursor.description))


def _select_all_rows(conn, table_name):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    return cur.fetchall()


def read_sqlite_table(path: str, table_name: str) -> dict:
    with sqlite3.connect(path) as con:
        column_names = _table_column_names(con, table_name)
        rows = _select_all_rows(con, table_name)
    return combine_names_rows(column_names, rows)


def sqlite_type(column: list) -> str:
    """
    Check what sqlite type column of values can be converted to.
    
    Returns Sqlite type name.
    
    """
    if all(isinstance(x, int) for x in column):
        return 'INTEGER'
    if all(isinstance(x, (int, float)) for x in column):
        return 'REAL'
    if all(isinstance(x, bytes) for x in column):
        return 'BLOB'
    if all(isinstance(x, str) for x in column):
        return 'TEXT'
    else:
        return 'OBJECT'
    

def sqlite_column_types(data: Mapping) -> dict:
    """
    Check what sqlite types each column can be converted to.
    
    Return dict[column_name, sqlite_type_name]
    """
    return {name: sqlite_type(values) for name, values in data.items()}


def data_to_sqlite_table(
    data: MutableMapping,
    path: str,
    table_name: str,
    data_types: Optional[dict] = None) -> None:
    """
    Create Sqlite Table and insert data.
    Error if table_name already exists.
    Guesses sqlite data types for columns if not provided.
    """
    data = copy_table(data)
    if data_types is None:
        data_types = sqlite_column_types(data)

    # Convert any OBJECT data types to str
    for name, type in data_types.items():
        if type == 'OBJECT':
            data[name] = [str(x) for x in data[name]]
        data_types[name] = 'TEXT'

    # Create Sqlite Table with column types

    # Insert data rows

