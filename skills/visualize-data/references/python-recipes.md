# Python Chart Recipes

Minimal, copy-paste-ready code for each chart type. All examples use the Agg backend
for headless compatibility.

## Setup (all charts)

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

STYLE_DEFAULTS = {
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
}
plt.rcParams.update(STYLE_DEFAULTS)
```

## Distribution

### Histogram

```python
fig, ax = plt.subplots()
ax.hist(df["value"], bins="auto", edgecolor="white", alpha=0.85)
ax.set_title("Distribution of Values")
ax.set_xlabel("Value")
ax.set_ylabel("Frequency")
fig.tight_layout()
fig.savefig("histogram.png", bbox_inches="tight")
plt.close(fig)
```

### Density Plot

```python
import seaborn as sns

fig, ax = plt.subplots()
sns.kdeplot(data=df, x="value", fill=True, ax=ax)
ax.set_title("Density of Values")
fig.tight_layout()
fig.savefig("density.png", bbox_inches="tight")
plt.close(fig)
```

### Boxplot

```python
fig, ax = plt.subplots()
ax.boxplot(df["value"], vert=True)
ax.set_title("Value Distribution")
ax.set_ylabel("Value")
fig.tight_layout()
fig.savefig("boxplot.png", bbox_inches="tight")
plt.close(fig)
```

### Violin Plot (grouped)

```python
import seaborn as sns

fig, ax = plt.subplots()
sns.violinplot(data=df, x="category", y="value", ax=ax)
ax.set_title("Distribution by Category")
fig.tight_layout()
fig.savefig("violin.png", bbox_inches="tight")
plt.close(fig)
```

### Ridgeline

```python
import seaborn as sns

groups = df["category"].unique()
n = len(groups)
fig, axes = plt.subplots(n, 1, figsize=(10, 2 * n), sharex=True, squeeze=False)
for ax_row, grp in zip(axes, groups):
    ax = ax_row[0]
    subset = df[df["category"] == grp]["value"]
    sns.kdeplot(subset, fill=True, ax=ax)
    ax.set_ylabel(grp)
    ax.set_yticks([])
