import pytest
from src.data_loader import DataLoader
import pandas as pd
from pathlib import Path

def test_validate_file():
    loader = DataLoader()
    with pytest.raises(FileNotFoundError):
        loader.validate_file("nonexistent.csv")
    with pytest.raises(ValueError):
        loader.validate_file("test.txt")

def test_load_file(tmp_path):
    loader = DataLoader()
    csv_path = tmp_path / "test.csv"
    pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]}).to_csv(csv_path, index=False)
    df = loader.load_file(str(csv_path))
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["col1", "col2"]