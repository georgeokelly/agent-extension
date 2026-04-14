#!/usr/bin/env python3
"""Data profiling tool for the data-visualization skill.

Analyzes a data file and outputs a JSON summary including column types,
basic statistics, data features, and recommended chart types.

Usage:
    python data_inspect.py <file_path> [--sample N] [--intent INTENT] [--format json|text]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Column classification
# ---------------------------------------------------------------------------

_MAX_UNIQUE_FOR_CATEGORICAL = 10
_MAX_UNIQUE_RATIO_FOR_CATEGORICAL = 0.05

def classify_column(series: pd.Series) -> str:
    """Classify a pandas Series as numeric, categorical, datetime, text, or unknown."""
    if series.dropna().empty:
        return "unknown"
    if pd.api.types.is_bool_dtype(series):
        return "categorical"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        n_unique = series.nunique()
        if (n_unique <= _MAX_UNIQUE_FOR_CATEGORICAL
                and n_unique <= len(series) * _MAX_UNIQUE_RATIO_FOR_CATEGORICAL):
            return "categorical"
        return "numeric"
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        non_null = series.dropna()
        mean_len = non_null.astype(str).str.len().mean()
        if mean_len > 50:
            return "text"
        sample = non_null.head(20)
        try:
            parsed = pd.to_datetime(sample, format="mixed")
            if parsed.notna().sum() == len(sample):
                return "datetime"
        except (ValueError, TypeError):
            pass
        return "categorical"
    return "categorical"


def column_stats(series: pd.Series, col_type: str) -> dict[str, Any]:
    """Compute summary statistics for a column based on its classified type."""
    stats: dict[str, Any] = {
        "count": int(series.count()),
        "null_count": int(series.isnull().sum()),
        "null_pct": round(float(series.isnull().mean()) * 100, 1),
        "unique": int(series.nunique()),
    }
    if col_type == "numeric":
        desc = series.describe()
        stats.update({
            "min": _safe_num(desc.get("min")),
            "max": _safe_num(desc.get("max")),
            "mean": _safe_num(desc.get("mean")),
            "std": _safe_num(desc.get("std")),
            "median": _safe_num(series.median()),
        })
    elif col_type == "categorical":
        top = series.value_counts().head(5)
        stats["top_values"] = {str(k): int(v) for k, v in top.items()}
    elif col_type == "datetime":
        non_null = series.dropna()
        if len(non_null) > 0:
            try:
                dt = pd.to_datetime(non_null, format="mixed")
                stats["min"] = str(dt.min())
                stats["max"] = str(dt.max())
            except (ValueError, TypeError):
                pass
    return stats


def _safe_num(val: Any) -> float | None:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    return round(float(val), 4)


# ---------------------------------------------------------------------------
# Data feature extraction (NEW — addresses reviewer findings)
# ---------------------------------------------------------------------------

def extract_data_features(
    df: pd.DataFrame,
    profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    """Extract semantic data features beyond column types.

    These features enable smarter chart selection by detecting:
    - Data granularity (raw observations vs summary/aggregate table)
    - Redundant/derived columns (linearly correlated)
    - Multi-scale issues (values spanning orders of magnitude)
    - Constant/near-constant columns (no actual trend)
    - Composition signals (values summing to 100 or 1.0)
    """
    features: dict[str, Any] = {}
    n_rows = len(df)
    num_cols = [p["name"] for p in profiles if p["type"] == "numeric"]
    cat_cols = [p["name"] for p in profiles if p["type"] == "categorical"]

    # --- Granularity: raw vs summary table ---
    features["n_rows"] = n_rows
    features["is_summary_table"] = n_rows <= 10 and len(cat_cols) >= 1
    features["is_tiny_table"] = n_rows <= 5

    # --- Per-numeric-column features ---
    col_features: dict[str, dict[str, Any]] = {}
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        mean = s.mean()
        std = s.std() if len(s) > 1 else 0.0
        cv = std / abs(mean) if abs(mean) > 1e-10 else 0.0
        col_features[col] = {
            "cv": round(cv, 4),
            "is_constant": cv < 0.01 or s.nunique() == 1,
            "is_monotonic": bool(s.is_monotonic_increasing or s.is_monotonic_decreasing),
            "is_sequence_index": bool(
                s.is_monotonic_increasing
                and len(s) > 1
                and s.diff().dropna().std() < 1e-10
            ),
            "min": float(s.min()),
            "max": float(s.max()),
        }
    features["columns"] = col_features

    # --- Redundant/derived column detection ---
    redundant_pairs: list[list[str]] = []
    if len(num_cols) >= 2:
        for i, c1 in enumerate(num_cols):
            for c2 in num_cols[i + 1:]:
                s1 = df[c1].dropna()
                s2 = df[c2].dropna()
                common = s1.index.intersection(s2.index)
                if len(common) >= 3:
                    with np.errstate(invalid="ignore"):
                        corr = np.corrcoef(s1[common], s2[common])[0, 1]
                    if np.isnan(corr):
                        continue
                    if abs(corr) > 0.99:
                        redundant_pairs.append([c1, c2])
    features["redundant_column_pairs"] = redundant_pairs
    features["has_redundant_columns"] = len(redundant_pairs) > 0
    features["effective_n_num"] = len(num_cols) - len(redundant_pairs)

    # --- Multi-scale detection ---
    if len(num_cols) >= 2:
        mins = [col_features[c]["min"] for c in num_cols if c in col_features]
        maxs = [col_features[c]["max"] for c in num_cols if c in col_features]
        all_abs = [abs(v) for v in mins + maxs if v != 0]
        if all_abs:
            scale_ratio = max(all_abs) / max(min(all_abs), 1e-10)
            features["scale_ratio"] = round(scale_ratio, 1)
            features["is_multi_scale"] = scale_ratio > 10
        else:
            features["scale_ratio"] = 1.0
            features["is_multi_scale"] = False
    else:
        features["scale_ratio"] = 1.0
        features["is_multi_scale"] = False

    # --- Composition / part-of-whole signals ---
    features["has_percentage_column"] = False
    features["has_sum_to_100"] = False
    features["has_sum_to_1"] = False
    for col in num_cols:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        total = s.sum()
        if abs(total - 100) < 2.0:
            features["has_sum_to_100"] = True
            features["has_percentage_column"] = True
        if abs(total - 1.0) < 0.05:
            features["has_sum_to_1"] = True
            features["has_percentage_column"] = True

    # --- Constant-value detection across all numeric ---
    features["all_numeric_constant"] = all(
        col_features.get(c, {}).get("is_constant", False)
        for c in num_cols
    ) if num_cols else False

    # --- Intent inference from data features and column names ---
    features["inferred_intents"] = _infer_intents(df, profiles, features, col_features)

    return features


# Semantic column name patterns for intent inference
_COLUMN_PATTERNS: dict[str, list[str]] = {
    "trend": ["time", "date", "year", "month", "day", "step", "epoch", "iteration",
              "timestamp", "period", "quarter", "week"],
    "comparison": ["name", "category", "group", "type", "class", "label", "method",
                   "model", "version", "config", "implementation", "backend"],
    "part-of-whole": ["percent", "pct", "share", "ratio", "proportion", "fraction",
                      "contribution", "breakdown"],
    "relationship": ["correlation", "coeff", "r_squared", "p_value"],
    "flow": ["source", "target", "from", "to", "origin", "destination"],
    "hierarchy": ["parent", "child", "level", "depth", "path"],
    "spatial": ["lat", "lon", "latitude", "longitude", "geo", "country", "region",
                "state", "city", "zip", "postal"],
    "distribution": ["sample", "measurement", "observation", "trial"],
}


def _infer_intents(
    df: pd.DataFrame,
    profiles: list[dict[str, Any]],
    features: dict[str, Any],
    col_features: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Infer analytical intents from column names and data characteristics.

    Returns ranked list of [{"intent": str, "confidence": float, "evidence": [str]}].
    """
    scores: dict[str, float] = {k: 0.0 for k in _COLUMN_PATTERNS}
    evidence: dict[str, list[str]] = {k: [] for k in _COLUMN_PATTERNS}
    col_names = [c.lower().replace("_", " ") for c in df.columns]

    # Column name pattern matching
    for intent, patterns in _COLUMN_PATTERNS.items():
        for pat in patterns:
            for col_name in col_names:
                if pat in col_name:
                    scores[intent] += 0.3
                    evidence[intent].append(f"column name '{col_name}' matches '{pat}'")

    # Data feature signals
    if features.get("has_percentage_column") or features.get("has_sum_to_100") or features.get("has_sum_to_1"):
        scores["part-of-whole"] += 0.5
        evidence["part-of-whole"].append("values sum to ~100 or ~1.0")

    if features.get("all_numeric_constant"):
        scores["trend"] -= 0.4
        evidence["trend"].append("DEMOTED: all numeric values are constant")
        scores["comparison"] += 0.3
        evidence["comparison"].append("constant values → comparison of categories")

    n_num = sum(1 for p in profiles if p["type"] == "numeric")
    n_cat = sum(1 for p in profiles if p["type"] == "categorical")
    n_dt = sum(1 for p in profiles if p["type"] == "datetime")

    if n_dt >= 1:
        scores["trend"] += 0.4
        evidence["trend"].append(f"{n_dt} datetime column(s)")

    has_sequence = any(cf.get("is_sequence_index") for cf in col_features.values())
    if has_sequence and not features.get("all_numeric_constant"):
        scores["trend"] += 0.3
        evidence["trend"].append("ordered sequence index detected")

    if n_cat >= 1 and n_num >= 1 and features.get("is_summary_table"):
        scores["comparison"] += 0.4
        evidence["comparison"].append("summary table with categories + values")

    if features.get("is_multi_scale"):
        scores["comparison"] += 0.1
        evidence["comparison"].append("multi-scale data suggests metric comparison")

    if n_num >= 3 and n_cat == 0 and not has_sequence:
        scores["relationship"] += 0.3
        evidence["relationship"].append("multiple unordered numeric columns")

    # Build ranked list, filter out zero/negative scores
    results = []
    for intent, score in sorted(scores.items(), key=lambda x: -x[1]):
        if score > 0:
            results.append({
                "intent": intent,
                "confidence": round(min(score, 1.0), 2),
                "evidence": evidence[intent],
            })
    if not results:
        results.append({"intent": "comparison", "confidence": 0.1, "evidence": ["fallback"]})
    return results


