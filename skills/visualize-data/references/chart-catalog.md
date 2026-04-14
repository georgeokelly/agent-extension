# Chart Catalog

> Source: [data-to-viz.com](https://www.data-to-viz.com/). 36 chart types organized by analytical intent.
> Each entry: Definition, What for, When NOT to use, Common mistakes.
> For code templates, see [python-recipes.md](python-recipes.md).

---

## 1. Distribution

Charts that answer: **"How is this variable distributed?"**

Use when exploring a new dataset — checking distributions is the first task you should do.

### Histogram

**Definition**: Divides a numeric variable into bins and shows the count per bin as bar height.
**What for**: Study distribution shape (normal, skewed, bimodal, uniform). Detect outliers and data quality issues (e.g., rounding artifacts show as "comb" patterns).
**When NOT**: Don't confuse with barplot (barplot = categorical, histogram = numeric). Don't overlay more than ~3 groups — use violin or ridgeline instead.
**Mistakes**: Always try several bin sizes — different bins lead to different conclusions. Unequal bin widths distort perception.

### Density Plot

**Definition**: Smoothed version of histogram using kernel density estimation. Shows probability density function.
**What for**: Same as histogram but smoother. Better for overlaying 2-3 group distributions with transparency.
**When NOT**: Don't compare more than ~3 groups on same plot. Bandwidth choice matters as much as bin size in histograms.
**Mistakes**: Play with bandwidth argument — too smooth hides real patterns, too narrow creates noise.

### Boxplot

**Definition**: Summarizes distribution via median, quartiles (Q1/Q3), whiskers (1.5x IQR), and outlier dots.
**What for**: Quick summary of distribution across groups. Shows median, spread, and outliers at a glance.
**When NOT**: Hides the actual distribution shape — a bimodal distribution looks identical to a uniform one. For large datasets, use violin instead. For small datasets, add jitter points on top.
**Mistakes**: Always show sample size per group. Consider raincloud plots (half-violin + boxplot + jitter) for maximum information.

### Violin Plot

**Definition**: Shows the density distribution for each group as a mirrored curve. Combines density plot with grouping.
**What for**: Compare both ranking and full distribution shape across groups. More informative than boxplot for large datasets.
**When NOT**: For small datasets (< ~30 per group), use boxplot with jitter instead. For > ~15 groups, consider ridgeline.
**Mistakes**: Order groups by median for easier comparison. Show sample size if groups differ significantly.

### Ridgeline Plot

**Definition**: Multiple density plots stacked vertically with slight overlap, aligned to a common x-axis.
**What for**: Compare distributions across many groups (6-20+). Works well when there's a clear pattern or ordering.
**When NOT**: Fewer than ~6 groups — use violin or boxplot. No clear pattern — overlap makes it messy.
**Mistakes**: Bandwidth choice matters. Order groups meaningfully (by median or by a natural ordering like time).

---

## 2. Comparison / Ranking

Charts that answer: **"How do values compare across categories?"**

### Barplot

**Definition**: Shows relationship between a numeric and a categorical variable. Bar height = numeric value.
**What for**: Compare values across categories. Ordered barplot shows both ranking and specific values. Supports grouped and stacked variants.
**When NOT**: Multiple observations per group — use boxplot or violin instead, not bar + error bars. Don't use for distributions (that's histogram).
**Mistakes**: Order bars by value if categories have no natural order. Y-axis must start at 0. Don't use for time series (use line chart).

### Lollipop Chart

**Definition**: Barplot variant where bars are replaced with a line segment and a dot.
**What for**: Same as barplot but less visual clutter. Especially good when many bars have similar heights (avoids Moire pattern). Cleveland dot plot variant compares two values per category.
**When NOT**: If bars must remain unsorted, bar chart is easier to read. Multiple observations per group — same caveat as barplot.
**Mistakes**: Order by value. Use horizontal version for long labels. Dumbbell variant (two dots connected) is excellent for before/after comparison.

### Circular Barplot

**Definition**: Barplot arranged in a circle. Each bar radiates from center.
**What for**: Eye-catching when you have many groups (40+) and an obvious pattern. Groups well with a secondary grouping variable.
**When NOT**: Fewer than ~40 groups — use regular barplot. Precise value comparison needed — circular layout distorts perception. Outer bars appear disproportionately larger.
**Mistakes**: Inner circle must be > 1/2 of total radius, otherwise bars are heavily skewed. Always show a Y scale along the circle.

---

## 3. Relationship / Correlation

Charts that answer: **"How do two variables relate?"**

### Scatter Plot

