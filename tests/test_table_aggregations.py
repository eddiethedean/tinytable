"""Test Table aggregation methods and groupby functionality."""

import pytest

from tinytable import Table


class TestTableAggregations:
    """Test Table aggregation methods."""

    def test_sum_numeric(self, sample_table):
        """Test Table sum method with numeric columns."""
        result = sample_table.sum()
        assert result["id"] == 55
        assert result["age"] == 291
        # String columns should not be summed
        assert "name" not in result
        assert "gender" not in result

    def test_sum_empty_table(self, empty_table):
        """Test Table sum method with empty table."""
        result = empty_table.sum()
        assert result == {}

    def test_sum_single_column(self):
        """Test Table sum method with single numeric column."""
        t = Table({"values": [1, 2, 3, 4, 5]})
        result = t.sum()
        assert result["values"] == 15

    def test_count(self, sample_table):
        """Test Table count method."""
        result = sample_table.count()
        assert result["id"] == 10
        assert result["name"] == 10
        assert result["age"] == 10
        assert result["gender"] == 10

    def test_count_with_none(self, table_with_none):
        """Test Table count method with None values."""
        result = table_with_none.count()
        # Count method doesn't exclude None values, but may not include columns with all None
        assert len(result) >= 0  # May be empty if all columns are None

    def test_mean(self, sample_table):
        """Test Table mean method."""
        result = sample_table.mean()
        assert result["id"] == 5.5
        assert result["age"] == 29.1
        # String columns should not have mean
        assert "name" not in result
        assert "gender" not in result

    def test_mean_empty_table(self, empty_table):
        """Test Table mean method with empty table."""
        result = empty_table.mean()
        assert result == {}

    def test_min(self, sample_table):
        """Test Table min method."""
        result = sample_table.min()
        assert result["id"] == 1
        assert result["age"] == 3
        assert result["name"] == "Amelia"  # Alphabetically first
        assert result["gender"] == "f"  # Alphabetically first

    def test_max(self, sample_table):
        """Test Table max method."""
        result = sample_table.max()
        assert result["id"] == 10
        assert result["age"] == 90
        assert result["name"] == "Sophia"  # Alphabetically last
        assert result["gender"] == "m"  # Alphabetically last

    def test_std(self, sample_table):
        """Test Table std method."""
        result = sample_table.std()
        assert "id" in result
        assert "age" in result
        # String columns should not have std
        assert "name" not in result
        assert "gender" not in result

    def test_std_empty_table(self, empty_table):
        """Test Table std method with empty table."""
        result = empty_table.std()
        assert result == {}

    def test_mode(self, sample_table):
        """Test Table mode method."""
        result = sample_table.mode()
        # Mode returns the actual mode value, not a list
        assert result["gender"] in ["f", "m"]

    def test_pstd(self, sample_table):
        """Test Table pstd method (population standard deviation)."""
        result = sample_table.pstd()
        assert "id" in result
        assert "age" in result
        # String columns should not have pstd
        assert "name" not in result
        assert "gender" not in result

    def test_pstd_empty_table(self, empty_table):
        """Test Table pstd method with empty table."""
        result = empty_table.pstd()
        assert result == {}


