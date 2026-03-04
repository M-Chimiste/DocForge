"""Tests for data transforms: rename, filter, sort, format, computed, pipeline."""

from __future__ import annotations

import pandas as pd

from transforms.base import TransformPipeline
from transforms.computed import ComputedTransform
from transforms.filter import FilterTransform
from transforms.format import DateFormatTransform, NumberFormatTransform
from transforms.pipeline import create_default_transform_registry
from transforms.rename import RenameTransform
from transforms.sort import SortTransform

# ---------------------------------------------------------------------------
# Shared test data builders
# ---------------------------------------------------------------------------


def _sample_df() -> pd.DataFrame:
    """A simple DataFrame used across multiple test classes."""
    return pd.DataFrame(
        {
            "Name": ["Alice", "Bob", "Carol", "Dave"],
            "Score": [85, 92, 78, 95],
            "Department": ["Eng", "Sales", "Eng", "HR"],
        }
    )


def _numeric_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "A": [10, 20, 30],
            "B": [5, 15, 25],
            "C": [1, 2, 3],
        }
    )


def _date_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event": ["Launch", "Review"],
            "date": ["2026-01-15", "2026-06-30"],
        }
    )


# ---------------------------------------------------------------------------
# TestRenameTransform
# ---------------------------------------------------------------------------


class TestRenameTransform:
    def setup_method(self):
        self.transform = RenameTransform()

    def test_can_handle(self):
        assert self.transform.can_handle("rename") is True
        assert self.transform.can_handle("filter") is False

    def test_single_rename(self):
        df = _sample_df()
        result = self.transform.apply(df, {"columns": {"Name": "FullName"}})
        assert "FullName" in result.columns
        assert "Name" not in result.columns
        assert result["FullName"].iloc[0] == "Alice"

    def test_multiple_renames(self):
        df = _sample_df()
        result = self.transform.apply(df, {"columns": {"Name": "Employee", "Score": "Points"}})
        assert "Employee" in result.columns
        assert "Points" in result.columns
        assert "Name" not in result.columns
        assert "Score" not in result.columns

    def test_rename_nonexistent_column_is_noop(self):
        df = _sample_df()
        result = self.transform.apply(df, {"columns": {"NonExistent": "New"}})
        assert list(result.columns) == list(df.columns)
        assert result.equals(df)


# ---------------------------------------------------------------------------
# TestFilterTransform
# ---------------------------------------------------------------------------


class TestFilterTransform:
    def setup_method(self):
        self.transform = FilterTransform()

    def test_can_handle(self):
        assert self.transform.can_handle("filter") is True
        assert self.transform.can_handle("sort") is False

    def test_equals(self):
        df = _sample_df()
        result = self.transform.apply(
            df, {"column": "Department", "operator": "equals", "value": "Eng"}
        )
        assert len(result) == 2
        assert list(result["Name"]) == ["Alice", "Carol"]

    def test_not_equals(self):
        df = _sample_df()
        result = self.transform.apply(
            df, {"column": "Department", "operator": "not_equals", "value": "Eng"}
        )
        assert len(result) == 2
        assert list(result["Name"]) == ["Bob", "Dave"]

    def test_contains(self):
        df = _sample_df()
        result = self.transform.apply(df, {"column": "Name", "operator": "contains", "value": "ob"})
        assert len(result) == 1
        assert result["Name"].iloc[0] == "Bob"

    def test_gt(self):
        df = _sample_df()
        result = self.transform.apply(df, {"column": "Score", "operator": "gt", "value": 90})
        assert len(result) == 2
        assert set(result["Name"]) == {"Bob", "Dave"}

    def test_lt(self):
        df = _sample_df()
        result = self.transform.apply(df, {"column": "Score", "operator": "lt", "value": 80})
        assert len(result) == 1
        assert result["Name"].iloc[0] == "Carol"

    def test_filter_on_missing_column_is_noop(self):
        df = _sample_df()
        result = self.transform.apply(
            df, {"column": "NonExistent", "operator": "equals", "value": "x"}
        )
        assert len(result) == len(df)
        assert result.equals(df)


# ---------------------------------------------------------------------------
# TestSortTransform
# ---------------------------------------------------------------------------


class TestSortTransform:
    def setup_method(self):
        self.transform = SortTransform()

    def test_can_handle(self):
        assert self.transform.can_handle("sort") is True
        assert self.transform.can_handle("rename") is False

    def test_single_ascending(self):
        df = _sample_df()
        result = self.transform.apply(df, {"columns": ["Score"], "ascending": True})
        assert list(result["Score"]) == [78, 85, 92, 95]

    def test_single_descending(self):
        df = _sample_df()
        result = self.transform.apply(df, {"columns": ["Score"], "ascending": False})
        assert list(result["Score"]) == [95, 92, 85, 78]

    def test_multi_column_sort(self):
        df = pd.DataFrame(
            {
                "Dept": ["Eng", "Sales", "Eng", "Sales"],
                "Score": [80, 70, 90, 60],
            }
        )
        result = self.transform.apply(
            df, {"columns": ["Dept", "Score"], "ascending": [True, False]}
        )
        assert list(result["Dept"]) == ["Eng", "Eng", "Sales", "Sales"]
        assert list(result["Score"]) == [90, 80, 70, 60]

    def test_missing_column_is_noop(self):
        df = _sample_df()
        original = df.copy()
        result = self.transform.apply(df, {"columns": ["NonExistent"], "ascending": True})
        assert result.equals(original)


# ---------------------------------------------------------------------------
# TestDateFormatTransform
# ---------------------------------------------------------------------------