**Definition**: Each data point plotted by its X and Y values. Reveals relationships between 2 numeric variables.
**What for**: Detect correlation, clusters, outliers, and non-linear patterns (linear, quadratic, sinusoidal). Often accompanied by correlation coefficient or fitted model.
**When NOT**: Ordered/time data — use line chart. Sample size > ~2000 with overplotting — use 2D density or hexbin.
**Mistakes**: Show subgroups with color if available (can reveal Simpson's paradox). Add marginal distributions for extra insight.

### Bubble Plot

**Definition**: Scatterplot with a third variable encoded as bubble size.
**What for**: Show relationship between 2 variables + a third dimension via area. Good for showing 3 variables simultaneously (e.g., GDP vs life expectancy vs population).
**When NOT**: Area is poorly perceived by humans — the size variable is the hardest to read. Prioritize your variables: X and Y relationship is much clearer than size.
**Mistakes**: Map to bubble area, not radius. Show legend for bubble size. Watch for overplotting.

### 2D Density Plot

**Definition**: Extensions of density plot to 2D: hexbin, 2D histogram, contour, or kernel density on a plane.
**What for**: Avoid overplotting in scatterplots with large sample sizes. Reveals hidden patterns (clusters) that scatter hides.
**When NOT**: Small sample size — use regular scatter. Useful only when overplotting is a problem.
**Mistakes**: Play with bin size / bandwidth. Pick a good color palette (avoid rainbow).

### Correlogram

**Definition**: Matrix of scatterplots showing relationships between every pair of numeric variables. Diagonal shows distributions.
**What for**: Exploratory analysis of multivariate data. Reveals pairwise relationships at a glance. One of the first things to build on a new multivariate dataset.
**When NOT**: More than ~10 variables — plot becomes unreadable. All scatterplot caveats apply to each cell.
**Mistakes**: Show subgroups with color. Consider adding regression lines.

### Connected Scatterplot

**Definition**: Scatterplot where points are connected in order (typically time). Shows evolution of two paired variables.
**What for**: Story-telling about how two variables co-evolve over time. Powerful when both variables don't share the same unit (avoids dual axis). Direction of time flow tells the story.
**When NOT**: Time flows both directions — can mislead. Audience must be educated about this format. Always add arrows and date labels.
**Mistakes**: Readers expect time to flow left-to-right. If it doesn't, add clear directional indicators.

---

## 4. Evolution / Trend

Charts that answer: **"How does this value change over time or along a sequence?"**

### Line Chart

**Definition**: Data points connected by straight line segments, ordered by x-axis (typically time).
**What for**: Show trends, patterns, and evolution over time. Handles many data points well. Multiple series possible (but beware spaghetti).
**When NOT**: Unordered data — use scatter. More than ~5-7 overlapping lines — use small multiples or heatmap. Y-axis doesn't need to start at 0 (unlike bar chart).
**Mistakes**: Beware spaghetti chart (too many lines). Consider aspect ratio — extreme ratios mislead. Don't use dual axis for comparing two variables.

### Area Chart

**Definition**: Line chart with the area between the line and x-axis filled with color.
**What for**: Same as line chart but filled area emphasizes magnitude. Makes pattern more visually obvious. Good for showing cumulative quantities.
**When NOT**: Criticized for poor data-ink ratio. If the fill doesn't add meaning, use line chart instead.
**Mistakes**: Same caveats as line chart. Y-axis usually should start at 0 since area implies magnitude from zero.

### Stacked Area Chart

**Definition**: Multiple area charts stacked on top of each other. Each layer = one group.
**What for**: Show evolution of the whole AND relative proportions of each group. Top edge = total; layer thickness = group contribution.
**When NOT**: Studying individual group evolution — very hard to subtract other layers visually. Use small multiples with line/area charts instead.
**Mistakes**: Group order (bottom to top) matters — try several orders. Percent-stacked variant normalizes to 100% at each time point.

### Streamgraph

**Definition**: Stacked area displaced around a central axis. Produces flowing, organic shapes.
**What for**: Show relative proportions over time. More aesthetic than stacked area. Good when there's a clear pattern.
**When NOT**: Proportions remain roughly constant — figure won't be insightful. Individual group values are very hard to read.
**Mistakes**: Works best with interactivity (hover to highlight groups). Static version is mainly for aesthetic/editorial use.

---

## 5. Composition / Part-to-Whole

Charts that answer: **"What proportion does each part contribute to the whole?"**

### Pie Chart

**Definition**: Circle divided into sectors proportional to values. Sum of sectors = 100%.
**What for**: Show percentage breakdown. Widely understood by general public.
**When NOT**: Humans are bad at reading angles — hard to compare similar-sized slices. Almost always inferior to barplot for accuracy. Never use with > 5 slices, 3D, or exploded segments.
**Mistakes**: Don't use pie charts. Use barplot or lollipop instead. If you must, max 5 slices, always label with percentages.

### Treemap

**Definition**: Nested rectangles where area is proportional to value. Hierarchy shown via nesting.
**What for**: Show hierarchical part-to-whole. Efficient use of space for many items. Good for showing how the whole is divided at multiple levels.
**When NOT**: Precise value comparison — area is hard to read. More than 3 hierarchy levels — use interactive version.
**Mistakes**: Don't annotate more than 3 levels. Interactive version strongly recommended. Prioritize highest hierarchy level.

### Sunburst

**Definition**: Radial layout of nested donut rings. Center = root, outer rings = leaves.
**What for**: Show hierarchical structure with part-of-whole proportions. Alternative to treemap with radial layout.
**When NOT**: Labels are very hard to place — almost requires interactivity. Outer slices are exaggerated (larger perimeter). Angles are hard to read (same problem as pie).
**Mistakes**: Nearly always needs interactivity. Deeper slices appear disproportionately large by construction.

### Circular Packing

**Definition**: Hierarchical data shown as nested circles. Circle size = value.
**What for**: Show hierarchical organization clearly. Less space-efficient than treemap but hierarchy is more visually obvious.
**When NOT**: Precise value comparison — area encoding is inaccurate. Many hierarchy levels — use interactive version.
**Mistakes**: Many levels require interactivity. Without nesting (single level), it degrades to a less-accurate barplot.

---

## 6. Flow / Connection

Charts that answer: **"How do things flow between entities?"**

### Sankey Diagram

**Definition**: Flow diagram where arrow width is proportional to flow quantity. Nodes are rectangles, links are weighted arcs.
**What for**: Show weighted flows between entities. Two use cases: (1) evolution/migration between states, (2) source-to-destination flows with intermediate steps.
**When NOT**: Too many connections — becomes cluttered. Position nodes to minimize crossing.
**Mistakes**: Node order is critical — use algorithms to minimize crossing. Dismiss weak connections to reduce clutter.

### Chord Diagram

**Definition**: Circular layout where entities sit on the outer ring and arcs between them show weighted relationships.
**What for**: Show weighted relationships between entities in a compact circular form. Eye-catching. Good for migration/flow data.
**When NOT**: Not straightforward to read — audience needs education. Minimize arc crossings by optimizing group order.
**Mistakes**: Give plenty of explanation. Break down the graphic progressively when presenting. Dismiss weak connections.

### Arc Diagram

**Definition**: Network diagram where nodes are aligned on a single axis and connections shown as arcs above/below.
**What for**: Show network connections while keeping all node labels readable. Highlights clusters and bridges well when node order is optimized.
**When NOT**: Overall network structure is harder to see than in 2D network layout. Node order has huge impact — random order makes it useless.
**Mistakes**: Node ordering is the key. Use community detection to group related nodes together.

---

## 7. Hierarchy

Charts that answer: **"How is the data hierarchically organized?"**

### Dendrogram

**Definition**: Tree structure showing hierarchical relationships. Nodes connected by branches. Can represent explicit hierarchy or clustering results.
**What for**: Show hierarchical organization (org charts, taxonomies). Visualize clustering results — branch length represents distance between clusters.
**When NOT**: Too many leaves make it unreadable. Horizontal version preferred for long labels.
**Mistakes**: For clustering: understand which distance metric and algorithm were used. Show heatmap alongside for validation. Circular variant saves space for many nodes.

---

## 8. Spatial / Geographic

Charts that answer: **"Where are things located? How does a variable vary geographically?"**

### Choropleth Map

**Definition**: Map where regions are colored according to a numeric variable.
**What for**: Show how a variable varies across a territory. Highlight spatial patterns, compare regions.
**When NOT**: Large regions visually dominate small ones — introduces size bias. Always normalize data (per capita, per area).
**Mistakes**: Normalize your variable. Choose color palette carefully. Don't forget legend. Consider hexbin map if regions have very different sizes.

### Cartogram

**Definition**: Map where region geometry is distorted — area inflated/deflated according to a variable.
**What for**: Correct the size bias of choropleth maps. Region area reflects the variable (e.g., population), not geography.
**When NOT**: Distorted boundaries confuse audience. Always show the original map alongside for reference.
**Mistakes**: Audience needs explanation — distorted shapes are unfamiliar. Show initial map for comparison.

### Bubble Map

**Definition**: Circles of varying size placed at geographic coordinates on a map.
**What for**: Show values at specific locations. Avoids the region-size bias of choropleths. Two inputs: coordinates + numeric value, OR regions with centroids.
**When NOT**: Map to bubble area, not radius. Mind overplotting — use transparency.
**Mistakes**: Use area encoding (not diameter). Add transparency. Don't forget legend linking size to value.

### Hexbin Map

**Definition**: Two meanings: (1) regions represented as equal hexagons instead of real boundaries, (2) geographic 2D density using hexagonal bins.
**What for**: Type 1: eliminates size bias since all regions are equal hexagons. Type 2: shows density of points on a map.
**When NOT**: Type 1: readers may not recognize distorted geography — add labels. Type 2: useful only with many points.
**Mistakes**: Normalize variables. Choose color palette carefully.

---

## 9. Network

Charts that answer: **"How are entities connected?"**

### Network Diagram

**Definition**: Nodes (entities) connected by edges (relationships). Layout algorithms position nodes to reveal structure.
**What for**: Show interconnections between entities. Four types: undirected/directed x unweighted/weighted. Layout algorithm choice is critical (Fruchterman-Reingold, DrL, etc.).
**When NOT**: Too many connections → "hairball" — the main caveat. For directed weighted flows, prefer Sankey or Chord.
**Mistakes**: Hairball is the main risk. Try different layout algorithms. Add node attributes (size, color) for extra information.

### Hierarchical Edge Bundling

**Definition**: Adjacency connections bundled along hierarchy paths in a circular dendrogram layout. Reduces clutter.
**What for**: Show adjacency relations between entities organized in a hierarchy. Bundling reduces visual clutter dramatically compared to straight lines.
**When NOT**: Requires hierarchical organization of nodes. Without hierarchy, use regular network diagram.
**Mistakes**: Tension parameter controls bundling tightness. Compare bundled vs unbundled to validate that bundling doesn't hide important patterns.

---

## 10. Multi-dimensional

Charts that answer: **"How do multiple variables compare across samples?"**

### Parallel Coordinates

**Definition**: Each variable gets a vertical axis. Samples are lines connecting their values across all axes. Variables can have different units and scales.
**What for**: Compare features of samples across many quantitative variables, even with different units. Axis order and scaling are crucial.
**When NOT**: Too many samples → spaghetti chart. Highlight specific groups or use small multiples.
**Mistakes**: Try different axis orderings — minimizes line crossing. Try different scaling (normalize, standardize, center). Preferred over spider/radar chart.

### Spider / Radar Chart

**Definition**: Circular layout where each variable is an axis radiating from center. Values connected to form a polygon.
**What for**: Compare one or a few series across multiple quantitative variables. The shape gives a quick profile view.
**When NOT**: Widely criticized: circular layout harder to read than linear, category order changes shape dramatically, area grows quadratically not linearly. Almost always inferior to parallel coordinates, barplot, or lollipop.
**Mistakes**: Use parallel coordinates or lollipop plot instead. If you must use radar: max 2-3 series, use small multiples for more, be aware that category order dramatically changes the shape.

### Heatmap

**Definition**: Matrix of values represented as colors. Rows and columns can be reordered by clustering.
**What for**: General overview of a numeric matrix. Reveals patterns, clusters, and outliers. Often combined with clustering dendrograms.
**When NOT**: Extracting specific values — color-to-number mapping is imprecise. Often needs normalization (scale by column/row).
**Mistakes**: Normalize your data. Use clustering to reorder rows/columns and reveal patterns. Color palette choice is critical.

### Venn Diagram

**Definition**: Overlapping circles showing set intersections. Circle overlap area represents shared elements.
**What for**: Show intersection between 2 or 3 sets. Easy to understand shared membership.
**When NOT**: More than 3 sets — becomes unreadable. Use UpSet plot instead for > 3 sets.
**Mistakes**: Max 3 sets. Make circle areas proportional to set size when possible. Write numbers in each region.

### Wordcloud

**Definition**: Words sized proportionally to their frequency or importance.
**What for**: Quick visual impression of prominent terms. Widely used in media, well understood by public.
**When NOT**: Highly inaccurate — area is a poor metaphor for numeric values. Longer words appear bigger by construction (more letters). Use barplot or lollipop for accuracy.
**Mistakes**: Building a wordcloud is a pitfall on its own, except for aesthetic purposes. Always prefer barplot/lollipop for actual analysis.
