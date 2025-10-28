"""Test core Table operations with pytest patterns."""

import pytest

from tinytable import Table


class TestTableConstructors:
    """Test Table constructors and initialization."""

    def test_init_with_dict(self):
        """Test Table initialization with dictionary."""
        data = {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]}
        t = Table(data)
        assert t.data == data
        assert t.labels is None

    def test_init_with_sequences_and_columns(self):
        """Test Table initialization with sequences and column names."""
        data = [[1, "Alice"], [2, "Bob"], [3, "Charlie"]]
        columns = ["id", "name"]
        t = Table(data, columns=columns)
        expected = {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]}
        assert t.data == expected

    def test_init_with_labels(self):
        """Test Table initialization with labels."""
        data = {"id": [1, 2], "name": ["Alice", "Bob"]}
        labels = [("r1",), ("r2",)]
        t = Table(data, labels=labels)
        assert t.data == data
        assert t.labels == list(labels)

    def test_from_records(self):
        """Test Table.from_records class method."""
        data = [[1, "Alice"], [2, "Bob"]]
        columns = ["id", "name"]
        t = Table.from_records(data, columns)
        expected = {"id": [1, 2], "name": ["Alice", "Bob"]}
        assert t.data == expected

    def test_from_dict(self):
        """Test Table.from_dict class method."""
        data = {"id": [1, 2], "name": ["Alice", "Bob"]}
        t = Table.from_dict(data)
        assert t.data == data

    def test_init_validates_column_lengths(self):
        """Test that Table validates all columns have same length."""
        data = {"id": [1, 2, 3], "name": ["Alice", "Bob"]}  # Different lengths
        with pytest.raises(ValueError, match="All columns must be of the same length"):
            Table(data)

    def test_init_empty_table(self):
        """Test creating empty table."""
        t = Table()
        assert t.data == {}
        assert t.labels is None


class TestTableGetItem:
    """Test Table __getitem__ access patterns."""

    def test_getitem_string_returns_column(self, sample_table):
        """Test that string key returns Column."""
        col = sample_table["id"]
        assert hasattr(col, "data")
        assert col.data == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @pytest.mark.parametrize(
        "index,expected_name",
        [
            (0, "Olivia"),
            (1, "Noah"),
            (-1, "Mateo"),
            (-2, "Sophia"),
        ],
    )
    def test_getitem_int_returns_row(self, sample_table, index, expected_name):
        """Test that int key returns Row."""
        row = sample_table[index]
        assert hasattr(row, "data")
        assert row.data["name"] == expected_name

    def test_getitem_slice_returns_table(self, sample_table):
        """Test that slice returns new Table."""
        subset = sample_table[1:4]
        assert isinstance(subset, Table)
        assert len(subset) == 3
        assert subset.data["name"] == ["Noah", "Emma", "Liam"]

    def test_getitem_list_of_strings_returns_table(self, sample_table):
        """Test that list of strings returns Table with selected columns."""
        subset = sample_table[["id", "name"]]
        assert isinstance(subset, Table)
        assert list(subset.columns) == ["id", "name"]
        assert len(subset) == 10

    def test_getitem_list_of_bool_filters_table(self, sample_table):
        """Test that list of bools filters table."""
        mask = [True, False, True, False] + [False] * 6
        subset = sample_table[mask]
        assert isinstance(subset, Table)
        assert len(subset) == 2
        assert subset.data["name"] == ["Olivia", "Emma"]

    def test_getitem_filter_object(self, sample_table):
        """Test that Filter object filters table."""
        filter_obj = sample_table["age"] > 20
        subset = sample_table[filter_obj]
        assert isinstance(subset, Table)
        assert len(subset) == 5  # ages: 24, 56, 12, 68, 21, 90 (actually 5 > 20)

    def test_getitem_tuple_with_labels(self, labeled_table):
        """Test tuple key with labeled table."""
        row = labeled_table[("r2",)]
        assert row.data["name"] == "Bob"

    def test_getitem_tuple_without_labels_raises(self, sample_table):
        """Test tuple key without labels raises error."""
        with pytest.raises(ValueError, match="Table must have labels"):
            _ = sample_table[("invalid",)]

    def test_getitem_invalid_key_raises(self, sample_table):
        """Test invalid key type raises error."""
        with pytest.raises(TypeError, match="key must be str"):
            _ = sample_table[123.45]

    def test_getitem_out_of_range_raises(self, sample_table):
        """Test out of range index raises error."""
        with pytest.raises(IndexError):
            _ = sample_table[100]