# ---------------------------------------------------------------------------
# Anti-pattern checks (post-selection validation)
# ---------------------------------------------------------------------------

_ANTI_PATTERNS: dict[str, list[tuple[str, str]]] = {
    # Distribution charts: need many observations
    "histogram": [
        ("is_summary_table", "Histogram needs many values — use bar for summary tables"),
    ],
    "density": [
        ("is_summary_table", "Density needs many values — use bar for summary tables"),
    ],
    "boxplot": [
        ("is_summary_table", "Boxplot needs multiple observations per group — use bar"),
    ],
    "violin": [
        ("is_summary_table", "Violin needs many observations per group (>30) — use bar or boxplot+jitter"),
    ],
    "ridgeline": [
        ("is_summary_table", "Ridgeline needs many observations — use bar"),
        ("_few_groups", "Ridgeline needs 6+ groups — use violin or boxplot instead"),
    ],
    # Relationship charts: need many data points
    "scatter": [
        ("is_summary_table", "Scatter is meaningless with <10 points — use bar or lollipop"),
    ],
    "hexbin": [
        ("is_summary_table", "Hexbin requires many points (>2000) — use scatter or bar"),
    ],
    "bubble": [
        ("is_summary_table", "Bubble needs many points — use bar for summary tables"),
    ],
    "pairplot": [
        ("is_summary_table", "Pairplot is meaningless with <10 points"),
        ("_too_many_vars", "Pairplot becomes unreadable with >10 variables"),
    ],
    "correlogram": [
        ("_too_many_vars", "Correlogram becomes unreadable with >10 variables"),
    ],
    # Trend charts: need actual variation
    "line": [
        ("all_numeric_constant", "Values are constant — flat line; consider bar or stacked bar"),
    ],
    "area": [
        ("all_numeric_constant", "Values are constant — flat area; consider bar or stacked bar"),
    ],
    "stacked_area": [
        ("all_numeric_constant", "Values are constant — use stacked bar instead"),
        ("is_summary_table", "Stacked area needs many time points — use stacked bar"),
    ],
    "connected_scatter": [
        ("is_summary_table", "Connected scatter needs many points — use line or bar"),
    ],
    # Part-of-whole charts: limits
    "pie": [
        ("_too_many_categories", "Pie chart max 5 slices — use bar or treemap instead"),
    ],
    "donut": [
        ("_too_many_categories", "Donut max 5 slices — use bar or treemap instead"),
    ],
    "sunburst": [
        ("is_summary_table", "Sunburst needs hierarchical data — use pie or treemap for flat data"),
    ],
    # Comparison charts
    "circular_barplot": [
        ("_few_categories", "Circular barplot needs 40+ groups — use regular bar"),
    ],
    # Multi-dimensional
    "faceted": [
        ("is_tiny_table", "Faceted multiples with <5 rows creates near-empty panels"),
    ],
    "radar": [
        ("_too_many_vars", "Radar is hard to read — prefer parallel coordinates or lollipop"),
    ],
    # Network/flow: these are generally OK but warn about clutter
    "sankey": [
        ("_too_many_connections", "Too many connections make Sankey unreadable"),
    ],
}


