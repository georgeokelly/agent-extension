# Data Loading Recipes

Patterns for loading data from various sources into pandas DataFrames.

## CSV / TSV

```python
import pandas as pd

# Auto-detect separator and encoding
df = pd.read_csv("data.csv")

# Explicit options for tricky files
df = pd.read_csv(
    "data.csv",
    sep=",",            # use "\t" for TSV
    encoding="utf-8",   # try "latin-1" or "cp1252" if utf-8 fails
    na_values=["", "NA", "N/A", "null", "-"],
    parse_dates=["date_column"],
    dtype={"id": str},  # force string type for ID-like columns
)
```

### Encoding Detection

```python
def read_csv_auto_encoding(path, **kwargs):
    """Try common encodings in order."""
    for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "gbk"]:
        try:
            return pd.read_csv(path, encoding=enc, **kwargs)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Cannot detect encoding for {path}")
```

## Excel

```python
import pandas as pd

# Requires: pip install openpyxl
df = pd.read_excel("data.xlsx")

# Specific sheet
df = pd.read_excel("data.xlsx", sheet_name="Sheet2")

# All sheets as dict of DataFrames
all_sheets = pd.read_excel("data.xlsx", sheet_name=None)
```

## Parquet

```python
import pandas as pd

# Requires: pip install pyarrow (or fastparquet)
df = pd.read_parquet("data.parquet")

# Read specific columns only (efficient for wide datasets)
df = pd.read_parquet("data.parquet", columns=["col_a", "col_b"])
```

## JSON

```python
import pandas as pd

# Array of objects: [{"a": 1, "b": 2}, ...]
df = pd.read_json("data.json")

# Nested JSON
df = pd.json_normalize(data, record_path="items", meta=["id", "name"])
```

### From API Response

```python
import requests
import pandas as pd

resp = requests.get("https://api.example.com/data")
resp.raise_for_status()
data = resp.json()

# Flat list of dicts
df = pd.DataFrame(data)

# Nested response
df = pd.json_normalize(data["results"])
```

## SQL

```python
import pandas as pd
from sqlalchemy import create_engine

# SQLite
engine = create_engine("sqlite:///data.db")

# PostgreSQL: pip install psycopg2-binary
# engine = create_engine("postgresql://user:pass@host:5432/dbname")

# MySQL: pip install pymysql
# engine = create_engine("mysql+pymysql://user:pass@host:3306/dbname")

df = pd.read_sql("SELECT * FROM table_name", engine)

# Parameterized query
df = pd.read_sql(
    "SELECT * FROM orders WHERE date > :start",
    engine,
    params={"start": "2024-01-01"},
)
```

## Inline Data (from user message)

When the user provides data directly in conversation, parse it into a DataFrame:

```python
import pandas as pd
from io import StringIO

# Tab/space separated text
text = """
name    score   grade
Alice   95      A
Bob     82      B
Carol   91      A
"""
df = pd.read_csv(StringIO(text.strip()), sep=r"\s+")

# Dict-like data
data = [
    {"product": "A", "sales": 100},
    {"product": "B", "sales": 200},
]
df = pd.DataFrame(data)
```

## Large Files

For files too large to fit in memory:

```python
# Partial read: only first N rows (does NOT load full file)
df_sample = pd.read_csv("huge.csv", nrows=5000)

# Read in chunks for streaming processing
for chunk in pd.read_csv("huge.csv", chunksize=50000):
    process(chunk)

# Reservoir sampling (approximate random sample without full load)
import random
df_sample = pd.read_csv(
    "huge.csv",
    skiprows=lambda i: i > 0 and random.random() > 0.01,  # ~1% sample
)
```

## Post-Loading Checklist

After loading, verify data quality:

```python
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Dtypes:\n{df.dtypes}")
print(f"Null counts:\n{df.isnull().sum()}")
print(df.head())
```

Or use `data_inspect.py` to automate this:

```bash
python scripts/data_inspect.py data.csv
```
