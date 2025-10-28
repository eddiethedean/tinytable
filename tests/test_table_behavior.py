"""Test table behavior and bugfixes."""

import pytest

from tinytable.table import Table


def test_init_default_dict_not_shared():
    """Test that default dict is not shared between instances."""
    a = Table()
    b = Table()
    a.data["x"] = [1]
    assert "x" not in b.data


def test_label_tail_uses_n():
    """Test that label_tail respects the n parameter."""
    t = Table({"a": [1, 2, 3, 4]}, labels=["w", "x", "y", "z"])
    assert t.label_tail(2) == ["y", "z"]


def test_filter_by_indexes_pure():
    """Test that filter_by_indexes doesn't mutate original table."""
    t = Table({"a": [1, 2, 3, 4]}, labels=["w", "x", "y", "z"])
    t2 = t.filter_by_indexes([1, 3])
    assert t.labels == ["w", "x", "y", "z"]  # original unchanged
    assert t2.labels == ["x", "z"]  # new table has filtered labels


def test_drop_row_without_labels():
    """Test that drop_row works when labels is None."""
    t = Table({"a": [1, 2, 3]})
    # should not raise
    t.drop_row(1, inplace=True)
    assert t.data["a"] == [1, 3]


def test_edit_column_preserves_labels_when_not_inplace():
    """Test that edit_column preserves labels when inplace=False."""
    t = Table({"a": [1, 2]}, labels=["r1", "r2"])
    t2 = t.edit_column("a", [10, 20], inplace=False)
    assert t2.labels == ["r1", "r2"]  # labels preserved


def test_join_invalid_how_message():
    """Test that join error message mentions 'full' not 'outer'."""
    t = Table({"id": [1], "v": [2]})
    with pytest.raises(ValueError, match='"full"'):
        t.join({"id": [1], "w": [3]}, left_on="id", how="bad")  # type: ignore[arg-type]