def _check_anti_patterns(
    chart_type: str,
    features: dict[str, Any],
    profiles: list[dict[str, Any]] | None = None,
) -> str | None:
    """Check if a chart type triggers any anti-pattern for the given data features.

    Supports both direct feature keys and computed checks (prefixed with _).
    Returns a warning string if an anti-pattern fires, or None if OK.
    """
    checks = _ANTI_PATTERNS.get(chart_type, [])
    n_cat = sum(1 for p in (profiles or []) if p["type"] == "categorical")
    n_num = sum(1 for p in (profiles or []) if p["type"] == "numeric")

    for feature_key, warning in checks:
        if feature_key.startswith("_"):
            if feature_key == "_too_many_categories" and n_cat >= 1:
                max_unique = max(
                    (p.get("unique", 0) for p in (profiles or []) if p["type"] == "categorical"),
                    default=0,
                )
                if max_unique > 5:
                    return warning
            elif feature_key == "_few_categories" and n_cat >= 1:
                max_unique = max(
                    (p.get("unique", 0) for p in (profiles or []) if p["type"] == "categorical"),
                    default=0,
                )
                if max_unique < 40:
                    return warning
            elif feature_key == "_few_groups" and n_cat >= 1:
                max_unique = max(
                    (p.get("unique", 0) for p in (profiles or []) if p["type"] == "categorical"),
                    default=0,
                )
                if max_unique < 6:
                    return warning
            elif feature_key == "_too_many_vars" and n_num > 10:
                return warning
            elif feature_key == "_too_many_connections":
                n_rows = features.get("n_rows", 0)
                if n_rows > 50:
                    return warning
        else:
            if features.get(feature_key, False):
                return warning
    return None


