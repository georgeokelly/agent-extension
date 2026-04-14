# Terminal Charts (plotext)

ASCII-based charts for SSH / headless / no-file environments.
Requires: `pip install plotext`

## Quick Start

```python
import plotext as plt

plt.plot([1, 2, 3, 4], [10, 20, 15, 25])
plt.title("Quick Line")
plt.show()
```

## Bar Chart

```python
import plotext as plt

categories = ["A", "B", "C", "D", "E"]
values = [25, 40, 30, 55, 45]

plt.bar(categories, values)
plt.title("Bar Chart")
plt.show()
```

## Horizontal Bar

```python
import plotext as plt

categories = ["Alpha", "Beta", "Gamma", "Delta"]
values = [30, 50, 20, 40]

plt.bar(categories, values, orientation="horizontal")
plt.title("Horizontal Bar")
plt.show()
```

## Stacked Bar

```python
import plotext as plt

categories = ["Q1", "Q2", "Q3", "Q4"]
series_a = [10, 20, 15, 25]
series_b = [5, 10, 20, 15]

plt.stacked_bar(categories, [series_a, series_b], labels=["Product A", "Product B"])
plt.title("Stacked Bar")
plt.show()
```

## Line Chart

```python
import plotext as plt

x = list(range(1, 13))
y = [12, 15, 13, 18, 22, 25, 28, 26, 20, 15, 12, 10]

plt.plot(x, y, marker="braille")
plt.title("Monthly Trend")
plt.xlabel("Month")
plt.ylabel("Value")
plt.show()
```

## Multi-line

```python
import plotext as plt

x = list(range(1, 11))
plt.plot(x, [i ** 1.5 for i in x], label="Series A")
plt.plot(x, [i ** 1.2 for i in x], label="Series B")
plt.title("Multi Series")
plt.show()
```

## Scatter Plot

```python
import plotext as plt

x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [2, 4, 1, 5, 3, 7, 6, 8]

plt.scatter(x, y)
plt.title("Scatter")
plt.show()
```

## Histogram

```python
import plotext as plt
import random

data = [random.gauss(50, 15) for _ in range(1000)]
plt.hist(data, bins=30)
plt.title("Histogram")
plt.show()
```

## Heatmap (matrix)

```python
import plotext as plt

matrix = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16],
]
plt.matrix_plot(matrix)
plt.title("Heatmap")
plt.show()
```

## Date/Time Line

```python
import plotext as plt

dates = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05"]
values = [100, 120, 115, 140, 135]

plt.date_form("Y-m")
plt.plot(plt.datetimes_to_string(dates), values)
plt.title("Time Series")
plt.show()
```

## Controlling Size

```python
import plotext as plt

plt.plotsize(80, 25)  # width, height in characters
plt.plot([1, 2, 3], [10, 20, 15])
plt.title("Custom Size")
plt.show()
```

## Saving to File (optional)

plotext output is text-based. To capture it:

```python
import plotext as plt

plt.plot([1, 2, 3], [10, 20, 15])
plt.title("Saved Plot")
plt.save_fig("chart.txt")  # saves as text art
```

## Tips

- `marker="braille"` gives higher-resolution rendering for line/scatter
- Use `plt.clear_figure()` between plots in a loop
- plotext auto-detects terminal size; use `plt.plotsize()` to override
- For color terminals, plotext auto-uses colors; no extra config needed
