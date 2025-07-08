from src.data_loader import DataLoader
from src.data_cleaner import DataCleaner
from src.llm_processor import LLMProcessor
from src.report_generator import ReportGenerator
import yaml
from pathlib import Path
from loguru import logger

def run_cli(input_path: str, output_path: str, output_format: str, config_path: str = "config/settings.yaml"):
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        loader = DataLoader()
        cleaner = DataCleaner(
            nullity_threshold=config.get('nullity_threshold', 0.8),
            outlier_method=config.get('outlier_method', 'iqr'),
            outlier_action=config.get('outlier_action', 'cap'),
            fuzzy_threshold=config.get('fuzzy_threshold', 90),
            scale_numeric=config.get('scale_numeric', False),
            scale_method=config.get('scale_method', 'minmax')
        )
        llm_processor = LLMProcessor(api_key=config.get('openai_api_key', ''))
        report_generator = ReportGenerator()

        df = loader.load_file(input_path)
        
        # Apply LLM suggestions
        col_suggestions = llm_processor.suggest_column_names(df)
        if col_suggestions:
            df.rename(columns=col_suggestions, inplace=True)
            logger.info(f"Renamed columns: {col_suggestions}")
        
        for col in df.columns:
            missing_strategy = llm_processor.suggest_missing_value_strategy(df, col)
            df = cleaner.handle_missing_values(df, strategy=missing_strategy.get('strategy', 'auto'))
            if df[col].dtype == 'object':
                category_fixes = llm_processor.detect_inconsistent_categories(df, col)
                if category_fixes:
                    df[col] = df[col].map(category_fixes).fillna(df[col])
                    logger.info(f"Fixed categories in {col}: {category_fixes}")

        df = cleaner.clean(df)
        cleaner.save_output(df, output_path, output_format)

        summary = report_generator.generate_cleaning_summary(cleaner.actions)
        report_path = Path(output_path).with_suffix('.md')
        report_generator.save_report(summary, report_path, 'markdown')

        profiling_report = report_generator.generate_profiling_report(df)
        logger.info("CLI cleaning process completed")
    except Exception as e:
        logger.error(f"CLI error: {e}")
        raise