# ---------------------------------------------------------------------------
# Chart recommendation engine (rewritten with data-feature awareness)
# ---------------------------------------------------------------------------

_HELPER_SUPPORTED = frozenset({
    "bar", "grouped_bar", "stacked_bar", "lollipop", "dumbbell",
    "histogram", "density", "boxplot", "violin", "ridgeline",
    "scatter", "hexbin", "bubble", "connected_scatter", "pairplot",
    "line", "area", "stacked_area",
    "pie", "donut", "treemap", "waffle", "sunburst",
    "heatmap", "parallel_coords", "radar",
    "sankey",
})

_CHART_INTENT: dict[str, str] = {
    "histogram": "distribution", "boxplot": "distribution",
    "violin": "distribution", "density": "distribution",
    "ridgeline": "distribution",
    "bar": "comparison", "grouped_bar": "comparison",
    "stacked_bar": "part-of-whole", "lollipop": "comparison",
    "dumbbell": "comparison",
    "scatter": "relationship", "hexbin": "relationship",
    "bubble": "relationship", "pairplot": "relationship",
    "correlogram": "relationship",
    "line": "trend", "area": "trend",
    "stacked_area": "trend", "streamgraph": "trend",
    "connected_scatter": "trend",
    "pie": "part-of-whole", "treemap": "part-of-whole",
    "sunburst": "part-of-whole",
    "sankey": "flow", "chord": "flow", "arc": "flow",
    "dendrogram": "hierarchy",
    "network": "network", "edge_bundling": "network",
    "heatmap": "multi-dimensional", "parallel": "multi-dimensional",
    "radar": "multi-dimensional", "wordcloud": "distribution",
    "faceted": "multi-dimensional",
    "choropleth": "spatial", "bubble_map": "spatial",
}

# Intent → candidate chart types (for intent-first routing)
_INTENT_CHARTS: dict[str, list[str]] = {
    "distribution": ["histogram", "boxplot", "violin", "density", "ridgeline"],
    "comparison": ["bar", "lollipop", "grouped_bar", "dumbbell"],
    "trend": ["line", "area", "stacked_area"],
    "relationship": ["scatter", "hexbin", "bubble", "correlogram"],
    "part-of-whole": ["stacked_bar", "treemap", "pie"],
    "flow": ["sankey", "chord", "arc"],
    "hierarchy": ["dendrogram", "treemap"],
    "network": ["network", "edge_bundling"],
    "multi-dimensional": ["heatmap", "parallel"],
    "spatial": ["choropleth", "bubble_map"],
}


