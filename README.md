Automated Data Cleaning Project
Overview
This project automates data cleaning tasks using Pandas, LangChain with GPT-3.5, and Streamlit. It supports CSV and Excel inputs, performs various cleaning tasks, and generates reports.
Installation
pip install -r requirements.txt

Usage
CLI
python scripts/run_cleaning.py --input sample_data/input.csv --output cleaned_data/output.csv --format csv

Streamlit UI
streamlit run src/ui.py

Configuration
Edit config/settings.yaml to set your OpenAI API key and nullity threshold.
Features

Remove duplicate rows
Handle missing values (drop, mean/median/mode)
Standardize column names to snake_case
Detect and fix inconsistent data types and outliers
Normalize text fields
Drop high-nullity columns
Generate data profiling and cleaning reports

Requirements
See requirements.txt for dependencies.
