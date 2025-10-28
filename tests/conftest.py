"""Shared pytest fixtures for tinytable tests."""

import pytest

from tinytable import Table


@pytest.fixture
def sample_table():
    """Basic 10-row people table for testing."""
    return Table(
        {
            "id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "name": ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"],
            "age": [4, 5, 8, 3, 24, 56, 12, 68, 21, 90],
            "gender": ["f", "m", "f", "m", "f", "m", "f", "m", "f", "m"],
        }
    )


@pytest.fixture
def empty_table():
    """Empty Table for testing edge cases."""
    return Table()


@pytest.fixture
def labeled_table():
    """Table with row labels for testing labeled operations."""
    return Table({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}, labels=[("r1",), ("r2",), ("r3",)])


@pytest.fixture
def small_table():
    """Small 3-row table for basic testing."""
    return Table({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]})


@pytest.fixture
def temp_csv_path(tmp_path):
    """Temporary CSV file path."""
    return tmp_path / "test.csv"


@pytest.fixture
def temp_xlsx_path(tmp_path):
    """Temporary Excel file path."""
    return tmp_path / "test.xlsx"


@pytest.fixture
def temp_db_path(tmp_path):
    """Temporary SQLite database path."""
    return tmp_path / "test.db"


@pytest.fixture
def table_with_none():
    """Table with None values for NA testing."""
    return Table(
        {"id": [1, 2, 3, 4], "name": ["Alice", None, "Charlie", "David"], "age": [25, None, 35, 40], "score": [85.5, 92.0, None, 78.5]}
    )