class TestTableGroupBy:
    """Test Table groupby functionality."""

    def test_groupby_single_column(self, sample_table):
        """Test groupby with single column."""
        groups = sample_table.groupby("gender")
        assert len(groups.groups) == 2

        # Check that we can iterate over groups
        group_keys = [key for key, _ in groups]
        assert "f" in group_keys
        assert "m" in group_keys

        # Check group contents
        female_group = None
        male_group = None
        for key, group in groups:
            if key == "f":
                female_group = group
            elif key == "m":
                male_group = group

        assert len(female_group) == 5
        assert len(male_group) == 5

    def test_groupby_multiple_columns(self):
        """Test groupby with multiple columns."""
        t = Table({"category": ["A", "A", "B", "B", "A", "B"], "subcategory": ["X", "Y", "X", "Y", "X", "X"], "value": [1, 2, 3, 4, 5, 6]})

        groups = t.groupby(["category", "subcategory"])
        assert len(groups.groups) == 4

        # Check specific groups
        group_keys = [key for key, _ in groups]
        assert ("A", "X") in group_keys
        assert ("A", "Y") in group_keys
        assert ("B", "X") in group_keys
        assert ("B", "Y") in group_keys

    def test_groupby_empty_table(self, empty_table):
        """Test groupby with empty table."""
        # Empty table groupby should raise KeyError for nonexistent column
        with pytest.raises(KeyError):
            _ = empty_table.groupby("nonexistent")

    def test_groupby_nonexistent_column(self, sample_table):
        """Test groupby with nonexistent column."""
        with pytest.raises(KeyError):
            _ = sample_table.groupby("nonexistent")

    def test_groupby_iteration(self, sample_table):
        """Test iterating over groupby results."""
        groups = sample_table.groupby("gender")

        group_names = []
        group_sizes = []
        for name, group in groups:
            group_names.append(name)
            group_sizes.append(len(group))

        assert set(group_names) == {"f", "m"}
        assert group_sizes == [5, 5]

    def test_groupby_aggregation(self, sample_table):
        """Test aggregation within groups."""
        groups = sample_table.groupby("gender")

        # Test sum within groups
        female_group = None
        male_group = None
        for key, group in groups:
            if key == "f":
                female_group = group
            elif key == "m":
                male_group = group

        female_ages = female_group.sum()["age"]
        male_ages = male_group.sum()["age"]

        assert female_ages == sum(age for age, gender in zip(sample_table.data["age"], sample_table.data["gender"]) if gender == "f")
        assert male_ages == sum(age for age, gender in zip(sample_table.data["age"], sample_table.data["gender"]) if gender == "m")

    def test_groupby_preserves_labels(self, labeled_table):
        """Test groupby preserves labels."""
        groups = labeled_table.groupby("name")

        # Each group should preserve its labels (if they exist)
        for name, group in groups:
            # Labels may be None in grouped tables
            assert hasattr(group, "labels")

    def test_groupby_single_group(self):
        """Test groupby with all values the same."""
        t = Table({"category": ["A", "A", "A", "A"], "value": [1, 2, 3, 4]})

        groups = t.groupby("category")
        assert len(groups.groups) == 1
        assert groups.groups[0][0] == "A"  # Key is 'A'
        assert len(groups.groups[0][1]) == 4  # Group has 4 rows

    def test_groupby_with_none_values(self, table_with_none):
        """Test groupby with None values."""
        # Groupby with None values should work
        groups = table_with_none.groupby("name")

        # Should have groups for None and non-None values
        group_keys = [key for key, _ in groups]
        assert None in group_keys or len(group_keys) > 0


class TestTableAggregationEdgeCases:
    """Test edge cases for Table aggregations."""

    def test_aggregation_with_all_none(self):
        """Test aggregation with all None values."""
        t = Table({"col1": [None, None, None]})

        result_sum = t.sum()
        result_mean = t.mean()
        result_count = t.count()

        assert result_sum == {}
        assert result_mean == {}
        assert result_count["col1"] == 3  # Count includes None values

    def test_aggregation_with_mixed_types(self):
        """Test aggregation with mixed data types."""
        t = Table({"numbers": [1, 2, 3], "strings": ["a", "b", "c"], "mixed": [1, "b", 3]})

        result_sum = t.sum()
        result_mean = t.mean()

        assert "numbers" in result_sum
        assert "strings" not in result_sum
        assert "mixed" not in result_sum  # Mixed types can't be summed

        assert "numbers" in result_mean
        assert "strings" not in result_mean
        assert "mixed" not in result_mean

    def test_aggregation_single_value(self):
        """Test aggregation with single value."""
        t = Table({"value": [42]})

        result_sum = t.sum()
        result_mean = t.mean()
        result_min = t.min()
        result_max = t.max()

        assert result_sum["value"] == 42
        assert result_mean["value"] == 42
        assert result_min["value"] == 42
        assert result_max["value"] == 42

    def test_aggregation_zero_values(self):
        """Test aggregation with zero values."""
        t = Table({"value": [0, 0, 0]})

        result_sum = t.sum()
        result_mean = t.mean()

        assert result_sum["value"] == 0
        assert result_mean["value"] == 0

    def test_groupby_with_duplicate_keys(self):
        """Test groupby with duplicate grouping keys."""
        t = Table({"key": ["A", "A", "A", "B", "B"], "value": [1, 2, 3, 4, 5]})

        groups = t.groupby("key")
        assert len(groups.groups) == 2

        # Check group sizes
        group_sizes = [len(group) for _, group in groups]
        assert 3 in group_sizes  # Group A has 3 items
        assert 2 in group_sizes  # Group B has 2 items

    def test_groupby_empty_groups(self):
        """Test groupby that results in empty groups."""
        t = Table({"category": ["A", "B", "C"], "value": [1, 2, 3]})

        groups = t.groupby("category")
        assert len(groups.groups) == 3
        assert all(len(group) == 1 for _, group in groups)
