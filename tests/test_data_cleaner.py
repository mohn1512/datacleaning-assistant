import pytest
from src.data_cleaner import DataCleaner
import pandas as pd
import numpy as np

def test_remove_duplicates():
    cleaner = DataCleaner()
    df = pd.DataFrame({"col1": [1, 1, 2], "col2": ["a", "a", "b"]})
    df_cleaned = cleaner.remove_duplicates(df)
    assert len(df_cleaned) == 2
    assert "Removed 1 duplicate rows" in cleaner.actions

def test_standardize_columns():
    cleaner = DataCleaner()
    df = pd.DataFrame(columns=["First Name", "Last-Name", "Age@#"])
    df_cleaned = cleaner.standardize_columns(df)
    assert list(df_cleaned.columns) == ["first_name", "last_name", "age"]