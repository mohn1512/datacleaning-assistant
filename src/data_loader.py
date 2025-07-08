import pandas as pd
from pathlib import Path
from loguru import logger

class DataLoader:
    def __init__(self):
        self.supported_formats = {'.csv', '.xlsx', '.xls'}

    def validate_file(self, file_path: str) -> bool:
        """Validate if the file exists and has a supported format."""
        file = Path(file_path)
        if not file.exists():
            raise FileNotFoundError(f"File {file_path} does not exist.")
        if file.suffix not in self.supported_formats:
            raise ValueError(f"Unsupported file format. Supported: {self.supported_formats}")
        return True

    def load_file(self, file_path: str) -> pd.DataFrame:
        """Load CSV or Excel file into a Pandas DataFrame."""
        self.validate_file(file_path)
        file = Path(file_path)
        logger.info(f"Loading file: {file_path}")
        try:
            if file.suffix == '.csv':
                return pd.read_csv(file)
            else:
                return pd.read_excel(file)
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise