"""Command-line entry point for the Sprocket Central customer analytics project."""

from pathlib import Path

from src.kpmg_sprocket_analysis import run_analysis


if __name__ == "__main__":
    tables = run_analysis(Path(__file__).resolve().parent)
    print("Analysis complete. Generated summary tables:")
    for table_name, table in tables.items():
        print(f"- {table_name}: {table.shape[0]} rows x {table.shape[1]} columns")