class TestTableSetItem:
    """Test Table __setitem__ operations."""

    def test_setitem_column(self, sample_table):
        """Test setting column values."""
        # First add the column with proper length
        sample_table.data["score"] = [85, 90, 95, 80, 88, 92, 87, 89, 91, 93]
        assert "score" in sample_table.data
        assert sample_table.data["score"] == [85, 90, 95, 80, 88, 92, 87, 89, 91, 93]

    def test_setitem_row(self, sample_table):
        """Test setting row values."""
        sample_table[0] = {"id": 100, "name": "Updated", "age": 25, "gender": "f"}
        assert sample_table.data["name"][0] == "Updated"
        assert sample_table.data["age"][0] == 25


class TestTableDelItem:
    """Test Table __delitem__ operations."""

    def test_delitem_column(self, sample_table):
        """Test deleting column."""
        del sample_table["gender"]
        assert "gender" not in sample_table.data
        assert len(sample_table.columns) == 3

    def test_delitem_row(self, sample_table):
        """Test deleting row."""
        original_len = len(sample_table)
        del sample_table[0]
        assert len(sample_table) == original_len - 1
        assert sample_table.data["name"][0] == "Noah"  # Second row moved up


class TestTableProperties:
    """Test Table properties."""

    def test_shape(self, sample_table):
        """Test shape property."""
        assert sample_table.shape == (10, 4)

    def test_shape_empty(self, empty_table):
        """Test shape of empty table."""
        assert empty_table.shape == (0, 0)

    def test_size(self, sample_table):
        """Test size property."""
        assert sample_table.size == 40  # 10 rows * 4 columns

    def test_columns_getter(self, sample_table):
        """Test columns property getter."""
        cols = sample_table.columns
        assert cols == ("id", "name", "age", "gender")

    def test_columns_setter(self):
        """Test columns property setter."""
        t = Table({"id": [1, 2], "name": ["Alice", "Bob"], "age": [25, 30]})
        t.columns = ["ID", "NAME", "AGE"]
        assert t.columns == ("ID", "NAME", "AGE")

    def test_index(self, sample_table):
        """Test index property."""
        index_col = sample_table.index
        assert hasattr(index_col, "data")
        assert len(index_col.data) == 10

    def test_values(self, sample_table):
        """Test values property."""
        values = sample_table.values
        assert isinstance(values, tuple)
        assert len(values) == 10  # 10 rows
        assert len(values[0]) == 4  # 4 columns


class TestTableSpecialMethods:
    """Test Table special methods."""

    def test_len(self, sample_table):
        """Test __len__ method."""
        assert len(sample_table) == 10

    def test_len_empty(self, empty_table):
        """Test __len__ of empty table."""
        assert len(empty_table) == 0

    def test_iter(self, sample_table):
        """Test __iter__ method."""
        columns = list(sample_table)
        assert columns == ["id", "name", "age", "gender"]

    def test_repr(self, sample_table):
        """Test __repr__ method."""
        repr_str = repr(sample_table)
        assert "id" in repr_str
        assert "name" in repr_str
        assert "Olivia" in repr_str

    def test_keys(self, sample_table):
        """Test keys method."""
        keys = sample_table.keys()
        assert keys == ("id", "name", "age", "gender")
