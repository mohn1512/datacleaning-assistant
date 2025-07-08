from ydata_profiling import ProfileReport
import pandas as pd
from pathlib import Path
from loguru import logger

class ReportGenerator:
    def __init__(self):
        pass

    def generate_profiling_report(self, df: pd.DataFrame) -> dict:
        """Generate data profiling report using YData Profiling."""
        try:
            profile = ProfileReport(df, title="Data Profiling Report", explorative=True)
            report = profile.to_notebook_iframe()
            logger.info("Generated data profiling report")
            return {"report": report, "stats": df.describe().to_dict()}
        except Exception as e:
            logger.error(f"Error generating profiling report: {e}")
            return {}

    def generate_cleaning_summary(self, actions: list) -> str:
        """Generate a Markdown summary of cleaning actions."""
        summary = "# Data Cleaning Summary\n\n"
        summary += "## Cleaning Actions\n"
        for action in actions:
            summary += f"- {action}\n"
        logger.info("Generated cleaning summary")
        return summary

    def save_report(self, content: str, output_path: str, format: str = 'markdown'):
        """Save report as Markdown or PDF."""
        output_path = Path(output_path)
        if format == 'markdown':
            with open(output_path, 'w') as f:
                f.write(content)
        elif format == 'pdf':
            # Requires pandoc installation
            import pypandoc
            pypandoc.convert_text(content, 'pdf', format='md', outputfile=str(output_path))
        logger.info(f"Saved report to {output_path}")