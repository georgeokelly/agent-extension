"""Shared fixtures for data-viz tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import pandas as pd

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SCRIPTS_DIR = Path(__file__).parent.parent

# Add scripts dir to path so we can import data_inspect / viz_gen
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def numeric_csv() -> Path:
    return FIXTURES_DIR / "sample_numeric.csv"


@pytest.fixture
def categorical_csv() -> Path:
    return FIXTURES_DIR / "sample_categorical.csv"


@pytest.fixture
def timeseries_csv() -> Path:
    return FIXTURES_DIR / "sample_timeseries.csv"


@pytest.fixture
def mixed_csv() -> Path:
    return FIXTURES_DIR / "sample_mixed.csv"


@pytest.fixture
def numeric_df(numeric_csv: Path) -> pd.DataFrame:
    return pd.read_csv(numeric_csv)


@pytest.fixture
def categorical_df(categorical_csv: Path) -> pd.DataFrame:
    return pd.read_csv(categorical_csv)


@pytest.fixture
def timeseries_df(timeseries_csv: Path) -> pd.DataFrame:
    return pd.read_csv(timeseries_csv)


@pytest.fixture
def mixed_df(mixed_csv: Path) -> pd.DataFrame:
    return pd.read_csv(mixed_csv)
