"""Test Column and Row behavior."""

import pytest

from tinytable.column import Column
from tinytable.filter import Filter
from tinytable.row import Row


class TestColumnBehavior:
    """Test Column class behavior."""

    def test_column_init(self, sample_table):
        """Test Column initialization."""
        col = sample_table["id"]
        assert isinstance(col, Column)
        assert col.name == "id"
        assert col.data == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert col.parent is sample_table

    def test_column_getitem(self, sample_table):
        """Test Column __getitem__."""
        col = sample_table["name"]
        assert col[0] == "Olivia"
        assert col[1] == "Noah"
        assert col[-1] == "Mateo"

    def test_column_getitem_out_of_bounds(self, sample_table):
        """Test Column __getitem__ out of bounds."""
        col = sample_table["name"]
        with pytest.raises(IndexError):
            _ = col[100]

    def test_column_setitem(self, sample_table):
        """Test Column __setitem__."""
        col = sample_table["name"]
        col[0] = "Updated"
        assert col[0] == "Updated"
        assert sample_table.data["name"][0] == "Updated"  # Should update parent

    def test_column_setitem_out_of_bounds(self, sample_table):
        """Test Column __setitem__ out of bounds."""
        col = sample_table["name"]
        with pytest.raises(IndexError):
            col[100] = "Updated"

    def test_column_len(self, sample_table):
        """Test Column __len__."""
        col = sample_table["name"]
        assert len(col) == 10

    def test_column_iter(self, sample_table):
        """Test Column __iter__."""
        col = sample_table["name"]
        names = list(col)
        assert names == ["Olivia", "Noah", "Emma", "Liam", "Amelia", "Oliver", "Ava", "Elijah", "Sophia", "Mateo"]

    def test_column_repr(self, sample_table):
        """Test Column __repr__."""
        col = sample_table["name"]
        repr_str = repr(col)
        assert "name" in repr_str
        assert "Olivia" in repr_str

    @pytest.mark.parametrize(
        "op,value,expected",
        [
            ("==", "Olivia", [True, False, False, False, False, False, False, False, False, False]),
            ("!=", "Olivia", [False, True, True, True, True, True, True, True, True, True]),
            (">", "M", [True, True, False, False, False, True, False, False, True, True]),  # Actual string comparison
            ("<", "M", [False, False, True, True, True, False, True, True, False, False]),  # Actual string comparison
            (">=", "Olivia", [True, False, False, False, False, False, False, False, True, False]),  # Actual string comparison
            ("<=", "Olivia", [True, True, True, True, True, True, True, True, False, True]),  # Actual string comparison
        ],
    )
    def test_column_comparisons(self, sample_table, op, value, expected):
        """Test Column comparison operations."""
        col = sample_table["name"]
        if op == "==":
            result = col == value
        elif op == "!=":
            result = col != value
        elif op == ">":
            result = col > value
        elif op == "<":
            result = col < value
        elif op == ">=":
            result = col >= value
        elif op == "<=":
            result = col <= value

        assert isinstance(result, Filter)
        assert list(result) == expected

    def test_column_isin(self, sample_table):
        """Test Column isin method."""
        col = sample_table["name"]
        result = col.isin(["Olivia", "Emma", "Ava"])
        assert isinstance(result, Filter)
        assert list(result) == [True, False, True, False, False, False, True, False, False, False]

    def test_column_notin(self, sample_table):
        """Test Column notin method."""
        col = sample_table["name"]
        result = col.notin(["Olivia", "Emma", "Ava"])
        assert isinstance(result, Filter)
        assert list(result) == [False, True, False, True, True, True, False, True, True, True]

    def test_column_arithmetic_operations(self, sample_table):
        """Test Column arithmetic operations."""
        col = sample_table["age"]

        # Addition
        result_add = col + 10
        assert isinstance(result_add, Column)
        assert result_add.data == [14, 15, 18, 13, 34, 66, 22, 78, 31, 100]

        # Subtraction
        result_sub = col - 5
        assert isinstance(result_sub, Column)
        assert result_sub.data == [-1, 0, 3, -2, 19, 51, 7, 63, 16, 85]

        # Multiplication
        result_mul = col * 2
        assert isinstance(result_mul, Column)
        assert result_mul.data == [8, 10, 16, 6, 48, 112, 24, 136, 42, 180]

        # Division
        result_div = col / 2
        assert isinstance(result_div, Column)
        assert result_div.data == [2.0, 2.5, 4.0, 1.5, 12.0, 28.0, 6.0, 34.0, 10.5, 45.0]

        # Modulo
        result_mod = col % 3
        assert isinstance(result_mod, Column)
        assert result_mod.data == [1, 2, 2, 0, 0, 2, 0, 2, 0, 0]

        # Floor division
        result_floordiv = col // 3
        assert isinstance(result_floordiv, Column)
        assert result_floordiv.data == [1, 1, 2, 1, 8, 18, 4, 22, 7, 30]

        # Exponentiation
        result_pow = col**2
        assert isinstance(result_pow, Column)
        assert result_pow.data == [16, 25, 64, 9, 576, 3136, 144, 4624, 441, 8100]

    def test_column_value_counts(self, sample_table):
        """Test Column value_counts method."""
        col = sample_table["gender"]
        counts = col.value_counts()
        assert counts == {"f": 5, "m": 5}

    def test_column_sum(self, sample_table):
        """Test Column sum method."""
        col = sample_table["age"]
        total = col.sum()
        assert total == 291  # Actual sum of ages

    def test_column_sum_strings(self, sample_table):
        """Test Column sum with strings (raises TypeError)."""
        col = sample_table["name"]
        # String sum raises TypeError
        with pytest.raises(TypeError):
            col.sum()

    def test_column_cast_as(self, sample_table):
        """Test Column cast_as method."""
        col = sample_table["age"]
        col.cast_as(str)
        assert all(isinstance(x, str) for x in col.data)
        assert col.data[0] == "4"

    def test_column_drop(self, sample_table):
        """Test Column drop method."""
        col = sample_table["name"]
        col.drop()
        assert "name" not in sample_table.data
        assert col.parent is None

    def test_column_drop_no_parent(self):
        """Test Column drop with no parent."""
        col = Column([1, 2, 3], "test")
        col.drop()  # Should not raise
        assert col.parent is None


