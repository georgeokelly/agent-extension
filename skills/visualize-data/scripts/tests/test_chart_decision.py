"""Tests for chart decision logic — end-to-end and branch-level."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest
from data_inspect import profile_dataframe, recommend_charts

FIXTURES = Path(__file__).parent / "fixtures"

class TestEndToEnd:
    def test_numeric_file(self):
        result = profile_dataframe(pd.read_csv(FIXTURES / "sample_numeric.csv"))
        types = [r["type"] for r in result["recommended_charts"]]
        assert "heatmap" in types

    def test_categorical_file(self):
        result = profile_dataframe(pd.read_csv(FIXTURES / "sample_categorical.csv"))
        types = [r["type"] for r in result["recommended_charts"]]
        assert any(t in types for t in ("bar", "heatmap", "grouped_bar"))

    def test_timeseries_file(self):
        result = profile_dataframe(pd.read_csv(FIXTURES / "sample_timeseries.csv"))
        types = [r["type"] for r in result["recommended_charts"]]
        assert "line" in types

    def test_mixed_file(self):
        result = profile_dataframe(pd.read_csv(FIXTURES / "sample_mixed.csv"))
        types = [r["type"] for r in result["recommended_charts"]]
        assert any(t in types for t in ("bar", "scatter", "boxplot", "grouped_bar"))

class TestBranches:
    def _p(self, types):
        return [{"name": f"c{i}", "type": t} for i, t in enumerate(types)]

    def test_single_numeric(self):
        assert recommend_charts(self._p(["numeric"]))[0]["type"] == "histogram"

    def test_two_numeric(self):
        assert recommend_charts(self._p(["numeric","numeric"]))[0]["type"] == "scatter"

    def test_many_numeric(self):
        assert recommend_charts(self._p(["numeric"]*6))[0]["type"] == "heatmap"

    def test_single_cat(self):
        assert recommend_charts(self._p(["categorical"]))[0]["type"] == "bar"

    def test_datetime_numeric(self):
        assert recommend_charts(self._p(["datetime","numeric"]))[0]["type"] == "line"

    def test_one_num_one_cat(self):
        assert recommend_charts(self._p(["numeric","categorical"]))[0]["type"] == "bar"

    def test_one_num_multi_cat(self):
        assert recommend_charts(self._p(["numeric","categorical","categorical"]))[0]["type"] == "grouped_bar"

    def test_multi_num_one_cat(self):
        """Without features, old behavior: scatter. With summary features: grouped_bar."""
        recs = recommend_charts(self._p(["numeric","numeric","categorical"]))
        assert recs[0]["type"] in ("scatter", "grouped_bar")

    def test_multi_num_one_cat_summary(self):
        """Summary table → should get grouped_bar, NOT scatter."""
        features = {"is_summary_table": True, "is_tiny_table": True,
                    "has_redundant_columns": False, "effective_n_num": 2,
                    "has_percentage_column": False, "is_multi_scale": False,
                    "scale_ratio": 1.0, "all_numeric_constant": False,
                    "has_sum_to_100": False, "has_sum_to_1": False, "columns": {}}
        recs = recommend_charts(self._p(["numeric","numeric","categorical"]), features)
        assert recs[0]["type"] in ("grouped_bar", "dumbbell", "bar")

class TestEdgeCases:
    def _p(self, types):
        return [{"name": f"c{i}", "type": t} for i, t in enumerate(types)]

    def test_empty(self):
        assert len(recommend_charts([])) > 0

    def test_text_only(self):
        assert recommend_charts(self._p(["text"]))[0]["type"] == "wordcloud"

    def test_unknown(self):
        assert len(recommend_charts(self._p(["unknown"]))) > 0

    def test_intent_field_present(self):
        for combo in [["numeric"], ["categorical"], ["datetime","numeric"]]:
            for rec in recommend_charts(self._p(combo)):
                assert "intent" in rec

    def test_supported_field_present(self):
        for rec in recommend_charts(self._p(["numeric"])):
            assert "supported" in rec
