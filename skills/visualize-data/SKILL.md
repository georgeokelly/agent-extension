---
name: visualize-data
description: >-
  Analyzes data and generates visualizations (charts, plots, dashboards) using Python.
  Supports matplotlib, seaborn, plotly for file output, and plotext for terminal ASCII charts.
  Includes data profiling, chart type recommendation, and multi-source data loading
  (CSV, Excel, Parquet, JSON, SQL, DataFrame). Use when asked to visualize data, plot charts,
  draw graphs, create dashboards, analyze distributions, trends, comparisons, EDA,
  or when the user mentions 可视化, 画图, 图表, 探索性分析, histogram, heatmap,
  scatter, plot, chart, dashboard.
metadata:
  author: georgel
  version: "0.1"
---

# Data Visualization

Generate charts from data. Prioritize clarity and accuracy over decoration.

## Dependencies

```
# Required
pandas
matplotlib

# Recommended
seaborn         # statistical charts
plotly          # interactive HTML charts

# Optional
plotext          # terminal ASCII charts (SSH / no display)
openpyxl         # Excel support
sqlalchemy       # SQL data source
pyarrow          # Parquet support
```

Before generating charts, verify core deps are available. If missing, inform the user
and suggest `pip install pandas matplotlib seaborn`.

## Workflow

1. **Load data** — see [data-loading.md](references/data-loading.md)
2. **Identify intent** — BEFORE profiling, determine what question the user is asking (see Step 2 below). You MUST state the intent explicitly.
3. **Profile data** — run `python scripts/data_inspect.py <file> --intent <INTENT>` to get recommendations filtered by intent
4. **Present options** — show the user the multi-option output (each chart with pros/cons/advisory) and let them choose
5. **Detect environment** — choose rendering backend
6. **Generate chart** — use `viz_gen.py` or code recipes from [python-recipes.md](references/python-recipes.md)
7. **Output** — save file and report path to user

## Step 2: Identify Intent (MANDATORY)

**You MUST classify the user's question into one of the 10 intents below BEFORE running `data_inspect.py`.** This is the single most important step — getting intent wrong leads to wrong charts.

### Intent Routing Table

| Intent | User is asking... | Primary Charts |
|---|---|---|
| `distribution` | "How is X distributed?" "What's the spread?" "Any outliers?" | histogram, boxplot, violin, density |
| `comparison` | "How do groups compare?" "Which is biggest?" "Rank these" | bar, lollipop, grouped bar, dumbbell |
| `trend` | "How does X change over time?" "What's the trend?" | line, area, stacked area |
| `relationship` | "How do X and Y relate?" "Correlation?" | scatter, hexbin, bubble |
| `part-of-whole` | "What % is each part?" "Composition?" "Breakdown" | stacked bar, treemap, pie (max 5) |
| `flow` | "Where does X flow to?" "Source to destination?" | sankey, chord |
| `hierarchy` | "How is it organized? Parent-child?" | dendrogram, treemap, sunburst |
| `spatial` | "Where is it? Geographic distribution?" | choropleth, bubble map |
| `network` | "How are entities connected?" | network diagram, arc |
| `multi-dimensional` | "Compare across many variables?" | parallel coordinates, heatmap |

### Few-Shot Examples: User Question → Intent

```
"帮我看看各阶段的时间占比"           → part-of-whole
"哪个阶段最慢？"                     → comparison
"性能有没有随 step 变化的趋势？"      → trend
"FA4 比 SDPA 快多少？"               → comparison
"这些指标之间有没有相关性？"          → relationship
"数据的分布是什么样的？有没有异常值？" → distribution
"用户从哪个页面跳转到哪个页面？"      → flow
"按地区展示销售额"                    → spatial
"这些特征在不同模型之间怎么对比？"     → multi-dimensional
```

### What if intent is ambiguous?

The same data can answer different questions. If unsure:
1. Ask the user: "你想看的是各部分占比，还是不同组之间的对比？"
2. Or pass both intents and present options from both: `--intent comparison` first, then `--intent part-of-whole`, let the user compare the two sets of recommendations.

### What if the user doesn't ask a question?