class TestRowBehavior:
    """Test Row class behavior."""

    def test_row_init(self, sample_table):
        """Test Row initialization."""
        row = sample_table[0]
        assert isinstance(row, Row)
        assert row.index == 0
        assert row.data == {"id": 1, "name": "Olivia", "age": 4, "gender": "f"}
        assert row.parent is sample_table

    def test_row_init_with_labels(self, labeled_table):
        """Test Row initialization with labels."""
        row = labeled_table[0]
        assert row.index == 0
        assert row.label == ("r1",)
        assert row.data == {"id": 1, "name": "Alice", "age": 25}

    def test_row_getitem(self, sample_table):
        """Test Row __getitem__."""
        row = sample_table[0]
        assert row["name"] == "Olivia"
        assert row["age"] == 4

    def test_row_getitem_invalid_key(self, sample_table):
        """Test Row __getitem__ with invalid key."""
        row = sample_table[0]
        with pytest.raises(KeyError):
            _ = row["invalid"]

    def test_row_setitem(self, sample_table):
        """Test Row __setitem__."""
        row = sample_table[0]
        row["name"] = "Updated"
        assert row["name"] == "Updated"
        assert sample_table.data["name"][0] == "Updated"  # Should update parent

    def test_row_setitem_new_key(self, sample_table):
        """Test Row __setitem__ with new key (raises KeyError)."""
        row = sample_table[0]
        # Setting new key raises KeyError
        with pytest.raises(KeyError):
            row["new_field"] = "test"

    def test_row_len(self, sample_table):
        """Test Row __len__."""
        row = sample_table[0]
        assert len(row) == 4  # 4 columns

    def test_row_iter(self, sample_table):
        """Test Row __iter__."""
        row = sample_table[0]
        values = list(row)
        assert values == [1, "Olivia", 4, "f"]

    def test_row_keys(self, sample_table):
        """Test Row keys method."""
        row = sample_table[0]
        keys = row.keys()
        assert keys == ["id", "name", "age", "gender"]

    def test_row_values(self, sample_table):
        """Test Row values method."""
        row = sample_table[0]
        values = row.values()
        assert values == [1, "Olivia", 4, "f"]

    def test_row_repr(self, sample_table):
        """Test Row __repr__."""
        row = sample_table[0]
        repr_str = repr(row)
        assert "Olivia" in repr_str

    def test_row_repr_with_labels(self, labeled_table):
        """Test Row __repr__ with labels."""
        row = labeled_table[0]
        repr_str = repr(row)
        assert "Alice" in repr_str

    def test_row_drop(self, sample_table):
        """Test Row drop method."""
        original_len = len(sample_table)
        row = sample_table[0]
        row.drop()
        assert len(sample_table) == original_len - 1
        assert row.parent is None

    def test_row_drop_no_parent(self):
        """Test Row drop with no parent."""
        row = Row({"id": 1, "name": "Alice"}, 0)
        row.drop()  # Should not raise
        assert row.parent is None

    def test_row_drop_updates_indices(self, sample_table):
        """Test Row drop updates subsequent row indices."""
        row1 = sample_table[0]
        row2 = sample_table[1]
        assert row2.index == 1

        row1.drop()
        # After dropping row 0, the second row becomes row 0
        assert sample_table.data["name"][0] == "Noah"


class TestColumnRowIntegration:
    """Test Column and Row integration with Table."""

    def test_column_parent_linking(self, sample_table):
        """Test Column parent linking."""
        col = sample_table["name"]
        col[0] = "Updated"
        assert sample_table.data["name"][0] == "Updated"

    def test_row_parent_linking(self, sample_table):
        """Test Row parent linking."""
        row = sample_table[0]
        row["name"] = "Updated"
        assert sample_table.data["name"][0] == "Updated"

    def test_column_drop_updates_table(self, sample_table):
        """Test Column drop updates parent table."""
        col = sample_table["name"]
        col.drop()
        assert "name" not in sample_table.data
        assert len(sample_table.columns) == 3

    def test_row_drop_updates_table(self, sample_table):
        """Test Row drop updates parent table."""
        original_len = len(sample_table)
        row = sample_table[0]
        row.drop()
        assert len(sample_table) == original_len - 1

    def test_column_with_labels(self, labeled_table):
        """Test Column with labeled table."""
        col = labeled_table["name"]
        assert col.labels == [("r1",), ("r2",), ("r3",)]

    def test_row_with_labels(self, labeled_table):
        """Test Row with labeled table."""
        row = labeled_table[0]
        assert row.label == ("r1",)

    def test_column_arithmetic_independence(self, sample_table):
        """Test Column arithmetic operations don't affect original."""
        col = sample_table["age"]
        result = col + 10
        assert col.data == [4, 5, 8, 3, 24, 56, 12, 68, 21, 90]  # Original unchanged
        assert result.data == [14, 15, 18, 13, 34, 66, 22, 78, 31, 100]  # New column

    def test_row_independence_after_drop(self, sample_table):
        """Test Row independence after dropping."""
        row = sample_table[0]
        row.drop()
        # Row should still be accessible even after dropping
        assert row.data == {"id": 1, "name": "Olivia", "age": 4, "gender": "f"}
        assert row.parent is None
