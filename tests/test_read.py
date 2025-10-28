"""Test the read_csv, read_excel, read_sqlite functions."""

from tinytable.csv import read_csv_file
from tinytable.excel import read_excel_file
from tinytable.sqlite import read_sqlite_table


def test_read_csv():
    """Test reading CSV file."""
    data = read_csv_file("tests/data/people.csv")
    expected = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    assert data == expected


def test_read_excel():
    """Test reading Excel file."""
    data = read_excel_file("tests/data/people.xlsx", "Sheet1")
    expected = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    assert data == expected


def test_read_sqlite():
    """Test reading SQLite database."""
    data = read_sqlite_table("tests/data/data.db", "people")
    expected = {
        "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
        "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
        "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
    }
    assert data == expected
