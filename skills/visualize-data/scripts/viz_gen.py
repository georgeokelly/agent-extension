#!/usr/bin/env python3
"""Chart generation helper for the data-visualization skill.

Generates charts from data files with consistent styling.

Usage:
    python viz_gen.py <file> --type <chart_type> [options]

Examples:
    python viz_gen.py data.csv --type bar --x category --y value -o chart.png
    python viz_gen.py data.csv --type scatter --x col_a --y col_b -o scatter.png
    python viz_gen.py data.csv --type histogram --x value -o hist.png
    python viz_gen.py data.csv --type line --x date --y value -o trend.png
    python viz_gen.py data.csv --type heatmap -o corr.png
    python viz_gen.py data.csv --type bar --x name --y score --terminal
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Robust import: works both as CLI script and when imported as module
try:
    from data_inspect import load_data
except ImportError:
    from .data_inspect import load_data  # type: ignore[no-redef]

# ---------------------------------------------------------------------------
# Style defaults
# ---------------------------------------------------------------------------

STYLE = {
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.grid": True,
    "grid.alpha": 0.3,
}
plt.rcParams.update(STYLE)


# ---------------------------------------------------------------------------
# Column validation
# ---------------------------------------------------------------------------

# Required columns per chart type: "x", "y", or "xy"
_REQUIRED_COLUMNS: dict[str, str] = {
    "bar": "xy", "grouped_bar": "xy", "stacked_bar": "xy",
    "lollipop": "xy", "dumbbell": "xy",
    "histogram": "x", "density": "x",
    "boxplot": "xy", "violin": "xy", "ridgeline": "xy",
    "scatter": "xy", "hexbin": "xy", "bubble": "xy",
    "connected_scatter": "xy", "pairplot": "",
    "line": "xy", "area": "xy", "stacked_area": "xy",
    "pie": "xy", "donut": "xy", "treemap": "xy",
    "waffle": "xy", "sunburst": "xy",
    "heatmap": "", "parallel_coords": "x", "radar": "xy",
    "sankey": "xy",
}


def _validate_columns(
    df: pd.DataFrame,
    chart_type: str,
    x: str | None,
    y: str | None,
) -> None:
    """Validate that required x/y columns exist in the DataFrame."""
    required = _REQUIRED_COLUMNS.get(chart_type, "")
    if "x" in required and not x:
        raise ValueError(f"Chart type '{chart_type}' requires --x column")
    if "y" in required and not y:
        raise ValueError(f"Chart type '{chart_type}' requires --y column")
    if x and x not in df.columns:
        raise ValueError(
            f"Column '{x}' not found. Available: {', '.join(df.columns)}"
        )
    if y and y not in df.columns:
        raise ValueError(
            f"Column '{y}' not found. Available: {', '.join(df.columns)}"
        )


# ---------------------------------------------------------------------------
# Chart generators
# ---------------------------------------------------------------------------

def gen_bar(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots()
    data = df.sort_values(y, ascending=False) if len(df) > 15 else df
    if len(data) > 20:
        ax.barh(data[x], data[y])
        ax.set_xlabel(y)
        ax.set_ylabel(x)
        ax.invert_yaxis()
    else:
        ax.bar(data[x], data[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_ylim(bottom=0)
        plt.xticks(rotation=45, ha="right")
    ax.set_title(kw.get("title", f"{y} by {x}"))
    return fig


def gen_grouped_bar(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Grouped bar chart. Requires a 'group' or 'color' column for grouping."""
    fig, ax = plt.subplots()
    color_col = kw.get("color")
    if color_col and color_col in df.columns:
        groups = df[color_col].unique()
        categories = df[x].unique()
        x_pos = np.arange(len(categories))
        width = 0.8 / len(groups)
        for i, grp in enumerate(groups):
            vals = df[df[color_col] == grp].set_index(x).reindex(categories)[y]
            ax.bar(x_pos + i * width, vals, width, label=grp)
        ax.set_xticks(x_pos + width * (len(groups) - 1) / 2)
        ax.set_xticklabels(categories, rotation=45, ha="right")
        ax.legend()
    else:
        ax.bar(df[x], df[y])
        plt.xticks(rotation=45, ha="right")
    ax.set_title(kw.get("title", f"{y} by {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_ylim(bottom=0)
    return fig


def gen_stacked_bar(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Stacked bar chart. Requires a 'color' column for stacking."""
    color_col = kw.get("color")
    fig, ax = plt.subplots()
    if color_col and color_col in df.columns:
        pivot = df.pivot_table(index=x, columns=color_col, values=y, aggfunc="sum")
        pivot.plot(kind="bar", stacked=True, ax=ax)
    else:
        ax.bar(df[x], df[y])
        plt.xticks(rotation=45, ha="right")
    ax.set_title(kw.get("title", f"{y} by {x} (stacked)"))
    ax.set_ylabel(y)
    ax.set_ylim(bottom=0)
    return fig


def gen_histogram(df: pd.DataFrame, x: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots()
    ax.hist(df[x].dropna(), bins=kw.get("bins", "auto"), edgecolor="white", alpha=0.85)
    ax.set_title(kw.get("title", f"Distribution of {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel("Frequency")
    return fig


def gen_scatter(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 8))
    color_col = kw.get("color")
    if color_col and color_col in df.columns:
        for name, group in df.groupby(color_col):
            ax.scatter(group[x], group[y], label=name, alpha=0.6, edgecolors="white", linewidth=0.5)
        ax.legend()
    else:
        ax.scatter(df[x], df[y], alpha=0.6, edgecolors="white", linewidth=0.5)
    ax.set_title(kw.get("title", f"{x} vs {y}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig


def gen_hexbin(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots()
    hb = ax.hexbin(df[x], df[y], gridsize=30, cmap="viridis", mincnt=1)
    fig.colorbar(hb, ax=ax, label="Count")
    ax.set_title(kw.get("title", f"2D Density: {x} vs {y}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig


def gen_line(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots()
    color_col = kw.get("color")
    if color_col and color_col in df.columns:
        for name, group in df.groupby(color_col):
            group_sorted = group.sort_values(x)
            ax.plot(group_sorted[x], group_sorted[y], label=name, marker="o", markersize=3)
        ax.legend()
    else:
        df_sorted = df.sort_values(x)
        ax.plot(df_sorted[x], df_sorted[y], marker="o", markersize=3)
    ax.set_title(kw.get("title", f"{y} over {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    fig.autofmt_xdate()
    return fig


def gen_boxplot(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots()
    groups = df[x].unique()
    data = [df[df[x] == g][y].dropna().values for g in groups]
    bp = ax.boxplot(data, tick_labels=groups, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_alpha(0.7)
    ax.set_title(kw.get("title", f"{y} by {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    plt.xticks(rotation=45, ha="right")
    return fig


def gen_heatmap(df: pd.DataFrame, **kw: Any) -> plt.Figure:
    import seaborn as sns
    numeric = df.select_dtypes("number")
    if numeric.shape[1] < 2:
        raise ValueError("Heatmap requires at least 2 numeric columns")
    corr = numeric.corr()
    fig, ax = plt.subplots(figsize=(max(8, numeric.shape[1]), max(6, numeric.shape[1] * 0.8)))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title(kw.get("title", "Correlation Matrix"))
    return fig


def gen_violin(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    import seaborn as sns
    fig, ax = plt.subplots()
    sns.violinplot(data=df, x=x, y=y, ax=ax)
    ax.set_title(kw.get("title", f"{y} distribution by {x}"))
    plt.xticks(rotation=45, ha="right")
    return fig


def gen_pie(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 8))
    if (df[y] < 0).any():
        raise ValueError("Pie chart does not support negative values")
    data = df.nlargest(5, y) if len(df) > 5 else df
    if len(df) > 5:
        other_val = df[~df[x].isin(data[x])][y].sum()
        other_row = pd.DataFrame([{x: "Other", y: other_val}])
        data = pd.concat([data, other_row], ignore_index=True)
    ax.pie(data[y], labels=data[x], autopct="%1.1f%%", startangle=90)
    ax.set_title(kw.get("title", f"{y} by {x}"))
    return fig


def gen_area(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    fig, ax = plt.subplots()
    df_sorted = df.sort_values(x)
    ax.fill_between(df_sorted[x], df_sorted[y], alpha=0.4)
    ax.plot(df_sorted[x], df_sorted[y])
    ax.set_title(kw.get("title", f"{y} over {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_ylim(bottom=0)
    fig.autofmt_xdate()
    return fig


def gen_lollipop(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Lollipop chart — less cluttered alternative to bar chart."""
    fig, ax = plt.subplots()
    df_sorted = df.sort_values(y)
    ax.hlines(df_sorted[x], 0, df_sorted[y], color="gray", linewidth=1.5)
    ax.scatter(df_sorted[y], df_sorted[x], color="#2563eb", s=60, zorder=5,
               edgecolors="white", linewidth=1)
    ax.set_title(kw.get("title", f"{y} by {x}"))
    ax.set_xlabel(y)
    return fig


def gen_dumbbell(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Dumbbell / Cleveland dotplot — compare two values per category.

    Expects long-format data with a 'color' column for the two groups,
    OR wide-format with y as the first value column and color as the second.
    For wide-format, pass two numeric column names via y and color.
    """
    color_col = kw.get("color")
    fig, ax = plt.subplots()

    if color_col and color_col in df.columns:
        groups = df[color_col].unique()
        if len(groups) == 2:
            g1, g2 = groups
            cats = df[x].unique()
            v1 = df[df[color_col] == g1].set_index(x).reindex(cats)[y]
            v2 = df[df[color_col] == g2].set_index(x).reindex(cats)[y]

            y_pos = np.arange(len(cats))
            for i, (a, b) in enumerate(zip(v1, v2)):
                ax.plot([a, b], [i, i], color="#cbd5e1", linewidth=3, solid_capstyle="round")
            ax.scatter(v1, y_pos, color="#ea580c", s=70, zorder=5,
                       edgecolors="white", linewidth=1, label=str(g1))
            ax.scatter(v2, y_pos, color="#2563eb", s=70, zorder=5,
                       edgecolors="white", linewidth=1, label=str(g2))
            ax.set_yticks(y_pos)
            ax.set_yticklabels(cats)
            ax.legend()
        else:
            return gen_grouped_bar(df, x, y, **kw)
    else:
        return gen_lollipop(df, x, y, **kw)

    ax.set_title(kw.get("title", f"{y} comparison by {x}"))
    ax.set_xlabel(y)
    return fig


def gen_treemap(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Treemap — hierarchical part-of-whole via nested rectangles."""
    try:
        import squarify
    except ImportError:
        raise ImportError("squarify is required for treemap: pip install squarify")

    fig, ax = plt.subplots(figsize=(10, 8))
    df_sorted = df.sort_values(y, ascending=False)
    import matplotlib.colors as mcolors
    cmap = plt.colormaps.get_cmap("viridis")
    n = len(df_sorted)
    colors = [cmap(i / max(n - 1, 1)) for i in range(n)]
    squarify.plot(sizes=df_sorted[y].tolist(), label=df_sorted[x].tolist(),
                  color=colors, alpha=0.8, ax=ax)
    ax.set_title(kw.get("title", f"{y} by {x}"))
    ax.axis("off")
    return fig


def gen_density(df: pd.DataFrame, x: str, **kw: Any) -> plt.Figure:
    """Density plot — smoothed distribution via KDE."""
    import seaborn as sns
    fig, ax = plt.subplots()
    color_col = kw.get("color")
    if color_col and color_col in df.columns:
        for name, group in df.groupby(color_col):
            sns.kdeplot(data=group, x=x, fill=True, alpha=0.4, ax=ax, label=str(name))
        ax.legend()
    else:
        sns.kdeplot(data=df, x=x, fill=True, ax=ax)
    ax.set_title(kw.get("title", f"Density of {x}"))
    return fig


def gen_ridgeline(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Ridgeline plot — stacked density curves per group (y = group column)."""
    import seaborn as sns
    groups = df[y].unique()
    n = len(groups)
    fig, axes = plt.subplots(n, 1, figsize=(10, max(3, 1.5 * n)), sharex=True, squeeze=False)
    for i, grp in enumerate(groups):
        ax = axes[i, 0]
        subset = df[df[y] == grp][x].dropna()
        sns.kdeplot(subset, fill=True, ax=ax, color=plt.colormaps["viridis"](i / max(n - 1, 1)))
        ax.set_ylabel(str(grp), rotation=0, ha="right", va="center")
        ax.set_yticks([])
        if i < n - 1:
            ax.set_xlabel("")
    axes[-1, 0].set_xlabel(x)
    fig.suptitle(kw.get("title", f"Distribution of {x} by {y}"), fontweight="bold")
    fig.tight_layout()
    return fig


def gen_bubble(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Bubble chart — scatter with size as 3rd variable."""
    fig, ax = plt.subplots(figsize=(8, 8))
    size_col = kw.get("size", kw.get("color"))
    if size_col and size_col in df.columns:
        sizes = df[size_col]
        sizes_norm = (sizes - sizes.min()) / max(sizes.max() - sizes.min(), 1) * 500 + 20
    else:
        sizes_norm = 60
    ax.scatter(df[x], df[y], s=sizes_norm, alpha=0.5, edgecolors="white", linewidth=0.5)
    ax.set_title(kw.get("title", f"{x} vs {y}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig


def gen_donut(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Donut chart — pie with center hole."""
    fig, ax = plt.subplots(figsize=(8, 8))
    data = df.nlargest(5, y) if len(df) > 5 else df
    if len(df) > 5:
        other_val = df[~df[x].isin(data[x])][y].sum()
        data = pd.concat([data, pd.DataFrame([{x: "Other", y: other_val}])], ignore_index=True)
    wedges, texts, autotexts = ax.pie(
        data[y], labels=data[x], autopct="%1.1f%%", startangle=90,
        pctdistance=0.8,
    )
    centre = plt.Circle((0, 0), 0.55, fc="white")
    ax.add_patch(centre)
    ax.set_title(kw.get("title", f"{y} by {x}"))
    return fig


def gen_connected_scatter(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Connected scatter — scatter with points connected in order."""
    fig, ax = plt.subplots()
    df_sorted = df.sort_values(x)
    ax.plot(df_sorted[x], df_sorted[y], color="#69b3a2", linewidth=1.5, alpha=0.7)
    ax.scatter(df_sorted[x], df_sorted[y], color="#69b3a2", s=40, zorder=5, edgecolors="white")
    ax.set_title(kw.get("title", f"{y} over {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    fig.autofmt_xdate()
    return fig


def gen_stacked_area(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Stacked area chart — evolution of multiple groups over an ordered axis.

    Expects long format with x (ordered), y (values), and color (group) columns.
    """
    color_col = kw.get("color")
    fig, ax = plt.subplots()
    if color_col and color_col in df.columns:
        pivot = df.pivot_table(index=x, columns=color_col, values=y, aggfunc="sum").fillna(0)
        pivot = pivot.sort_index()
        ax.stackplot(pivot.index, *[pivot[c] for c in pivot.columns],
                      labels=pivot.columns, alpha=0.8)
        ax.legend(loc="upper left", fontsize=9)
    else:
        df_sorted = df.sort_values(x)
        ax.fill_between(df_sorted[x], df_sorted[y], alpha=0.4)
        ax.plot(df_sorted[x], df_sorted[y])
    ax.set_title(kw.get("title", f"{y} over {x}"))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_ylim(bottom=0)
    fig.autofmt_xdate()
    return fig


def gen_parallel_coords(df: pd.DataFrame, x: str, **kw: Any) -> plt.Figure:
    """Parallel coordinates — compare samples across multiple numeric axes.

    x = the categorical column for coloring groups.
    All other numeric columns become axes.
    """
    from pandas.plotting import parallel_coordinates
    fig, ax = plt.subplots(figsize=(10, 6))
    num_cols = df.select_dtypes("number").columns.tolist()
    plot_df = df[[x] + num_cols].dropna()
    parallel_coordinates(plot_df, x, ax=ax, colormap="viridis", alpha=0.5)
    ax.set_title(kw.get("title", f"Parallel Coordinates by {x}"))
    ax.legend(loc="upper right", fontsize=8)
    plt.xticks(rotation=30, ha="right")
    return fig


def gen_radar(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Radar / Spider chart — compare values across multiple axes in circular layout.

    x = category axis (variable names), y = values.
    Optionally color = group column for multiple series.
    """
    categories = df[x].unique().tolist()
    n = len(categories)
    angles = [i / n * 2 * np.pi for i in range(n)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    color_col = kw.get("color")
    if color_col and color_col in df.columns:
        for name, group in df.groupby(color_col):
            values = group.set_index(x).reindex(categories)[y].tolist()
            values += values[:1]
            ax.plot(angles, values, linewidth=2, label=str(name))
            ax.fill(angles, values, alpha=0.1)
        ax.legend(loc="upper right", fontsize=8, bbox_to_anchor=(1.3, 1.1))
    else:
        values = df.set_index(x)[y].reindex(categories).tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, color="#2563eb")
        ax.fill(angles, values, alpha=0.2, color="#2563eb")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_title(kw.get("title", f"Radar: {y}"), pad=20, fontweight="bold")
    return fig


def gen_sankey(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Sankey diagram — flow between source and target nodes.

    x = source column, y = value column, color = target column.
    Falls back to a horizontal stacked bar if plotly is not available.
    """
    target_col = kw.get("color", "target")
    if target_col not in df.columns:
        cols = [c for c in df.columns if c not in (x, y)]
        target_col = cols[0] if cols else x

    try:
        import plotly.graph_objects as go
        labels = list(set(df[x].tolist() + df[target_col].tolist()))
        fig_plotly = go.Figure(go.Sankey(
            node=dict(label=labels, pad=15, thickness=20),
            link=dict(
                source=[labels.index(s) for s in df[x]],
                target=[labels.index(t) for t in df[target_col]],
                value=df[y],
            ),
        ))
        fig_plotly.update_layout(title_text=kw.get("title", "Sankey Diagram"))
        output = kw.get("_output", "sankey.html")
        html_path = output.rsplit(".", 1)[0] + ".html"
        fig_plotly.write_html(html_path)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Sankey saved as HTML: {html_path}\n(plotly interactive)",
                ha="center", va="center", fontsize=12, transform=ax.transAxes)
        ax.set_axis_off()
        ax.set_title(kw.get("title", "Sankey Diagram"))
        return fig
    except ImportError:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Sankey requires plotly: pip install plotly",
                ha="center", va="center", fontsize=12, transform=ax.transAxes)
        ax.set_axis_off()
        return fig


def gen_waffle(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Waffle chart — grid of squares representing proportions."""
    total = df[y].sum()
    n_cells = 100
    fig, ax = plt.subplots(figsize=(10, 6))

    cmap = plt.colormaps["tab10"]
    cell_idx = 0
    cols_per_row = 10
    for i, row in df.iterrows():
        n = max(1, round(row[y] / total * n_cells))
        color = cmap(i % 10)
        for _ in range(n):
            if cell_idx >= n_cells:
                break
            r, c = divmod(cell_idx, cols_per_row)
            ax.add_patch(plt.Rectangle((c, 9 - r), 0.9, 0.9, facecolor=color, edgecolor="white"))
            cell_idx += 1

    ax.set_xlim(-0.5, cols_per_row + 0.5)
    ax.set_ylim(-0.5, 10.5)
    ax.set_aspect("equal")
    ax.set_axis_off()

    handles = [plt.Rectangle((0, 0), 1, 1, fc=cmap(i % 10))
               for i in range(len(df))]
    labels = [f"{row[x]} ({row[y] / total * 100:.1f}%)" for _, row in df.iterrows()]
    ax.legend(handles, labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=9)
    ax.set_title(kw.get("title", f"{y} by {x} (waffle)"), fontweight="bold")
    return fig


def gen_sunburst(df: pd.DataFrame, x: str, y: str, **kw: Any) -> plt.Figure:
    """Sunburst diagram — radial part-of-whole for hierarchical data.

    Uses nested pie charts as approximation in matplotlib.
    For true interactive sunburst, use plotly.
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = plt.colormaps["viridis"]
    n = len(df)
    colors = [cmap(i / max(n - 1, 1)) for i in range(n)]

    ax.pie(df[y], labels=df[x], colors=colors, autopct="%1.1f%%",
           startangle=90, pctdistance=0.75, radius=1.0)
    inner = plt.Circle((0, 0), 0.4, fc="white")
    ax.add_patch(inner)

    ax.set_title(kw.get("title", f"Sunburst: {y} by {x}"), fontweight="bold")
    return fig


def gen_pairplot(df: pd.DataFrame, **kw: Any) -> plt.Figure:
    """Pairplot / correlogram — pairwise scatter + diagonal distributions."""
    import seaborn as sns
    color_col = kw.get("color")
    hue = color_col if color_col and color_col in df.columns else None
    g = sns.pairplot(df, hue=hue, diag_kind="kde",
                     plot_kws={"alpha": 0.5, "edgecolor": "white", "linewidth": 0.3})
    g.fig.suptitle(kw.get("title", "Pairplot"), y=1.02, fontweight="bold")
    return g.fig


CHART_TYPES = {
    # Comparison / Ranking
    "bar": gen_bar,
    "grouped_bar": gen_grouped_bar,
    "stacked_bar": gen_stacked_bar,
    "lollipop": gen_lollipop,
    "dumbbell": gen_dumbbell,
    # Distribution
    "histogram": gen_histogram,
    "density": gen_density,
    "boxplot": gen_boxplot,
    "violin": gen_violin,
    "ridgeline": gen_ridgeline,
    # Relationship
    "scatter": gen_scatter,
    "hexbin": gen_hexbin,
    "bubble": gen_bubble,
    "connected_scatter": gen_connected_scatter,
    "pairplot": gen_pairplot,
    # Trend / Evolution
    "line": gen_line,
    "area": gen_area,
    "stacked_area": gen_stacked_area,
    # Part-of-Whole
    "pie": gen_pie,
    "donut": gen_donut,
    "treemap": gen_treemap,
    "waffle": gen_waffle,
    "sunburst": gen_sunburst,
    # Correlation / Multi-dimensional
    "heatmap": gen_heatmap,
    "parallel_coords": gen_parallel_coords,
    "radar": gen_radar,
    # Flow
    "sankey": gen_sankey,
}


# ---------------------------------------------------------------------------
# Terminal chart generators (plotext)
# ---------------------------------------------------------------------------

def gen_terminal_bar(df: pd.DataFrame, x: str, y: str, **kw: Any) -> None:
    import plotext as ptx
    ptx.bar(df[x].tolist(), df[y].tolist())
    ptx.title(kw.get("title", f"{y} by {x}"))
    ptx.show()


def gen_terminal_line(df: pd.DataFrame, x: str, y: str, **kw: Any) -> None:
    import plotext as ptx
    df_sorted = df.sort_values(x)
    x_labels = [str(v) for v in df_sorted[x].tolist()]
    ptx.plot(x_labels, df_sorted[y].tolist(), marker="braille")
    ptx.title(kw.get("title", f"{y} over {x}"))
    ptx.show()


def gen_terminal_scatter(df: pd.DataFrame, x: str, y: str, **kw: Any) -> None:
    import plotext as ptx
    ptx.scatter(df[x].tolist(), df[y].tolist())
    ptx.title(kw.get("title", f"{x} vs {y}"))
    ptx.show()


def gen_terminal_histogram(df: pd.DataFrame, x: str, **kw: Any) -> None:
    import plotext as ptx
    ptx.hist(df[x].dropna().tolist(), bins=30)
    ptx.title(kw.get("title", f"Distribution of {x}"))
    ptx.show()


TERMINAL_TYPES = {
    "bar": gen_terminal_bar,
    "line": gen_terminal_line,
    "scatter": gen_terminal_scatter,
    "histogram": gen_terminal_histogram,
}


# ---------------------------------------------------------------------------
# Main generation entry point
# ---------------------------------------------------------------------------

def generate_chart(
    df: pd.DataFrame,
    chart_type: str,
    x: str | None = None,
    y: str | None = None,
    output: str = "chart.png",
    terminal: bool = False,
    **kw: Any,
) -> str | None:
    """Generate a chart and save to file (or print to terminal).

    Returns the output file path, or None for terminal output.

    Raises:
        ValueError: if chart_type is unsupported, required columns are missing,
                    or specified columns don't exist in the DataFrame.
    """
    if terminal:
        gen_func = TERMINAL_TYPES.get(chart_type)
        if gen_func is None:
            supported = ", ".join(sorted(TERMINAL_TYPES))
            raise ValueError(
                f"Terminal chart type '{chart_type}' not supported. "
                f"Supported: {supported}"
            )
        _validate_columns(df, chart_type, x, y)
        args: dict[str, Any] = {"df": df, **kw}
        if x:
            args["x"] = x
        if y:
            args["y"] = y
        gen_func(**args)
        return None

    gen_func = CHART_TYPES.get(chart_type)
    if gen_func is None:
        supported = ", ".join(sorted(CHART_TYPES))
        raise ValueError(
            f"Chart type '{chart_type}' not supported. Supported: {supported}"
        )

    _validate_columns(df, chart_type, x, y)
    args = {"df": df, **kw}
    if x:
        args["x"] = x
    if y:
        args["y"] = y
    fig = gen_func(**args)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate charts from data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="Path to data file")
    parser.add_argument("--type", required=True, dest="chart_type",
                        choices=sorted(CHART_TYPES),
                        help="Chart type to generate")
    parser.add_argument("--x", help="X-axis column name")
    parser.add_argument("--y", help="Y-axis column name")
    parser.add_argument("--color", help="Color/group column name")
    parser.add_argument("--title", help="Chart title")
    parser.add_argument("-o", "--output", default="chart.png",
                        help="Output file path (default: chart.png)")
    parser.add_argument("--terminal", action="store_true",
                        help="Output as ASCII chart in terminal")
    parser.add_argument("--sample", type=int, default=None,
                        help="Sample N rows before plotting")
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        df = load_data(args.file, sample_n=args.sample)
    except Exception as e:
        print(f"Error loading file: {e}", file=sys.stderr)
        sys.exit(1)

    kw: dict[str, Any] = {}
    if args.color:
        kw["color"] = args.color
    if args.title:
        kw["title"] = args.title

    try:
        result = generate_chart(
            df, args.chart_type,
            x=args.x, y=args.y,
            output=args.output,
            terminal=args.terminal,
            **kw,
        )
    except Exception as e:
        print(f"Error generating chart: {e}", file=sys.stderr)
        sys.exit(1)

    if result:
        print(f"Saved: {result}")


if __name__ == "__main__":
    main()
