"""Tests for data_inspect.py — column classification, profiling, features, and recommendations."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data_inspect import (
    classify_column,
    column_stats,
    extract_data_features,
    load_data,
    profile_dataframe,
    recommend_charts,
)


# ---------------------------------------------------------------------------
# classify_column
# ---------------------------------------------------------------------------

class TestClassifyColumn:
    def test_numeric_int(self) -> None:
        assert classify_column(pd.Series(range(100))) == "numeric"

    def test_numeric_float(self) -> None:
        assert classify_column(pd.Series([1.1, 2.2, 3.3, 4.4, 5.5] * 10)) == "numeric"

    def test_numeric_low_unique_becomes_categorical(self) -> None:
        assert classify_column(pd.Series([1, 2, 3] * 100)) == "categorical"

    def test_categorical_string(self) -> None:
        assert classify_column(pd.Series(["a", "b", "c", "d", "e"] * 5)) == "categorical"

    def test_datetime_dtype(self) -> None:
        s = pd.to_datetime(pd.Series(["2024-01-01", "2024-01-02", "2024-01-03"]))
        assert classify_column(s) == "datetime"

    def test_datetime_string_parseable(self) -> None:
        dates = [f"2024-01-{d:02d}" for d in range(1, 25)]
        assert classify_column(pd.Series(dates)) == "datetime"

    def test_text_long_strings(self) -> None:
        assert classify_column(pd.Series(["x" * 100, "y" * 80, "z" * 120])) == "text"

    def test_empty_series(self) -> None:
        assert classify_column(pd.Series(dtype="object")) == "unknown"

    def test_all_null(self) -> None:
        assert classify_column(pd.Series([None, None, None])) == "unknown"

    def test_boolean_is_categorical(self) -> None:
        assert classify_column(pd.Series([True, False, True, False])) == "categorical"


# ---------------------------------------------------------------------------
# column_stats
# ---------------------------------------------------------------------------

class TestColumnStats:
    def test_numeric_stats(self) -> None:
        stats = column_stats(pd.Series([10, 20, 30, 40, 50]), "numeric")
        assert stats["count"] == 5
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0
        assert stats["mean"] == 30.0

    def test_categorical_stats(self) -> None:
        stats = column_stats(pd.Series(["a", "b", "a", "c", "b", "a"]), "categorical")
        assert stats["unique"] == 3
        assert stats["top_values"]["a"] == 3

    def test_null_handling(self) -> None:
        stats = column_stats(pd.Series([1.0, None, 3.0, None, 5.0]), "numeric")
        assert stats["null_count"] == 2
        assert stats["null_pct"] == 40.0


# ---------------------------------------------------------------------------
# extract_data_features — NEW
# ---------------------------------------------------------------------------

class TestExtractDataFeatures:
    def test_summary_table_detection(self) -> None:
        """4-row table with categories → is_summary_table."""
        df = pd.DataFrame({"stage": ["A", "B", "C", "D"], "time": [7.16, 0.1, 0.013, 0.004]})
        profiles = [{"name": "stage", "type": "categorical"}, {"name": "time", "type": "numeric"}]
        feat = extract_data_features(df, profiles)
        assert feat["is_summary_table"] is True
        assert feat["n_rows"] == 4

    def test_large_dataset_not_summary(self) -> None:
        df = pd.DataFrame({"cat": ["A"] * 50 + ["B"] * 50, "val": range(100)})
        profiles = [{"name": "cat", "type": "categorical"}, {"name": "val", "type": "numeric"}]
        feat = extract_data_features(df, profiles)
        assert feat["is_summary_table"] is False

    def test_redundant_column_detection(self) -> None:
        """Time and Percentage columns that are linearly related."""
        df = pd.DataFrame({
            "stage": ["A", "B", "C", "D"],
            "time": [7.16, 0.10, 0.013, 0.004],
            "pct": [98.3, 1.4, 0.2, 0.05],
        })
        profiles = [
            {"name": "stage", "type": "categorical"},
            {"name": "time", "type": "numeric"},
            {"name": "pct", "type": "numeric"},
        ]
        feat = extract_data_features(df, profiles)
        assert feat["has_redundant_columns"] is True
        assert feat["effective_n_num"] == 1

    def test_no_redundant_columns(self) -> None:
        np.random.seed(42)
        df = pd.DataFrame({"a": [1, 5, 2, 8, 3], "b": [9, 1, 7, 2, 6]})
        profiles = [{"name": "a", "type": "numeric"}, {"name": "b", "type": "numeric"}]
        feat = extract_data_features(df, profiles)
        assert feat["has_redundant_columns"] is False

    def test_multi_scale_detection(self) -> None:
        """Metrics spanning 100ms to 9310ms → multi-scale."""
        df = pd.DataFrame({
            "metric": ["a", "b", "c"],
            "sdpa": [105, 174, 9310],
            "fa4": [100, 146, 7280],
        })
        profiles = [
            {"name": "metric", "type": "categorical"},
            {"name": "sdpa", "type": "numeric"},
            {"name": "fa4", "type": "numeric"},
        ]
        feat = extract_data_features(df, profiles)
        assert feat["is_multi_scale"] is True
        assert feat["scale_ratio"] > 10

    def test_percentage_detection(self) -> None:
        df = pd.DataFrame({"cat": ["A", "B", "C"], "pct": [50.0, 30.0, 20.0]})
        profiles = [{"name": "cat", "type": "categorical"}, {"name": "pct", "type": "numeric"}]
        feat = extract_data_features(df, profiles)
        assert feat["has_sum_to_100"] is True
        assert feat["has_percentage_column"] is True

    def test_constant_column_detection(self) -> None:
        df = pd.DataFrame({"x": list(range(10)), "y": [159.0] * 10})
        profiles = [{"name": "x", "type": "numeric"}, {"name": "y", "type": "numeric"}]
        feat = extract_data_features(df, profiles)
        assert feat["columns"]["y"]["is_constant"] == True
        assert feat["columns"]["x"]["is_constant"] == False

    def test_sequence_index_detection(self) -> None:
        df = pd.DataFrame({"step": range(1, 50), "val": range(49)})
        profiles = [{"name": "step", "type": "numeric"}, {"name": "val", "type": "numeric"}]
        feat = extract_data_features(df, profiles)
        assert feat["columns"]["step"]["is_sequence_index"] is True


# ---------------------------------------------------------------------------
# recommend_charts — core regression tests from reviewer findings
# ---------------------------------------------------------------------------

class TestRecommendChartsRegression:
    """Tests directly from the 6-reviewer unbiased review findings."""

    def test_summary_table_stage_breakdown(self) -> None:
        """Table 1: 4-row stage breakdown → bar, NOT scatter.
        All 6 reviewers found the old code recommended scatter for this."""
        profiles = [
            {"name": "stage", "type": "categorical", "unique": 4},
            {"name": "time", "type": "numeric"},
            {"name": "pct", "type": "numeric"},
        ]
        features = {
            "is_summary_table": True,
            "is_tiny_table": True,
            "has_redundant_columns": True,
            "redundant_column_pairs": [["time", "pct"]],
            "effective_n_num": 1,
            "has_percentage_column": True,
            "has_sum_to_100": True,
            "is_multi_scale": False,
            "scale_ratio": 1.0,
            "all_numeric_constant": False,
            "columns": {},
        }
        recs = recommend_charts(profiles, features)
        types = [r["type"] for r in recs]
        assert "scatter" not in types, "Summary table must NOT get scatter"
        assert "pairplot" not in types, "Summary table must NOT get pairplot"
        assert types[0] in ("bar", "stacked_bar", "lollipop"), f"Expected bar-family, got {types[0]}"

    def test_summary_table_cfg_comparison(self) -> None:
        """Table 2: 2-row CFG comparison → grouped_bar, NOT faceted."""
        profiles = [
            {"name": "range", "type": "categorical"},
            {"name": "status", "type": "categorical"},
            {"name": "speed", "type": "numeric"},
            {"name": "per_step", "type": "numeric"},
            {"name": "steps", "type": "numeric"},
            {"name": "subtotal", "type": "numeric"},
        ]
        features = {
            "is_summary_table": True,
            "is_tiny_table": True,
            "has_redundant_columns": False,
            "effective_n_num": 4,
            "has_percentage_column": False,
            "is_multi_scale": True,
            "scale_ratio": 65.0,
            "all_numeric_constant": False,
            "has_sum_to_100": False,
            "has_sum_to_1": False,
            "columns": {},
        }
        recs = recommend_charts(profiles, features)
        types = [r["type"] for r in recs]
        assert "faceted" not in types, "2-row table must NOT get faceted"
        assert types[0] in ("grouped_bar", "dumbbell", "bar"), f"Expected comparison chart, got {types[0]}"

    def test_benchmark_comparison_table(self) -> None:
        """Table 3: FA4 vs SDPA → grouped_bar/dumbbell, NOT scatter.
        5 metrics × 3 numeric columns (SDPA, FA4, Speedup)."""
        profiles = [
            {"name": "metric", "type": "categorical", "unique": 5},
            {"name": "sdpa", "type": "numeric"},
            {"name": "fa4", "type": "numeric"},
            {"name": "speedup", "type": "numeric"},
        ]
        features = {
            "is_summary_table": True,
            "is_tiny_table": True,
            "has_redundant_columns": False,
            "effective_n_num": 3,
            "has_percentage_column": False,
            "is_multi_scale": True,
            "scale_ratio": 93.0,
            "all_numeric_constant": False,
            "has_sum_to_100": False,
            "has_sum_to_1": False,
            "columns": {},
        }
        recs = recommend_charts(profiles, features)
        types = [r["type"] for r in recs]
        assert "scatter" not in types, "Benchmark table must NOT get scatter"
        assert types[0] in ("grouped_bar", "dumbbell", "bar"), f"Expected comparison, got {types[0]}"
        assert any(r.get("warnings") for r in recs), "Multi-scale data should produce warning"

    def test_intent_overrides_shape(self) -> None:
        """When intent=part-of-whole is provided, it overrides shape-based scatter."""
        profiles = [
            {"name": "stage", "type": "categorical"},
            {"name": "time", "type": "numeric"},
            {"name": "pct", "type": "numeric"},
        ]
        recs = recommend_charts(profiles, intent="part-of-whole")
        types = [r["type"] for r in recs]
        assert all(t in ("stacked_bar", "treemap", "pie") for t in types), \
            f"Intent=part-of-whole should give part-of-whole charts, got {types}"

    def test_constant_values_demote_line(self) -> None:
        """Ordered numeric with constant Y → NOT line chart."""
        profiles = [
            {"name": "step", "type": "numeric"},
            {"name": "value", "type": "numeric"},
        ]
        features = {
            "is_summary_table": False,
            "is_tiny_table": False,
            "has_redundant_columns": False,
            "effective_n_num": 2,
            "has_percentage_column": False,
            "is_multi_scale": False,
            "scale_ratio": 1.0,
            "all_numeric_constant": True,
            "has_sum_to_100": False,
            "has_sum_to_1": False,
            "columns": {"step": {"is_constant": False}, "value": {"is_constant": True}},
        }
        recs = recommend_charts(profiles, features)
        types = [r["type"] for r in recs]
        assert types[0] != "line", "Constant values should NOT recommend line as primary"

    def test_backward_compatibility_no_features(self) -> None:
        """Old-style call without features still works."""
        profiles = [
            {"name": "x", "type": "numeric"},
            {"name": "y", "type": "numeric"},
        ]
        recs = recommend_charts(profiles)
        assert len(recs) > 0
        assert recs[0]["type"] == "scatter"


# ---------------------------------------------------------------------------
# recommend_charts — basic branch tests
# ---------------------------------------------------------------------------

class TestRecommendChartsBranches:
    def _profiles(self, types: list[str]) -> list[dict]:
        return [{"name": f"col_{i}", "type": t} for i, t in enumerate(types)]

    def test_single_numeric(self) -> None:
        recs = recommend_charts(self._profiles(["numeric"]))
        assert recs[0]["type"] == "histogram"

    def test_single_categorical(self) -> None:
        recs = recommend_charts(self._profiles(["categorical"]))
        assert recs[0]["type"] == "bar"

    def test_datetime_numeric(self) -> None:
        recs = recommend_charts(self._profiles(["datetime", "numeric"]))
        assert recs[0]["type"] == "line"

    def test_text_only(self) -> None:
        recs = recommend_charts(self._profiles(["text"]))
        assert recs[0]["type"] == "wordcloud"

    def test_recommendation_has_all_fields(self) -> None:
        recs = recommend_charts(self._profiles(["numeric", "numeric"]))
        for rec in recs:
            assert "type" in rec
            assert "reason" in rec
            assert "supported" in rec
            assert "intent" in rec


# ---------------------------------------------------------------------------
# load_data
# ---------------------------------------------------------------------------

class TestLoadData:
    def test_load_csv(self, numeric_csv: Path) -> None:
        df = load_data(str(numeric_csv))
        assert len(df) == 15

    def test_load_with_sample(self, numeric_csv: Path) -> None:
        df = load_data(str(numeric_csv), sample_n=5)
        assert len(df) == 5


# ---------------------------------------------------------------------------
# profile_dataframe
# ---------------------------------------------------------------------------

class TestProfileDataframe:
    def test_includes_data_features(self, numeric_df: pd.DataFrame) -> None:
        result = profile_dataframe(numeric_df)
        assert "data_features" in result
        assert "n_rows" in result["data_features"]

    def test_does_not_mutate_input(self) -> None:
        df = pd.DataFrame({
            "date": [f"2024-01-{d:02d}" for d in range(1, 21)],
            "val": range(20),
        })
        original_dtype = df["date"].dtype
        profile_dataframe(df)
        assert df["date"].dtype == original_dtype

    def test_intent_parameter_affects_output(self) -> None:
        df = pd.DataFrame({"cat": ["A", "B", "C"], "val": [50, 30, 20]})
        result = profile_dataframe(df, intent="part-of-whole")
        types = [r["type"] for r in result["recommended_charts"]]
        assert "stacked_bar" in types or "treemap" in types or "pie" in types

    def test_empty_dataframe(self) -> None:
        result = profile_dataframe(pd.DataFrame())
        assert result["shape"]["rows"] == 0
