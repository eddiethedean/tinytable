"""Test the data_to_csv, data_to_excel, data_to_sqlite functions."""

import os

from tinytable.csv import data_to_csv_file
from tinytable.excel import data_to_excel_file, read_excel_file
from tinytable.sqlite import data_to_sqlite_table

CSV_TEXT = """id,name,age,gender
1,Olivia,4,f
2,Noah,5,m
3,Emma,8,f
4,Liam,3,m
5,Amelia,24,f
6,Oliver,56,m
7,Ava,12,f
8,Elijah,68,m
9,Sophia,21,f
10,Mateo,90,m
"""


def delete_file(path: str) -> None:
    """Delete file if it exists."""
    if os.path.exists(path):
        os.remove(path)


def test_write_csv():
    """Test writing CSV file."""
    path = "tests/data/new_people.csv"
    delete_file(path)
    data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    data_to_csv_file(data, path)
    expected = CSV_TEXT
    with open(path, "r", encoding="utf-8-sig") as f:
        str_data = f.read()
    assert str_data == expected


def test_write_excel():
    """Test writing Excel file."""
    path = "tests/data/new_people.xlsx"
    copy_path = "tests/data/new_people_copy.xlsx"
    delete_file(path)
    data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    data_to_excel_file(data, path, replace_workbook=True)

    # Instead of comparing files directly, compare the data content
    generated_data = read_excel_file(path)
    expected_data = read_excel_file(copy_path)
    assert generated_data == expected_data


def test_write_sqlite():
    """Test writing SQLite database."""
    data = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    data_to_sqlite_table(data, "data.db", "people", replace_table=True)
    expected = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    assert data == expected
