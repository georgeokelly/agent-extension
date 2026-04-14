# Chart Question Guide

> Intent-first routing table. Use BEFORE looking at data shape.
> For detailed chart descriptions, see [chart-catalog.md](chart-catalog.md).
> For code templates, see [python-recipes.md](python-recipes.md).

## How to Use This Guide

1. **Identify the user's analytical question** from the table below
2. **Pick the chart family** that matches the intent
3. **Refine by data shape** using [chart-decision-tree.md](chart-decision-tree.md)
4. **Validate** against the constraints in the rightmost column

---

## Intent Routing Table

| Intent | Question Pattern | Primary Charts | Alternatives | Key Constraints |
|---|---|---|---|---|
| **Distribution** | "How is X distributed?" "What's the spread/shape?" "Any outliers?" | histogram, boxplot | density, violin, ridgeline | Histogram for 1 var; violin for grouped; ridgeline for 6+ groups |
| **Comparison** | "How do groups compare?" "Which is biggest?" "Rank these" | bar chart, lollipop | grouped bar, stacked bar, circular barplot | Order bars by value; lollipop if bars have similar heights; horizontal if long labels |
| **Trend** | "How does X change over time?" "What's the trend?" "Evolution of..." | line chart, area chart | stacked area, streamgraph, connected scatter | Line for trend; area for magnitude; stacked area for composition over time; max 5-7 lines |
| **Relationship** | "How do X and Y relate?" "Correlation?" "Clusters?" | scatter plot | bubble, hexbin, 2D density, correlogram | Scatter if < 2000 pts; hexbin/2D density if overplotting; bubble for 3rd variable |
| **Part-of-Whole** | "What % is each part?" "Composition?" "Breakdown of..." | treemap, stacked bar | pie (max 5), sunburst, circular packing | Treemap for hierarchy; stacked bar for time-composition; pie only if <= 5 slices |
| **Flow** | "Where does X flow to?" "Migration?" "Source to destination?" | sankey diagram | chord diagram, arc diagram | Sankey for directional flow; chord for circular mutual flows; minimize crossing |
| **Hierarchy** | "How is it organized?" "Parent-child?" "Taxonomy?" | dendrogram, treemap | sunburst, circular packing | Dendrogram for clustering; treemap if values matter; interactive for > 3 levels |
| **Spatial** | "Where is it?" "Geographic distribution?" | choropleth, bubble map | hexbin map, cartogram | Always normalize; choropleth has size bias; bubble map avoids it |
| **Network** | "How are entities connected?" "Co-occurrence?" | network diagram | chord, arc, edge bundling, heatmap | Hairball risk; use layout algorithms; edge bundling for hierarchical networks |
| **Multi-dimensional** | "Compare across many variables?" "Profile?" | parallel coordinates, heatmap | spider/radar (use sparingly) | Parallel coords > radar; heatmap with clustering; max ~10 variables |

---

## Common Mistakes by Intent

### Distribution
- Don't use bar chart for distributions — that's histogram's job
- Multiple observations per group? Don't use bar + error bars — use boxplot/violin

### Comparison
- Don't use pie chart to compare — bar chart is almost always more accurate
- Bar chart y-axis MUST start at 0

### Trend
- Ordered/sequential data MUST use line/area, NOT bar chart
- Don't use dual y-axis — use separate charts or normalize
- Beware spaghetti chart (> 5-7 lines)

### Relationship
- Overplotting with many points? Switch from scatter to hexbin/2D density
- Show subgroups with color — can reveal Simpson's paradox

### Part-of-Whole
- Pie chart: max 5 slices, never 3D, never exploded
- For > 5 categories, use treemap or bar chart instead
- Stacked area for composition OVER TIME; treemap for composition at a POINT IN TIME

### Flow
- Node ordering is critical for sankey/chord — minimize crossings
- Dismiss weak connections to reduce clutter

### Multi-dimensional
- Spider/radar chart is almost always inferior to parallel coordinates or lollipop
- Heatmap needs normalization (scale by column) and clustering (reorder rows/columns)
