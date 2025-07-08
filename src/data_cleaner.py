from pathlib import Path
import pandas as pd
import re
import numpy as np
from sklearn.ensemble import IsolationForest
from fuzzywuzzy import fuzz
from loguru import logger

class DataCleaner:
    """A class to clean and preprocess pandas DataFrames with advanced techniques.

    Args:
        nullity_threshold (float): Threshold for dropping columns with missing values (default: 0.8).
        outlier_method (str): Method for outlier detection ('iqr', 'isolation_forest', default: 'iqr').
        outlier_action (str): Action for handling outliers ('cap', 'remove', 'flag', default: 'cap').
        fuzzy_threshold (int): Threshold for fuzzy matching in text deduplication (default: 90).
        scale_numeric (bool): Whether to scale numeric columns (default: False).
        scale_method (str): Scaling method ('minmax', 'standard', default: 'minmax').
    """
    def __init__(self, nullity_threshold: float = 0.8, outlier_method: str = 'iqr', outlier_action: str = 'cap', 
                 fuzzy_threshold: int = 90, scale_numeric: bool = False, scale_method: str = 'minmax'):
        self.nullity_threshold = nullity_threshold
        self.outlier_method = outlier_method
        self.outlier_action = outlier_action
        self.fuzzy_threshold = fuzzy_threshold
        self.scale_numeric = scale_numeric
        self.scale_method = scale_method
        self.actions = []
        self.outlier_flags = {}

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        initial_rows = len(df)
        df = df.drop_duplicates()
        self.actions.append(f"Removed {initial_rows - len(df)} duplicate rows")
        logger.info(self.actions[-1])
        return df

    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'auto') -> pd.DataFrame:
        """Handle missing values based on strategy or auto-detection."""
        for col in df.columns:
            if df[col].isna().sum() > 0:
                if strategy == 'auto':
                    if df[col].dtype in ['int64', 'float64']:
                        strategy = 'mean' if df[col].skew() < 2 else 'median'
                    else:
                        strategy = 'mode'
                if strategy == 'mean':
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == 'median':
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == 'mode':
                    df[col] = df[col].fillna(df[col].mode()[0])
                elif strategy == 'drop':
                    df = df.dropna(subset=[col])
                self.actions.append(f"Handled missing values in '{col}' with {strategy}")
                logger.info(self.actions[-1])
        return df

    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert column names to snake_case."""
        def to_snake_case(name: str) -> str:
            name = re.sub(r'[\s-]+', '_', name).lower()
            return re.sub(r'[^a-z0-9_]', '', name)
        
        df.columns = [to_snake_case(col) for col in df.columns]
        self.actions.append("Standardized column names to snake_case")
        logger.info(self.actions[-1])
        return df

    def fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and correct inconsistent data types."""
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            self.actions.append(f"Checked and fixed data types for '{col}'")
            logger.info(self.actions[-1])
        return df

    def detect_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle outliers using IQR or Isolation Forest."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            if self.outlier_method == 'iqr':
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = ((df[col] < lower_bound) | (df[col] > upper_bound))
                    self._handle_outliers(df, col, outliers, lower_bound, upper_bound)
            elif self.outlier_method == 'isolation_forest':
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                numeric_data = df[numeric_cols].fillna(df[numeric_cols].mean())
                outlier_labels = iso_forest.fit_predict(numeric_data)
                outliers = outlier_labels == -1
                for col in numeric_cols:
                    col_outliers = pd.Series(outliers, index=df.index)
                    lower_bound = df[col].quantile(0.05)
                    upper_bound = df[col].quantile(0.95)
                    self._handle_outliers(df, col, col_outliers, lower_bound, upper_bound)
        return df

    def _handle_outliers(self, df: pd.DataFrame, col: str, outliers: pd.Series, lower_bound: float, upper_bound: float):
        """Helper method to handle outliers based on action."""
        outlier_count = outliers.sum()
        if outlier_count > 0:
            if self.outlier_action == 'cap':
                df.loc[outliers, col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                self.actions.append(f"Capped {outlier_count} outliers in '{col}'")
            elif self.outlier_action == 'remove':
                df.drop(df.index[outliers], inplace=True)
                self.actions.append(f"Removed {outlier_count} outliers in '{col}'")
            elif self.outlier_action == 'flag':
                self.outlier_flags[col] = outliers
                self.actions.append(f"Flagged {outlier_count} outliers in '{col}'")
            logger.info(self.actions[-1])

    def deduplicate_text_fuzzy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deduplicate text columns using fuzzy matching."""
        for col in df.select_dtypes(include=['object']).columns:
            unique_vals = df[col].dropna().unique()
            if len(unique_vals) < 2:
                continue
            mapping = {}
            for i, val1 in enumerate(unique_vals):
                for val2 in unique_vals[i+1:]:
                    if val1 in mapping or val2 in mapping:
                        continue
                    score = fuzz.ratio(val1.lower(), val2.lower())
                    if score >= self.fuzzy_threshold:
                        mapping[val2] = val1
            if mapping:
                df[col] = df[col].map(mapping).fillna(df[col])
                self.actions.append(f"Deduplicated {len(mapping)} text entries in '{col}' using fuzzy matching")
                logger.info(self.actions[-1])
        return df

    def scale_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numeric columns using min-max or standardization."""
        if not self.scale_numeric:
            return df
        for col in df.select_dtypes(include=[np.number]).columns:
            if self.scale_method == 'minmax':
                df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
                self.actions.append(f"Scaled '{col}' using min-max scaling")
            elif self.scale_method == 'standard':
                df[col] = (df[col] - df[col].mean()) / df[col].std()
                self.actions.append(f"Scaled '{col}' using standardization")
            logger.info(self.actions[-1])
        return df

    def parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse and standardize date columns with multiple formats."""
        date_formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y', '%Y/%m/%d', 
            '%d-%m-%Y', '%Y.%m.%d', '%d.%m.%Y'
        ]
        for col in df.columns:
            if df[col].dtype == 'object':
                for fmt in date_formats:
                    try:
                        parsed = pd.to_datetime(df[col], format=fmt, errors='coerce')
                        if parsed.notna().sum() > 0:  # If at least some values were parsed
                            df[col] = parsed
                            self.actions.append(f"Parsed '{col}' as datetime using format {fmt}")
                            logger.info(self.actions[-1])
                            break
                    except:
                        continue
        return df

    def normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize text fields (strip, lowercase)."""
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].str.len().mean() > 0:
                df[col] = df[col].str.strip().str.lower()
                self.actions.append(f"Normalized text in '{col}'")
                logger.info(self.actions[-1])
        return df

    def drop_high_nullity_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop columns with nullity above threshold."""
        for col in df.columns:
            nullity = df[col].isna().mean()
            if nullity > self.nullity_threshold:
                df = df.drop(columns=[col])
                self.actions.append(f"Dropped column '{col}' with {nullity:.2%} null values")
                logger.info(self.actions[-1])
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Orchestrate all cleaning tasks."""
        df = self.remove_duplicates(df)
        df = self.handle_missing_values(df)
        df = self.standardize_columns(df)
        df = self.fix_data_types(df)
        df = self.detect_outliers(df)
        df = self.normalize_text(df)
        df = self.deduplicate_text_fuzzy(df)  # New: Fuzzy deduplication
        df = self.drop_high_nullity_columns(df)
        df = self.parse_dates(df)  # Enhanced: Multi-format date parsing
        df = self.scale_numeric_columns(df)  # New: Numeric scaling
        return df

    def save_output(self, df: pd.DataFrame, output_path: str, format: str):
        """Save cleaned DataFrame to specified format."""
        output_path = Path(output_path)
        if format == 'csv':
            df.to_csv(output_path, index=False)
        elif format == 'excel':
            df.to_excel(output_path, index=False)
        logger.info(f"Saved cleaned data to {output_path}")