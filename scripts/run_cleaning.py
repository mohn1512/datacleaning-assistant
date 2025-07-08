import argparse
from src.cli import run_cli

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Data Cleaning Tool")
    parser.add_argument("--input", required=True, help="Input file path (CSV/Excel)")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--format", choices=["csv", "excel"], default="csv", help="Output format")
    parser.add_argument("--config", default="config/settings.yaml", help="Config file path")
    args = parser.parse_args()
    run_cli(args.input, args.output, args.format, args.config)