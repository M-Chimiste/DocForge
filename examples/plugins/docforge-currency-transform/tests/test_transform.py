"""Tests for the CurrencyConvertTransform plugin."""

from __future__ import annotations

import pandas as pd
import pytest

from docforge_currency_transform.transform import CurrencyConvertTransform


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "product": ["Widget", "Gadget", "Doohickey"],
        "price_usd": [10.0, 25.0, 5.50],
    })


class TestCanHandle:
    def test_matches_currency_convert(self):
        t = CurrencyConvertTransform()
        assert t.can_handle("currency_convert")

    def test_rejects_other_types(self):
        t = CurrencyConvertTransform()
        assert not t.can_handle("rename")
        assert not t.can_handle("filter")
        assert not t.can_handle("sort")


class TestApply:
    def test_basic_conversion(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        result = t.apply(sample_df, {"column": "price_usd", "rate": 0.92})

        assert "price_usd" in result.columns
        assert result.iloc[0]["price_usd"] == pytest.approx(9.2)
        assert result.iloc[1]["price_usd"] == pytest.approx(23.0)
        assert result.iloc[2]["price_usd"] == pytest.approx(5.06)

    def test_with_target_suffix(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        result = t.apply(
            sample_df, {"column": "price_usd", "rate": 0.92, "target_suffix": "_eur"}
        )

        assert "price_usd_eur" in result.columns
        assert "price_usd" not in result.columns
        assert result.iloc[0]["price_usd_eur"] == pytest.approx(9.2)

    def test_original_not_modified(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        original_value = sample_df.iloc[0]["price_usd"]
        t.apply(sample_df, {"column": "price_usd", "rate": 2.0})

        assert sample_df.iloc[0]["price_usd"] == original_value

    def test_missing_column_raises(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        with pytest.raises(ValueError, match="not found"):
            t.apply(sample_df, {"column": "nonexistent", "rate": 1.0})

    def test_missing_rate_raises(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        with pytest.raises(ValueError, match="'rate'"):
            t.apply(sample_df, {"column": "price_usd"})

    def test_missing_column_param_raises(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        with pytest.raises(ValueError, match="'column'"):
            t.apply(sample_df, {"rate": 1.0})

    def test_non_numeric_coerced(self):
        df = pd.DataFrame({"amount": ["10", "abc", "30"]})
        t = CurrencyConvertTransform()
        result = t.apply(df, {"column": "amount", "rate": 2.0})

        assert result.iloc[0]["amount"] == pytest.approx(20.0)
        assert pd.isna(result.iloc[1]["amount"])
        assert result.iloc[2]["amount"] == pytest.approx(60.0)

    def test_rate_of_one(self, sample_df: pd.DataFrame):
        t = CurrencyConvertTransform()
        result = t.apply(sample_df, {"column": "price_usd", "rate": 1.0})

        assert result.iloc[0]["price_usd"] == pytest.approx(10.0)
