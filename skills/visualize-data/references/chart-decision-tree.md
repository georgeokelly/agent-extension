# Chart Decision Tree

Based on [data-to-viz.com](https://www.data-to-viz.com/). Given column profiles from
`data_inspect.py`, walk the tree to find the best chart type.

## Step 1: Classify Columns

For each column in the dataset, assign one type:

| Type | Detection Rule |
|---|---|
| **numeric** | int/float dtype, > 10 unique values OR > 5% of total rows |
| **categorical** | object/string dtype, boolean, or int/float with <= 10 unique AND <= 5% of rows |
| **datetime** | datetime64 dtype, or string parseable as date |
| **text** | object dtype with mean string length > 50 |

## Step 2: Count Column Types

```
n_num  = number of numeric columns
n_cat  = number of categorical columns
n_dt   = number of datetime columns
n_text = number of text columns
```

## Step 3: Walk the Decision Tree

### Branch A: Pure Numeric

#### A1: Single numeric column (`n_num == 1, n_cat == 0, n_dt == 0`)

| Data Size | Primary | Alternatives |
|---|---|---|
| Any | **histogram** | density plot, boxplot, violin |

- Use `bins='auto'` for histogram; try different bin counts to explore
- Add a rug plot for small datasets (< 200 points)

#### A2: Two numeric columns (`n_num == 2, n_cat == 0`)

Check if one column is ordered (monotonically increasing index or sorted):

| Ordered? | Points | Primary | Alternatives |
|---|---|---|---|
| Yes (time-like) | Any | **line chart** | area chart, connected scatter |
| No | < 2000 | **scatter plot** | scatter + marginal histograms |
| No | >= 2000 | **2D density** | hexbin, contour plot |

#### A3: Three numeric columns (`n_num == 3, n_cat == 0`)

| Ordered? | Primary | Alternatives |
|---|---|---|
| One column ordered | **multi-line chart** | area chart, stacked area |
| No ordering | **bubble chart** | 3D scatter (avoid unless interactive) |

#### A4: Many numeric columns (`n_num >= 4, n_cat == 0`)

| Ordered? | Primary | Alternatives |
|---|---|---|
| One column ordered | **multi-line chart** | streamgraph, stacked area |
| No ordering | **correlogram (heatmap)** | PCA biplot, parallel coordinates |

### Branch B: Pure Categorical

#### B1: Single categorical column (`n_cat == 1, n_num == 0`)

| Unique Values | Primary | Alternatives |
|---|---|---|
| <= 10 | **bar chart** | lollipop, donut (if showing proportion) |
| 11-30 | **horizontal bar** | treemap |
| > 30 | **wordcloud** | treemap |

#### B2: Two categorical columns (`n_cat == 2, n_num == 0`)

| Relationship | Primary | Alternatives |
|---|---|---|
| Nested (hierarchical) | **treemap** | sunburst, dendrogram |
| Independent (cross-tab) | **heatmap** (count) | grouped bar, mosaic plot |
| Set membership | **venn diagram** | upset plot |

### Branch C: Numeric + Categorical Mix

#### C1: One numeric + one categorical (`n_num == 1, n_cat == 1`)

| Observations per Group | Primary | Alternatives |
|---|---|---|
| 1 per group | **bar chart** | lollipop, dot plot |
| Multiple per group | **boxplot** | violin, ridgeline, strip plot |

#### C2: One numeric + two or more categorical (`n_num == 1, n_cat >= 2`)

| Cat Relationship | Primary | Alternatives |
|---|---|---|
| Subgroups (crossed) | **grouped bar** | stacked bar, heatmap |
| Nested (hierarchical) | **treemap** | sunburst, stacked bar |

#### C3: Multiple numeric + one categorical (`n_num >= 2, n_cat == 1`)

| Numeric Ordered? | Primary | Alternatives |
|---|---|---|
| Yes (time + groups) | **multi-line by group** | faceted area, small multiples |
| No | **grouped scatter** | pairplot, parallel coordinates |

#### C4: Multiple numeric + multiple categorical (`n_num >= 2, n_cat >= 2`)

- Default: **faceted small multiples** (one chart per category combination)
- Alternative: **heatmap** with aggregated values

### Branch D: Time Series

Detected when at least one datetime column exists.

#### D1: Single time series (`n_dt == 1, n_num == 1`)

| Primary | Alternatives |
|---|---|
| **line chart** | area chart, bar chart (discrete intervals) |

#### D2: Multiple time series (`n_dt == 1, n_num >= 2` or grouped)

| Series Count | Primary | Alternatives |
|---|---|---|
| 2-5 | **multi-line chart** | faceted line charts |
| 6-15 | **small multiples** | ridgeline, heatmap (time x series) |
| > 15 | **heatmap** | streamgraph |

### Branch E: Hierarchical / Tree Data (not yet automated)

> **Note**: This branch requires semantic column detection (`parent`/`child` columns,
> nested JSON) which is not yet implemented in `data_inspect.py`. Use the chart recipes
> in `python-recipes.md` directly.

Detected by: nested JSON, columns named `parent`/`child`, or adjacency-list format.

| Has Values? | Primary | Alternatives |
|---|---|---|
| Yes (leaf values) | **treemap** | sunburst, circle packing |
| No (structure only) | **dendrogram** | tree diagram, indented list |

### Branch F: Network / Graph Data (not yet automated)

> **Note**: This branch requires semantic column detection (`source`/`target` columns)
> which is not yet implemented in `data_inspect.py`. Use the chart recipes
> in `python-recipes.md` directly.

Detected by: columns named `source`/`target`, or explicit edge-list format.

| Edge Values? | Primary | Alternatives |
|---|---|---|
| Weighted edges | **sankey** | chord diagram, weighted network |
| Unweighted | **network graph** | arc diagram, adjacency matrix |

## Step 4: Validate Choice

After selecting a chart type, check these constraints:

| Constraint | Action |
|---|---|
| Pie chart with > 5 categories | Switch to bar chart |
| Scatter with > 5000 points | Switch to 2D density or hexbin |
| Line chart with > 10 overlapping series | Use small multiples or heatmap |
| Bar chart with > 30 categories | Use horizontal bar or treemap |
| Any chart with mixed +/- values | Ensure baseline at 0; consider diverging bar |

## Programmatic Recommendation

The `data_inspect.py` script implements Branches A-D of this tree. Branches E and F
require semantic column detection and are not yet automated. Its output includes:

```json
{
  "recommended_charts": [
    {"type": "scatter", "reason": "2 numeric columns, < 2000 points, no ordering"},
    {"type": "line", "reason": "alternative if x-column represents a sequence"}
  ]
}
```

The first recommendation is the primary; others are alternatives worth considering.
