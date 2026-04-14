"""Tests for viz_gen.py — every chart type must generate a valid PNG."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from viz_gen import CHART_TYPES, generate_chart

@pytest.fixture
def out(tmp_path: Path) -> Path:
    return tmp_path

@pytest.fixture
def cat_num() -> pd.DataFrame:
    return pd.DataFrame({"cat": ["A","B","C","D","E"], "val": [25,40,30,55,45]})

@pytest.fixture
def two_num() -> pd.DataFrame:
    np.random.seed(42)
    return pd.DataFrame({"x": np.random.randn(50), "y": np.random.randn(50)})

@pytest.fixture
def time_series() -> pd.DataFrame:
    return pd.DataFrame({"date": pd.date_range("2024-01-01", periods=12, freq="ME"),
                          "value": [10,15,13,18,22,25,28,26,20,15,12,10]})

@pytest.fixture
def grouped() -> pd.DataFrame:
    return pd.DataFrame({"cat": ["A","A","B","B","C","C"],
                          "grp": ["X","Y","X","Y","X","Y"],
                          "val": [10,15,20,25,30,35]})

@pytest.fixture
def multi_num() -> pd.DataFrame:
    np.random.seed(0)
    return pd.DataFrame({"a": np.random.randn(30), "b": np.random.randn(30),
                          "c": np.random.randn(30), "species": (["A"]*10+["B"]*10+["C"]*10)})

@pytest.fixture
def flow_data() -> pd.DataFrame:
    return pd.DataFrame({"source": ["A","A","B","B"], "target": ["C","D","C","D"], "value": [10,20,15,25]})

def _ok(path: Path) -> None:
    assert path.exists(), f"{path} not created"
    assert path.stat().st_size > 0, f"{path} is empty"

# ---------------------------------------------------------------------------
# Comparison / Ranking
# ---------------------------------------------------------------------------
class TestBar:
    def test_gen(self, cat_num, out):
        p = out / "bar.png"
        generate_chart(cat_num, "bar", x="cat", y="val", output=str(p))
        _ok(p)

class TestGroupedBar:
    def test_gen(self, grouped, out):
        p = out / "gb.png"
        generate_chart(grouped, "grouped_bar", x="cat", y="val", output=str(p), color="grp")
        _ok(p)

class TestStackedBar:
    def test_gen(self, grouped, out):
        p = out / "sb.png"
        generate_chart(grouped, "stacked_bar", x="cat", y="val", output=str(p), color="grp")
        _ok(p)

class TestLollipop:
    def test_gen(self, cat_num, out):
        p = out / "lollipop.png"
        generate_chart(cat_num, "lollipop", x="cat", y="val", output=str(p))
        _ok(p)

class TestDumbbell:
    def test_gen(self, out):
        df = pd.DataFrame({"m": ["A","B","C"]*2, "impl": ["X"]*3+["Y"]*3, "v": [10,20,30,15,25,35]})
        p = out / "db.png"
        generate_chart(df, "dumbbell", x="m", y="v", output=str(p), color="impl")
        _ok(p)

# ---------------------------------------------------------------------------
# Distribution
# ---------------------------------------------------------------------------
class TestHistogram:
    def test_gen(self, two_num, out):
        p = out / "hist.png"
        generate_chart(two_num, "histogram", x="x", output=str(p))
        _ok(p)

class TestDensity:
    def test_gen(self, two_num, out):
        p = out / "density.png"
        generate_chart(two_num, "density", x="x", output=str(p))
        _ok(p)

class TestBoxplot:
    def test_gen(self, out):
        df = pd.DataFrame({"cat": ["A"]*20+["B"]*20, "val": list(range(40))})
        p = out / "box.png"
        generate_chart(df, "boxplot", x="cat", y="val", output=str(p))
        _ok(p)

class TestViolin:
    def test_gen(self, out):
        df = pd.DataFrame({"cat": ["A"]*20+["B"]*20, "val": list(range(40))})
        p = out / "violin.png"
        generate_chart(df, "violin", x="cat", y="val", output=str(p))
        _ok(p)

class TestRidgeline:
    def test_gen(self, out):
        np.random.seed(1)
        df = pd.DataFrame({"grp": (["A"]*50+["B"]*50+["C"]*50), "val": np.random.randn(150)})
        p = out / "ridge.png"
        generate_chart(df, "ridgeline", x="val", y="grp", output=str(p))
        _ok(p)

# ---------------------------------------------------------------------------
# Relationship
# ---------------------------------------------------------------------------
class TestScatter:
    def test_gen(self, two_num, out):
        p = out / "scatter.png"
        generate_chart(two_num, "scatter", x="x", y="y", output=str(p))
        _ok(p)

class TestHexbin:
    def test_gen(self, two_num, out):
        p = out / "hexbin.png"
        generate_chart(two_num, "hexbin", x="x", y="y", output=str(p))
        _ok(p)

class TestBubble:
    def test_gen(self, out):
        np.random.seed(0)
        df = pd.DataFrame({"x": np.random.randn(20), "y": np.random.randn(20), "sz": np.random.rand(20)*100})
        p = out / "bubble.png"
        generate_chart(df, "bubble", x="x", y="y", output=str(p), size="sz")
        _ok(p)

class TestConnectedScatter:
    def test_gen(self, time_series, out):
        p = out / "cs.png"
        generate_chart(time_series, "connected_scatter", x="date", y="value", output=str(p))
        _ok(p)

class TestPairplot:
    def test_gen(self, multi_num, out):
        p = out / "pair.png"
        df = multi_num[["a","b","c"]]
        generate_chart(df, "pairplot", output=str(p))
        _ok(p)

# ---------------------------------------------------------------------------
# Trend / Evolution
# ---------------------------------------------------------------------------
class TestLine:
    def test_gen(self, time_series, out):
        p = out / "line.png"
        generate_chart(time_series, "line", x="date", y="value", output=str(p))
        _ok(p)

class TestArea:
    def test_gen(self, time_series, out):
        p = out / "area.png"
        generate_chart(time_series, "area", x="date", y="value", output=str(p))
        _ok(p)

class TestStackedArea:
    def test_gen(self, out):
        df = pd.DataFrame({
            "month": list(range(1,7))*3,
            "grp": ["A"]*6+["B"]*6+["C"]*6,
            "val": [10,12,15,13,18,20, 5,7,6,8,9,11, 8,9,10,12,11,14],
        })
        p = out / "sa.png"
        generate_chart(df, "stacked_area", x="month", y="val", output=str(p), color="grp")
        _ok(p)

# ---------------------------------------------------------------------------
# Part-of-Whole
# ---------------------------------------------------------------------------
class TestPie:
    def test_gen(self, cat_num, out):
        p = out / "pie.png"
        generate_chart(cat_num, "pie", x="cat", y="val", output=str(p))
        _ok(p)

class TestDonut:
    def test_gen(self, cat_num, out):
        p = out / "donut.png"
        generate_chart(cat_num, "donut", x="cat", y="val", output=str(p))
        _ok(p)

class TestTreemap:
    def test_gen(self, cat_num, out):
        p = out / "treemap.png"
        generate_chart(cat_num, "treemap", x="cat", y="val", output=str(p))
        _ok(p)

class TestWaffle:
    def test_gen(self, cat_num, out):
        p = out / "waffle.png"
        generate_chart(cat_num, "waffle", x="cat", y="val", output=str(p))
        _ok(p)

class TestSunburst:
    def test_gen(self, cat_num, out):
        p = out / "sunburst.png"
        generate_chart(cat_num, "sunburst", x="cat", y="val", output=str(p))
        _ok(p)

# ---------------------------------------------------------------------------
# Correlation / Multi-dimensional
# ---------------------------------------------------------------------------
class TestHeatmap:
    def test_gen(self, out):
        df = pd.DataFrame({"a": [1,2,3,4,5], "b": [5,4,3,2,1], "c": [2,3,4,5,6]})
        p = out / "hm.png"
        generate_chart(df, "heatmap", output=str(p))
        _ok(p)

class TestParallelCoords:
    def test_gen(self, multi_num, out):
        p = out / "pc.png"
        generate_chart(multi_num, "parallel_coords", x="species", output=str(p))
        _ok(p)

class TestRadar:
    def test_gen(self, out):
        df = pd.DataFrame({"skill": ["Math","Eng","Sci","Art","Sport"], "score": [90,75,85,60,70]})
        p = out / "radar.png"
        generate_chart(df, "radar", x="skill", y="score", output=str(p))
        _ok(p)

# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------
class TestSankey:
    def test_gen(self, flow_data, out):
        p = out / "sankey.png"
        generate_chart(flow_data, "sankey", x="source", y="value", output=str(p), color="target")
        _ok(p)

# ---------------------------------------------------------------------------
# Validation & Registry
# ---------------------------------------------------------------------------
class TestValidation:
    def test_missing_x(self, cat_num, out):
        with pytest.raises(ValueError, match="requires --x"):
            generate_chart(cat_num, "bar", y="val", output=str(out / "f.png"))

    def test_nonexistent_column(self, cat_num, out):
        with pytest.raises(ValueError, match="not found"):
            generate_chart(cat_num, "bar", x="nope", y="val", output=str(out / "f.png"))

    def test_unsupported_type(self, cat_num, out):
        with pytest.raises(ValueError, match="not supported"):
            generate_chart(cat_num, "nope", x="cat", y="val", output=str(out / "f.png"))

class TestRegistry:
    def test_count(self):
        assert len(CHART_TYPES) == 27, f"Expected 27 chart types, got {len(CHART_TYPES)}"

    def test_contract(self):
        from data_inspect import _HELPER_SUPPORTED
        for t in _HELPER_SUPPORTED:
            assert t in CHART_TYPES, f"'{t}' in _HELPER_SUPPORTED but missing from CHART_TYPES"