axes[-1, 0].set_xlabel("Value")
fig.suptitle("Ridgeline Plot", fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("ridgeline.png", bbox_inches="tight")
plt.close(fig)
```

## Comparison

### Bar Chart (vertical)

```python
fig, ax = plt.subplots()
ax.bar(df["category"], df["value"])
ax.set_title("Values by Category")
ax.set_xlabel("Category")
ax.set_ylabel("Value")
ax.set_ylim(bottom=0)
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
fig.savefig("bar.png", bbox_inches="tight")
plt.close(fig)
```

### Horizontal Bar Chart

```python
fig, ax = plt.subplots()
df_sorted = df.sort_values("value")
ax.barh(df_sorted["category"], df_sorted["value"])
ax.set_title("Values by Category")
ax.set_xlabel("Value")
fig.tight_layout()
fig.savefig("bar_h.png", bbox_inches="tight")
plt.close(fig)
```

### Grouped Bar Chart

```python
import numpy as np

groups = df["group"].unique()
categories = df["category"].unique()
x = np.arange(len(categories))
width = 0.8 / len(groups)

fig, ax = plt.subplots()
for i, grp in enumerate(groups):
    vals = df[df["group"] == grp].set_index("category").reindex(categories)["value"]
    ax.bar(x + i * width, vals, width, label=grp)
ax.set_xticks(x + width * (len(groups) - 1) / 2)
ax.set_xticklabels(categories, rotation=45, ha="right")
ax.set_title("Grouped Comparison")
ax.legend()
ax.set_ylim(bottom=0)
fig.tight_layout()
fig.savefig("grouped_bar.png", bbox_inches="tight")
plt.close(fig)
```

### Stacked Bar Chart

```python
pivot = df.pivot_table(index="category", columns="group", values="value", aggfunc="sum")
fig, ax = plt.subplots()
pivot.plot(kind="bar", stacked=True, ax=ax)
ax.set_title("Stacked Bar")
ax.set_ylabel("Value")
ax.set_ylim(bottom=0)
fig.tight_layout()
fig.savefig("stacked_bar.png", bbox_inches="tight")
plt.close(fig)
```

### Lollipop Chart

```python
fig, ax = plt.subplots()
df_sorted = df.sort_values("value")
ax.hlines(df_sorted["category"], 0, df_sorted["value"], color="gray")
ax.plot(df_sorted["value"], df_sorted["category"], "o", color="steelblue")
ax.set_title("Lollipop Chart")
ax.set_xlabel("Value")
fig.tight_layout()
fig.savefig("lollipop.png", bbox_inches="tight")
plt.close(fig)
```

## Relationship

### Scatter Plot

```python
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(df["x"], df["y"], alpha=0.6, edgecolors="white", linewidth=0.5)
ax.set_title("X vs Y")
ax.set_xlabel("X")
ax.set_ylabel("Y")
fig.tight_layout()
fig.savefig("scatter.png", bbox_inches="tight")
plt.close(fig)
```

### Scatter with Marginals

```python
import seaborn as sns

g = sns.jointplot(data=df, x="x", y="y", kind="scatter", marginal_kws=dict(bins=30))
g.fig.suptitle("X vs Y with Marginals", y=1.02)
g.savefig("scatter_marginal.png", bbox_inches="tight")
plt.close()
```

### 2D Density / Hexbin

```python
fig, ax = plt.subplots()
hb = ax.hexbin(df["x"], df["y"], gridsize=30, cmap="viridis", mincnt=1)
fig.colorbar(hb, ax=ax, label="Count")
ax.set_title("2D Density (Hexbin)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
fig.tight_layout()
fig.savefig("hexbin.png", bbox_inches="tight")
plt.close(fig)
```

### Bubble Chart

```python
fig, ax = plt.subplots()
sc = ax.scatter(df["x"], df["y"], s=df["size"] * 10, alpha=0.5, edgecolors="white")
ax.set_title("Bubble Chart")
ax.set_xlabel("X")
ax.set_ylabel("Y")
fig.tight_layout()
fig.savefig("bubble.png", bbox_inches="tight")
plt.close(fig)
```

## Trend / Time Series

### Line Chart

```python
fig, ax = plt.subplots()
ax.plot(df["date"], df["value"], marker="o", markersize=3)
ax.set_title("Trend Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Value")
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig("line.png", bbox_inches="tight")
plt.close(fig)
```

### Multi-line Chart

```python
fig, ax = plt.subplots()
for name, group in df.groupby("series"):
    ax.plot(group["date"], group["value"], label=name, marker="o", markersize=2)
ax.set_title("Multiple Series")
ax.legend()
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig("multiline.png", bbox_inches="tight")
plt.close(fig)
```

### Area Chart

```python
fig, ax = plt.subplots()
ax.fill_between(df["date"], df["value"], alpha=0.4)
ax.plot(df["date"], df["value"])
ax.set_title("Area Chart")
ax.set_ylim(bottom=0)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig("area.png", bbox_inches="tight")
plt.close(fig)
```

### Stacked Area

```python
pivot = df.pivot_table(index="date", columns="series", values="value")
fig, ax = plt.subplots()
ax.stackplot(pivot.index, *[pivot[c] for c in pivot.columns], labels=pivot.columns, alpha=0.8)
ax.set_title("Stacked Area")
ax.legend(loc="upper left")
ax.set_ylim(bottom=0)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig("stacked_area.png", bbox_inches="tight")
plt.close(fig)
```

## Composition / Part-to-Whole

### Pie Chart (max 5 categories)

```python
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(df["value"], labels=df["category"], autopct="%1.1f%%", startangle=90)
ax.set_title("Composition")
fig.tight_layout()
fig.savefig("pie.png", bbox_inches="tight")
plt.close(fig)
```

### Treemap

```python
import squarify  # pip install squarify

fig, ax = plt.subplots(figsize=(10, 8))
squarify.plot(sizes=df["value"], label=df["category"], alpha=0.8, ax=ax)
ax.set_title("Treemap")
ax.axis("off")
fig.tight_layout()
fig.savefig("treemap.png", bbox_inches="tight")
plt.close(fig)
```

## Correlation

### Heatmap

```python
import seaborn as sns

corr = df.select_dtypes("number").corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Matrix")
fig.tight_layout()
fig.savefig("heatmap.png", bbox_inches="tight")
plt.close(fig)
```

### Pairplot

```python
import seaborn as sns

g = sns.pairplot(df.select_dtypes("number"), diag_kind="kde")
g.fig.suptitle("Pair Plot", y=1.02)
g.savefig("pairplot.png", bbox_inches="tight")
plt.close()
```

## Interactive (Plotly)

### Line Chart

```python
import plotly.express as px

fig = px.line(df, x="date", y="value", color="series", title="Interactive Trend")
fig.write_html("interactive_line.html")
print("Saved: interactive_line.html")
```

### Scatter Plot

```python
import plotly.express as px

fig = px.scatter(df, x="x", y="y", color="group", size="value",
                 title="Interactive Scatter")
fig.write_html("interactive_scatter.html")
print("Saved: interactive_scatter.html")
```

### Bar Chart

```python
import plotly.express as px

fig = px.bar(df, x="category", y="value", color="group", barmode="group",
             title="Interactive Bar")
fig.write_html("interactive_bar.html")
print("Saved: interactive_bar.html")
```

## Small Multiples / Faceting

```python
import seaborn as sns

g = sns.FacetGrid(df, col="category", col_wrap=3, sharey=True)
g.map_dataframe(sns.histplot, x="value")
g.set_titles("{col_name}")
g.fig.suptitle("Faceted Histograms", y=1.02)
g.savefig("facets.png", bbox_inches="tight")
plt.close()
```

## Network / Sankey (Plotly)

### Sankey Diagram

```python
import plotly.graph_objects as go

labels = list(set(df["source"].tolist() + df["target"].tolist()))
fig = go.Figure(go.Sankey(
    node=dict(label=labels),
    link=dict(
        source=[labels.index(s) for s in df["source"]],
        target=[labels.index(t) for t in df["target"]],
        value=df["value"],
    ),
))
fig.update_layout(title_text="Flow Diagram")
fig.write_html("sankey.html")
print("Saved: sankey.html")
```