class TestDateFormatTransform:
    def setup_method(self):
        self.transform = DateFormatTransform()

    def test_can_handle(self):
        assert self.transform.can_handle("format_date") is True
        assert self.transform.can_handle("format_number") is False

    def test_standard_format(self):
        df = _date_df()
        result = self.transform.apply(df, {"column": "date", "format": "%m/%d/%Y"})
        assert result["date"].iloc[0] == "01/15/2026"
        assert result["date"].iloc[1] == "06/30/2026"

    def test_custom_format(self):
        df = _date_df()
        result = self.transform.apply(df, {"column": "date", "format": "%d %b %Y"})
        assert result["date"].iloc[0] == "15 Jan 2026"

    def test_missing_column_is_noop(self):
        df = _date_df()
        result = self.transform.apply(df, {"column": "missing_col", "format": "%Y"})
        assert result.equals(df)


# ---------------------------------------------------------------------------
# TestNumberFormatTransform
# ---------------------------------------------------------------------------


class TestNumberFormatTransform:
    def setup_method(self):
        self.transform = NumberFormatTransform()

    def test_can_handle(self):
        assert self.transform.can_handle("format_number") is True
        assert self.transform.can_handle("format_date") is False

    def test_decimal(self):
        df = pd.DataFrame({"value": [3.14159, 2.71828]})
        result = self.transform.apply(df, {"column": "value", "style": "decimal", "decimals": 2})
        assert result["value"].iloc[0] == "3.14"
        assert result["value"].iloc[1] == "2.72"

    def test_currency(self):
        df = pd.DataFrame({"price": [1234.5, 9999.99]})
        result = self.transform.apply(
            df, {"column": "price", "style": "currency", "decimals": 2, "prefix": "$"}
        )
        assert result["price"].iloc[0] == "$1,234.50"
        assert result["price"].iloc[1] == "$9,999.99"

    def test_percentage(self):
        df = pd.DataFrame({"rate": [0.05, 0.123]})
        result = self.transform.apply(df, {"column": "rate", "style": "percentage", "decimals": 1})
        assert result["rate"].iloc[0] == "5.0%"
        assert result["rate"].iloc[1] == "12.3%"

    def test_missing_column_is_noop(self):
        df = pd.DataFrame({"x": [1, 2]})
        result = self.transform.apply(df, {"column": "missing", "style": "decimal"})
        assert result.equals(df)


# ---------------------------------------------------------------------------
# TestComputedTransform
# ---------------------------------------------------------------------------


class TestComputedTransform:
    def setup_method(self):
        self.transform = ComputedTransform()

    def test_can_handle(self):
        assert self.transform.can_handle("computed") is True
        assert self.transform.can_handle("filter") is False

    def test_row_total(self):
        df = _numeric_df()
        result = self.transform.apply(
            df,
            {
                "operation": "row_total",
                "columns": ["A", "B", "C"],
                "output_column": "total",
            },
        )
        assert "total" in result.columns
        assert list(result["total"]) == [16, 37, 58]

    def test_agg_sum(self):
        df = _numeric_df()
        result = self.transform.apply(
            df,
            {
                "operation": "agg_sum",
                "column": "A",
                "output_column": "sum_a",
            },
        )
        assert "sum_a" in result.columns
        # Every row gets the aggregate value
        assert result["sum_a"].iloc[0] == 60
        assert result["sum_a"].iloc[2] == 60

    def test_agg_mean(self):
        df = _numeric_df()
        result = self.transform.apply(
            df,
            {
                "operation": "agg_mean",
                "column": "A",
                "output_column": "mean_a",
            },
        )
        assert "mean_a" in result.columns
        assert result["mean_a"].iloc[0] == 20.0

    def test_agg_count(self):
        df = _sample_df()
        result = self.transform.apply(
            df,
            {
                "operation": "agg_count",
                "output_column": "row_count",
            },
        )
        assert "row_count" in result.columns
        assert result["row_count"].iloc[0] == 4

    def test_row_total_ignores_missing_columns(self):
        df = _numeric_df()
        result = self.transform.apply(
            df,
            {
                "operation": "row_total",
                "columns": ["A", "NonExistent"],
                "output_column": "partial_total",
            },
        )
        assert "partial_total" in result.columns
        assert list(result["partial_total"]) == [10, 20, 30]


# ---------------------------------------------------------------------------
# TestTransformPipeline
# ---------------------------------------------------------------------------


class TestTransformPipeline:
    def setup_method(self):
        self.registry = create_default_transform_registry()
        self.pipeline = TransformPipeline(self.registry)

    def test_chain_filter_and_sort(self):
        df = _sample_df()
        transforms = [
            {"type": "filter", "params": {"column": "Score", "operator": "gt", "value": 80}},
            {"type": "sort", "params": {"columns": ["Score"], "ascending": False}},
        ]
        result = self.pipeline.apply(df, transforms)
        assert len(result) == 3  # Alice(85), Bob(92), Dave(95)
        assert list(result["Score"]) == [95, 92, 85]

    def test_empty_pipeline_is_noop(self):
        df = _sample_df()
        result = self.pipeline.apply(df, [])
        assert result.equals(df)

    def test_rename_then_filter(self):
        df = _sample_df()
        transforms = [
            {"type": "rename", "params": {"columns": {"Score": "Points"}}},
            {"type": "filter", "params": {"column": "Points", "operator": "gte", "value": 90}},
        ]
        result = self.pipeline.apply(df, transforms)
        assert "Points" in result.columns
        assert "Score" not in result.columns
        assert len(result) == 2

    def test_pipeline_preserves_original(self):
        df = _sample_df()
        original = df.copy()
        self.pipeline.apply(
            df,
            [{"type": "filter", "params": {"column": "Score", "operator": "gt", "value": 90}}],
        )
        assert df.equals(original)
