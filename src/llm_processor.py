from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import json
from loguru import logger

class LLMProcessor:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
        self.column_name_prompt = PromptTemplate(
            input_variables=["columns", "sample_data"],
            template="Suggest standardized, snake_case column names for the following columns based on their content. Return a JSON object mapping original names to suggested names.\nColumns: {columns}\nSample data: {sample_data}"
        )
        self.missing_value_prompt = PromptTemplate(
            input_variables=["column", "stats"],
            template="Given a column '{column}' with stats: {stats}, suggest the best strategy to handle missing values (drop, mean, median, mode) and explain why. Return a JSON object with 'strategy' and 'reason'."
        )
        self.category_prompt = PromptTemplate(
            input_variables=["column", "values"],
            template="Identify inconsistencies in these category values for column '{column}': {values}. Suggest standardized versions. Return a JSON object mapping original to standardized values."
        )

    def suggest_column_names(self, df: pd.DataFrame) -> dict:
        """Suggest standardized column names using GPT-3.5."""
        columns = df.columns.tolist()
        sample_data = df.head(3).to_dict()
        chain = LLMChain(llm=self.llm, prompt=self.column_name_prompt)
        try:
            response = chain.run(columns=columns, sample_data=sample_data)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in suggest_column_names: {e}")
            return {}

    def suggest_missing_value_strategy(self, df: pd.DataFrame, column: str) -> dict:
        """Suggest strategy for handling missing values."""
        stats = {
            "null_count": int(df[column].isna().sum()),
            "dtype": str(df[column].dtype),
            "sample_values": df[column].dropna().head(3).tolist()
        }
        chain = LLMChain(llm=self.llm, prompt=self.missing_value_prompt)
        try:
            response = chain.run(column=column, stats=stats)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in suggest_missing_value_strategy: {e}")
            return {"strategy": "auto", "reason": "Default to auto due to error"}

    def detect_inconsistent_categories(self, df: pd.DataFrame, column: str) -> dict:
        """Identify and suggest fixes for inconsistent categories."""
        if column not in df.columns or df[column].dtype != 'object':
            return {}
        values = df[column].dropna().unique().tolist()
        chain = LLMChain(llm=self.llm, prompt=self.category_prompt)
        try:
            response = chain.run(column=column, values=values)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in detect_inconsistent_categories: {e}")
            return {}