If the user just says "visualize this data" with no specific question, **do NOT guess**. Run `data_inspect.py` without `--intent` (the script will infer from column names and data features) and present all options with pros/cons for the user to choose.

## Chart Selection by Data Shape (Step 4)

| Data Shape | Chart Types |
|---|---|
| 1 numeric | histogram, density, boxplot |
| 1 categorical | bar chart, treemap, wordcloud |
| 1 numeric + 1 categorical | grouped bar, violin, boxplot |
| 2 numeric (unordered) | scatter, 2D density |
| 2 numeric (ordered / time) | line chart, area chart |
| N numeric columns | heatmap, correlogram, parallel coordinates |
| N categorical + 1 numeric | stacked bar, grouped bar, heatmap |
| hierarchical | treemap, sunburst, dendrogram |
| network (edges) | network graph, chord diagram, sankey |

For the full decision tree with branching logic, read [chart-decision-tree.md](references/chart-decision-tree.md).

## Environment Detection

```python
import matplotlib
matplotlib.use("Agg")  # headless-safe; always set before importing pyplot
import matplotlib.pyplot as plt
```

| Condition | Backend | Output |
|---|---|---|
| File output needed | matplotlib Agg | PNG / SVG |
| Interactive exploration | plotly | HTML file |
| Terminal-only (user requests or `--terminal` flag) | plotext | stdout |

matplotlib with `Agg` backend works in all environments (headless, SSH, containers).
Only use plotext when the user explicitly requests terminal output or when generating
files is not feasible.

## Rendering Preferences

Default library selection:

1. **matplotlib** — default for all static charts
2. **seaborn** — when the chart is statistical (violin, pairplot, heatmap with annotations)
3. **plotly** — when the user requests interactive / HTML output

## Design Principles

- **Encoding hierarchy**: position > length > angle > area > color (Cleveland & McGill 1984)
- **Colorblind safety**: use `viridis`, `cividis`, or ColorBrewer palettes; never encode information by color alone
- **Pie chart limit**: max 5 visible slices (extras grouped as "Other"); suggest bar chart as alternative for > 5 categories
- **Bar chart baseline**: always start y-axis at 0
- **Large data** (> 5000 points): aggregate, sample, or use 2D density instead of scatter
- **Aspect ratio**: ~16:9 for line/area charts; ~1:1 for scatter plots
- **Direct labeling**: prefer labels on the chart over a separate legend when feasible

## Output Conventions

- Default format: PNG (universally viewable)
- File name: descriptive, lowercase with hyphens (e.g., `sales-by-region.png`)
- Default DPI: 150 (good balance of quality and file size)
- For SVG: add `--format svg` or user requests vector output
- For interactive HTML: use plotly and save with `fig.write_html()`
- Always print the output file path after generation

## Standard Chart Template

All matplotlib charts should follow this baseline:

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))

# ... plot data on ax ...

ax.set_title("Chart Title", fontsize=14, fontweight="bold")
ax.set_xlabel("X Label")
ax.set_ylabel("Y Label")
fig.tight_layout()
fig.savefig("output.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved: output.png")
```

## Using Helper Scripts

### Data Profiling

```bash
python scripts/data_inspect.py data.csv
```

Returns JSON with column types, statistics, and recommended chart types.
Use this to understand data before generating charts — avoids loading large datasets into context.

### Chart Generation

```bash
python scripts/viz_gen.py data.csv --type bar --x category --y value -o chart.png
```

Standardized chart generation with consistent styling.
Run `python scripts/viz_gen.py --help` for all options.

## Additional Resources

- **Intent routing**: [references/chart-question-guide.md](references/chart-question-guide.md) — what question → what chart
- **Chart catalog**: [references/chart-catalog.md](references/chart-catalog.md) — 36 chart types with definitions, use cases, and pitfalls
- Chart decision tree: [references/chart-decision-tree.md](references/chart-decision-tree.md) — data shape → chart type
- Python code recipes: [references/python-recipes.md](references/python-recipes.md)
- Terminal charts: [references/terminal-charts.md](references/terminal-charts.md)
- Data loading patterns: [references/data-loading.md](references/data-loading.md)