# Per-chart pros, cons, and advisory warnings (from chart-catalog.md "When NOT" rules
# that cannot be auto-detected — these require human judgment)
_CHART_TRADEOFFS: dict[str, dict[str, Any]] = {
    "bar": {
        "pros": ["Most accurate encoding (position); easy to compare; universally understood"],
        "cons": ["Hides distribution if multiple observations per group; boring but effective"],
        "advisory": ["Order bars by value if no natural order; y-axis must start at 0"],
    },
    "lollipop": {
        "pros": ["Less cluttered than bar; dumbbell variant ideal for before/after comparison"],
        "cons": ["Harder to read if bars must remain unsorted"],
        "advisory": ["Use horizontal version for long labels"],
    },
    "dumbbell": {
        "pros": ["Perfect for comparing two values per category (A vs B)"],
        "cons": ["Requires exactly two groups; doesn't show distribution"],
        "advisory": [],
    },
    "grouped_bar": {
        "pros": ["Clear comparison across groups and categories simultaneously"],
        "cons": ["Gets cluttered with > 4-5 groups; hard to compare non-adjacent bars"],
        "advisory": [],
    },
    "stacked_bar": {
        "pros": ["Shows composition AND total simultaneously"],
        "cons": ["Hard to compare individual segments across bars (only bottom segment is easy)"],
        "advisory": ["Consider whether total or individual segments matter more"],
    },
    "histogram": {
        "pros": ["Shows distribution shape directly; reveals outliers, gaps, multimodality"],
        "cons": ["Bin size dramatically changes the message — always try multiple bin sizes"],
        "advisory": ["Don't overlay more than ~3 groups; for more, use violin or ridgeline"],
    },
    "density": {
        "pros": ["Smoother than histogram; better for overlaying 2-3 group distributions"],
        "cons": ["Bandwidth choice affects conclusions as much as histogram bin size"],
        "advisory": ["Don't compare more than ~3 groups on same plot"],
    },
    "boxplot": {
        "pros": ["Compact summary (median, quartiles, outliers); easy to compare many groups"],
        "cons": ["HIDES distribution shape — bimodal looks identical to uniform"],
        "advisory": ["Always show sample size; consider adding jitter points or switching to violin"],
    },
    "violin": {
        "pros": ["Shows full distribution shape per group; more informative than boxplot"],
        "cons": ["Needs large sample (> ~30 per group) to be meaningful"],
        "advisory": ["Order groups by median for easier comparison; show sample size if groups differ"],
    },
    "ridgeline": {
        "pros": ["Compact comparison across many groups (6-20+); space-efficient"],
        "cons": ["Overlap hides data; only works when there's a clear pattern"],
        "advisory": ["Fewer than ~6 groups → use violin or boxplot instead"],
    },
    "scatter": {
        "pros": ["Reveals correlation, clusters, outliers, non-linear patterns"],
        "cons": ["Overplotting with > ~2000 points; meaningless with very few points"],
        "advisory": ["Show subgroups with color — may reveal Simpson's paradox"],
    },
    "hexbin": {
        "pros": ["Solves overplotting for large datasets; reveals density patterns scatter hides"],
        "cons": ["Loses individual point identity; only useful when overplotting is a problem"],
        "advisory": [],
    },
    "bubble": {
        "pros": ["Encodes 3 variables simultaneously (x, y, size)"],
        "cons": ["Size variable is hardest to read — area perception is poor for humans"],
        "advisory": ["Map to area not radius; X/Y relationship is much clearer than size"],
    },
    "connected_scatter": {
        "pros": ["Shows co-evolution of 2 paired variables; avoids dual axis"],
        "cons": ["Time may flow both directions — can mislead readers"],
        "advisory": ["Always add arrows and date labels; audience needs education about this format"],
    },
    "pairplot": {
        "pros": ["Reveals pairwise relationships at a glance; first thing to try on multivariate data"],
        "cons": ["Unreadable with > ~10 variables"],
        "advisory": ["Show subgroups with color"],
    },
    "line": {
        "pros": ["Shows trends and evolution clearly; handles many data points"],
        "cons": ["Implies continuity between points; spaghetti risk with > 5-7 lines"],
        "advisory": ["Y-axis does NOT need to start at 0; don't use dual axis"],
    },
    "area": {
        "pros": ["Like line but filled area emphasizes magnitude"],
        "cons": ["Criticized for poor data-ink ratio; if fill adds no meaning, use line instead"],
        "advisory": ["Y-axis should start at 0 since area implies magnitude from zero"],
    },
    "stacked_area": {
        "pros": ["Shows evolution of whole AND relative proportions over time"],
        "cons": ["Cannot study individual group evolution — very hard to subtract layers visually"],
        "advisory": ["For individual groups, use line chart with small multiples instead"],
    },
    "pie": {
        "pros": ["Widely understood by general public; shows percentage breakdown"],
        "cons": ["Humans are bad at reading angles; almost always inferior to bar for accuracy"],
        "advisory": ["Max 5 slices; never 3D; never exploded; consider bar or treemap instead"],
    },
    "donut": {
        "pros": ["Slightly more aesthetic than pie; center can hold summary text"],
        "cons": ["Same angle-reading problem as pie"],
        "advisory": ["Same 5-slice limit as pie; prefer bar for accuracy"],
    },
    "treemap": {
        "pros": ["Efficient use of space; shows hierarchical composition; many items fit"],
        "cons": ["Area is hard to read precisely; limit to 3 hierarchy levels"],
        "advisory": ["Interactive version recommended; for precise comparison use bar instead"],
    },
    "waffle": {
        "pros": ["Intuitive grid representation of proportions; more accurate than pie"],
        "cons": ["Limited to simple compositions; doesn't scale to many categories"],
        "advisory": [],
    },
    "sunburst": {
        "pros": ["Shows hierarchical part-of-whole with radial layout"],
        "cons": ["Labels hard to place; outer slices exaggerated; nearly requires interactivity"],
        "advisory": ["Deeper slices appear disproportionately large by construction"],
    },
    "heatmap": {
        "pros": ["General overview of a numeric matrix; reveals patterns and clusters"],
        "cons": ["Color-to-number mapping is imprecise; cannot extract specific values accurately"],
        "advisory": ["Normalize data; use clustering to reorder rows/columns; color palette is critical"],
    },
    "parallel_coords": {
        "pros": ["Compare features across many variables, even with different units/scales"],
        "cons": ["Too many samples → spaghetti; axis order dramatically changes readability"],
        "advisory": ["Try different axis orderings; try different scalings; preferred over radar"],
    },
    "radar": {
        "pros": ["Quick profile view; shape gives instant impression"],
        "cons": ["Circular layout harder to read than linear; category order changes shape; area grows quadratically"],
        "advisory": ["Almost always inferior to parallel coordinates or lollipop; max 2-3 series"],
    },
    "sankey": {
        "pros": ["Shows weighted flows between entities; link width = flow quantity"],
        "cons": ["Gets cluttered with too many connections; node positioning matters"],
        "advisory": ["Minimize crossing; dismiss weak connections to reduce clutter"],
    },
    "chord": {
        "pros": ["Compact circular layout for weighted relationships; eye-catching"],
        "cons": ["Not straightforward to read — audience needs education"],
        "advisory": ["Give plenty of explanation when presenting; break down progressively"],
    },
    "arc": {
        "pros": ["All node labels readable; highlights clusters and bridges"],
        "cons": ["Overall structure harder to see than 2D network; node order is critical"],
        "advisory": ["Random node order makes it useless — use community detection to group"],
    },
}


