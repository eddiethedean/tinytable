import sqlite3
from typing import List

from tinytim.functional.utils import combine_names_rows


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
