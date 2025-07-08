import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loader import DataLoader
import streamlit as st
from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.llm_processor import LLMProcessor
from src.report_generator import ReportGenerator
import pandas as pd
import yaml
from pathlib import Path
from loguru import logger


def run_ui():
    st.title("Automated Data Cleaning Tool")
    
    with open("config/settings.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    loader = DataLoader()
    st.sidebar.header("Cleaning Options")
    outlier_method = st.sidebar.selectbox("Outlier Detection Method", ["iqr", "isolation_forest"], 
                                         index=0 if config.get('outlier_method', 'iqr') == 'iqr' else 1)
    outlier_action = st.sidebar.selectbox("Outlier Action", ["cap", "remove", "flag"], 
                                          index=["cap", "remove", "flag"].index(config.get('outlier_action', 'cap')))
    fuzzy_threshold = st.sidebar.slider("Fuzzy Matching Threshold", 50, 100, config.get('fuzzy_threshold', 90))
    scale_numeric = st.sidebar.checkbox("Scale Numeric Columns", value=config.get('scale_numeric', False))
    scale_method = st.sidebar.selectbox("Scaling Method", ["minmax", "standard"], 
                                        index=0 if config.get('scale_method', 'minmax') == 'minmax' else 1)

    cleaner = DataCleaner(
        nullity_threshold=config.get('nullity_threshold', 0.8),
        outlier_method=outlier_method,
        outlier_action=outlier_action,
        fuzzy_threshold=fuzzy_threshold,
        scale_numeric=scale_numeric,
        scale_method=scale_method
    )
    
    llm_processor = LLMProcessor(api_key=config.get('openai_api_key', ''))
    report_generator = ReportGenerator()

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    output_format = st.selectbox("Output Format", ["csv", "excel"])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.write("### Original Data Preview")
            st.dataframe(df.head())

            if st.button("Clean Data"):
                col_suggestions = llm_processor.suggest_column_names(df)
                if col_suggestions:
                    df.rename(columns=col_suggestions, inplace=True)
                    st.write("Renamed columns:", col_suggestions)
                
                for col in df.columns:
                    missing_strategy = llm_processor.suggest_missing_value_strategy(df, col)
                    df = cleaner.handle_missing_values(df, strategy=missing_strategy.get('strategy', 'auto'))
                    if df[col].dtype == 'object':
                        category_fixes = llm_processor.detect_inconsistent_categories(df, col)
                        if category_fixes:
                            df[col] = df[col].map(category_fixes).fillna(df[col])
                            st.write(f"Fixed categories in {col}:", category_fixes)

                df = cleaner.clean(df)
                st.write("### Cleaned Data Preview")
                st.dataframe(df.head())

                output_path = f"cleaned_data.{output_format}"
                cleaner.save_output(df, output_path, output_format)
                with open(output_path, 'rb') as f:
                    st.download_button(f"Download Cleaned Data ({output_format})", f, file_name=output_path)

                summary = report_generator.generate_cleaning_summary(cleaner.actions)
                st.write("### Cleaning Summary")
                st.markdown(summary)
                
                report_path = "cleaning_report.md"
                report_generator.save_report(summary, report_path, 'markdown')
                with open(report_path, 'rb') as f:
                    st.download_button("Download Cleaning Report", f, file_name=report_path)
                
                profiling_report = report_generator.generate_profiling_report(df)
                st.write("### Profiling Report")
                st.write(profiling_report.get('stats', {}))
        except Exception as e:
            st.error(f"Error: {e}")
            logger.error(f"UI error: {e}")
            
if __name__ == "__main__":
    run_ui()