def _rec(chart_type: str, reason: str, **extra: Any) -> dict[str, Any]:
    """Build a recommendation dict with pros/cons/advisory from chart catalog."""
    tradeoffs = _CHART_TRADEOFFS.get(chart_type, {})
    return {
        "type": chart_type,
        "reason": reason,
        "supported": chart_type in _HELPER_SUPPORTED,
        "intent": _CHART_INTENT.get(chart_type, "comparison"),
        "pros": tradeoffs.get("pros", []),
        "cons": tradeoffs.get("cons", []),
        "advisory": tradeoffs.get("advisory", []),
        **extra,
    }


def recommend_charts(
    profiles: list[dict[str, Any]],
    data_features: dict[str, Any] | None = None,
    intent: str | None = None,
) -> list[dict[str, Any]]:
    """Recommend chart types using data shape + data features + optional intent.

    Decision priority (as per 6-reviewer consensus):
      1. Intent (if provided) sets the candidate chart family
      2. Data features filter/adjust candidates (anti-patterns, granularity)
      3. Data shape (column types) refines within the family
    When intent is not provided, falls back to shape-first with feature validation.
    """
    n_num = sum(1 for p in profiles if p["type"] == "numeric")
    n_cat = sum(1 for p in profiles if p["type"] == "categorical")
    n_dt = sum(1 for p in profiles if p["type"] == "datetime")
    n_text = sum(1 for p in profiles if p["type"] == "text")

    features = data_features or {}
    is_summary = features.get("is_summary_table", False)
    effective_n_num = features.get("effective_n_num", n_num)
    has_pct = features.get("has_percentage_column", False)
    is_multi_scale = features.get("is_multi_scale", False)
    all_constant = features.get("all_numeric_constant", False)
    has_redundant = features.get("has_redundant_columns", False)

    recommendations: list[dict[str, Any]] = []
    warnings: list[str] = []

    # --- Resolve intent: explicit > inferred > none ---
    resolved_intent = intent
    if not resolved_intent and features:
        inferred = features.get("inferred_intents", [])
        if inferred and inferred[0].get("confidence", 0) >= 0.5:
            resolved_intent = inferred[0]["intent"]

    # --- Intent-first path (explicit or high-confidence inferred) ---
    if resolved_intent and resolved_intent in _INTENT_CHARTS:
        candidates = _INTENT_CHARTS[resolved_intent]
        for chart in candidates:
            reason = f"intent={resolved_intent} → {chart}"
            ap = _check_anti_patterns(chart, features, profiles) if features else None
            if ap:
                warnings.append(f"{chart}: {ap}")
                continue
            recommendations.append(_rec(chart, reason))
        if recommendations:
            if is_multi_scale:
                warnings.append("Data spans multiple scales (max/min > 10x) — consider log axis, faceting, or normalizing")
            if warnings:
                recommendations[0]["warnings"] = warnings
            return recommendations

    # --- Feature-aware shape routing ---

    # Text-dominant
    if n_text > 0 and n_num == 0 and n_cat == 0 and n_dt == 0:
        recommendations.append(_rec("wordcloud", "text data — word frequencies (use recipes)"))
        return recommendations

    # Summary table override: use resolved_intent to guide the bar-family selection
    if is_summary and n_cat >= 1 and n_num >= 1:
        summary_intent = resolved_intent
        if not summary_intent:
            inferred = features.get("inferred_intents", [])
            if inferred:
                summary_intent = inferred[0]["intent"]

        if summary_intent == "part-of-whole":
            recommendations.append(_rec("stacked_bar", "summary part-of-whole — stacked bar"))
            recommendations.append(_rec("bar", "alternative: ordered bar for precise values"))
            if n_cat == 1 and len(set(p.get("unique", 0) for p in profiles if p["type"] == "categorical")) and \
               max((p.get("unique", 0) for p in profiles if p["type"] == "categorical"), default=0) <= 5:
                recommendations.append(_rec("pie", "alternative: pie (max 5 slices)"))
            recommendations.append(_rec("treemap", "alternative: treemap for hierarchical breakdown"))
        elif summary_intent == "distribution":
            recommendations.append(_rec("bar", "summary table — distribution view as bar"))
            recommendations.append(_rec("lollipop", "alternative: less visual clutter"))
        elif summary_intent == "trend":
            recommendations.append(_rec("bar", "summary table — too few points for line; bar comparison"))
            recommendations.append(_rec("lollipop", "alternative: ordered lollipop"))
            warnings.append("Summary table has too few rows for a proper trend chart — consider getting raw step-level data")
        elif has_pct or has_redundant:
            recommendations.append(_rec("bar", "summary table with composition data — ordered bar"))
            recommendations.append(_rec("stacked_bar", "alternative: show composition as stacked bar"))
        elif n_num >= 2:
            recommendations.append(_rec("grouped_bar", "summary table — compare metrics across groups"))
            recommendations.append(_rec("dumbbell", "alternative: before/after comparison per category"))
            recommendations.append(_rec("bar", "fallback: single metric comparison"))
        else:
            recommendations.append(_rec("bar", "summary table — compare values"))
            recommendations.append(_rec("lollipop", "alternative: less visual clutter"))

        if is_multi_scale:
            warnings.append("Data spans multiple scales — consider separate charts or log axis")
        if warnings and recommendations:
            recommendations[0]["warnings"] = warnings
        return recommendations

    # Branch D: time series
    if n_dt >= 1 and n_num >= 1:
        if all_constant:
            recommendations.append(_rec("bar", "datetime present but values are constant — bar comparison"))
            warnings.append("Values are constant despite ordered time axis — Trend intent unlikely")
        else:
            recommendations.append(_rec("line", f"{n_dt} datetime + {n_num} numeric — time series trend"))
            if n_num >= 2 or n_cat >= 1:
                recommendations.append(_rec("line", "multiple series — use --color for grouping"))
            recommendations.append(_rec("area", "alternative for cumulative trend"))
        if warnings:
            recommendations[0]["warnings"] = warnings
        return recommendations

    # Branch A: pure numeric (use effective count for redundant-aware routing)
    if n_num >= 1 and n_cat == 0:
        route_n = effective_n_num if has_redundant else n_num
        if route_n == 1:
            recommendations.append(_rec("histogram", "single numeric — show distribution"))
            recommendations.append(_rec("boxplot", "alternative distribution view"))
        elif route_n == 2:
            if all_constant:
                recommendations.append(_rec("bar", "2 numeric but constant — bar comparison"))
            else:
                recommendations.append(_rec("scatter", "2 numeric columns — show relationship"))
                recommendations.append(_rec("hexbin", "alternative if many data points"))
        else:
            recommendations.append(_rec("heatmap", f"{n_num} numeric columns — show correlations"))
            recommendations.append(_rec("pairplot", "pairwise relationships (use recipes)"))
        if has_redundant:
            warnings.append(f"Redundant columns detected: {features.get('redundant_column_pairs')} — consider using only one")
        if warnings:
            recommendations[0]["warnings"] = warnings
        return recommendations

    # Branch B: pure categorical
    if n_cat >= 1 and n_num == 0:
        if n_cat == 1:
            recommendations.append(_rec("bar", "single categorical — show counts"))
        else:
            recommendations.append(_rec("heatmap", "cross-tabulation of categories"))
            recommendations.append(_rec("grouped_bar", "compare across category groups"))
        return recommendations

    # Branch C: mixed numeric + categorical
    if n_num >= 1 and n_cat >= 1:
        route_n = effective_n_num if has_redundant else n_num
        if route_n == 1 and n_cat == 1:
            recommendations.append(_rec("bar", "1 numeric + 1 categorical — compare values"))
            recommendations.append(_rec("lollipop", "alternative: less visual clutter"))
        elif route_n == 1 and n_cat >= 2:
            recommendations.append(_rec("grouped_bar", "1 numeric + multiple categories"))
            recommendations.append(_rec("stacked_bar", "alternative composition view"))
        elif route_n >= 2 and n_cat == 1:
            recommendations.append(_rec("grouped_bar", "multi-numeric by category — grouped comparison"))
            recommendations.append(_rec("dumbbell", "before/after comparison per category"))
        else:
            recommendations.append(_rec("grouped_bar", "multiple metrics by multiple categories"))
            recommendations.append(_rec("heatmap", "aggregated values by category groups"))
        if has_redundant:
            warnings.append(f"Redundant columns detected — consider dropping derived column")
        if is_multi_scale:
            warnings.append("Data spans multiple scales — consider separate charts or normalization")
        if warnings:
            recommendations[0]["warnings"] = warnings
        return recommendations

    # Fallback
    recommendations.append(_rec("bar", "default fallback chart"))
    return recommendations


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------

def _read_csv_with_encoding(path: str, **kwargs: Any) -> pd.DataFrame:
    """Try common encodings in order for CSV files."""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252", "gbk"):
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Cannot detect encoding for {path}")


def load_data(path: str, sample_n: int | None = None) -> pd.DataFrame:
    """Load data file into DataFrame, with optional sampling."""
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in (".csv", ".tsv"):
        sep = "\t" if suffix == ".tsv" else ","
        return _read_csv_with_encoding(path, sep=sep, nrows=sample_n)

    loaders: dict[str, Any] = {
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".parquet": pd.read_parquet,
        ".json": pd.read_json,
    }

    loader = loaders.get(suffix)
    if loader is None:
        return _read_csv_with_encoding(path, nrows=sample_n)

    df = loader(path)
    if sample_n and len(df) > sample_n:
        df = df.sample(n=sample_n, random_state=42)
    return df


# ---------------------------------------------------------------------------
# Main profiling entry point
# ---------------------------------------------------------------------------

def profile_dataframe(
    df: pd.DataFrame,
    intent: str | None = None,
) -> dict[str, Any]:
    """Profile a DataFrame and return structured summary.

    Does NOT mutate the input DataFrame.
    """
    df = df.copy()

    for col in df.select_dtypes(include=["object"]).columns:
        try:
            sample = df[col].head(20).dropna()
            parsed = pd.to_datetime(sample, format="mixed")
            if len(sample) > 0 and parsed.notna().sum() == len(sample):
                df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
        except (ValueError, TypeError):
            pass

    columns = []
    for col_name in df.columns:
        series = df[col_name]
        col_type = classify_column(series)
        stats = column_stats(series, col_type)
        columns.append({
            "name": str(col_name),
            "type": col_type,
            **stats,
        })

    features = extract_data_features(df, columns)

    return {
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": columns,
        "data_features": features,
        "recommended_charts": recommend_charts(columns, features, intent),
        "sample": df.head(5).to_dict(orient="records"),
    }


def format_text(result: dict[str, Any]) -> str:
    """Format profile result as human-readable multi-option comparison."""
    lines = []
    shape = result["shape"]
    lines.append(f"Shape: {shape['rows']} rows x {shape['columns']} columns\n")

    feat = result.get("data_features", {})
    if feat.get("is_summary_table"):
        lines.append("  [!] Summary/aggregate table detected (few rows)")
    if feat.get("has_redundant_columns"):
        lines.append(f"  [!] Redundant columns: {feat.get('redundant_column_pairs')}")
    if feat.get("is_multi_scale"):
        lines.append(f"  [!] Multi-scale data (ratio: {feat.get('scale_ratio')}x)")
    if feat.get("has_percentage_column"):
        lines.append("  [!] Composition/percentage data detected")

    inferred = feat.get("inferred_intents", [])
    if inferred:
        top = inferred[0]
        lines.append(f"  [i] Inferred intent: {top['intent']} (confidence: {top['confidence']})")
        for ev in top.get("evidence", []):
            lines.append(f"      - {ev}")
    lines.append("")

    lines.append("Columns:")
    for col in result["columns"]:
        lines.append(f"  {col['name']} ({col['type']}): "
                     f"{col['count']} non-null, {col['null_pct']}% null, "
                     f"{col['unique']} unique")

    recs = result.get("recommended_charts", [])
    lines.append(f"\n{'='*60}")
    lines.append(f"Recommended Charts ({len(recs)} options — pick the one that best answers YOUR question):")
    lines.append(f"{'='*60}\n")

    for i, rec in enumerate(recs, 1):
        supported = "helper" if rec.get("supported") else "recipe"
        lines.append(f"Option {i}: {rec['type']} [{supported}]")
        lines.append(f"  Why: {rec['reason']}")
        for pro in rec.get("pros", []):
            lines.append(f"  + {pro}")
        for con in rec.get("cons", []):
            lines.append(f"  - {con}")
        for adv in rec.get("advisory", []):
            lines.append(f"  ! {adv}")
        for w in rec.get("warnings", []):
            lines.append(f"  ⚠ {w}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_VALID_INTENTS = sorted(_INTENT_CHARTS.keys())

def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a data file for visualization")
    parser.add_argument("file", help="Path to data file (CSV, Excel, Parquet, JSON)")
    parser.add_argument("--sample", type=int, default=None,
                        help="Sample N rows for profiling (useful for large files)")
    parser.add_argument("--intent", choices=_VALID_INTENTS, default=None,
                        help="Analytical intent (overrides shape-based routing)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        dest="output_format",
                        help="Output format (default: json)")
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        df = load_data(args.file, sample_n=args.sample)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)

    result = profile_dataframe(df, intent=args.intent)

    if args.output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
