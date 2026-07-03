"""Reusable analysis functions for the Sprocket Central customer analytics project."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

SHEETS = {
    "transactions": "Transactions",
    "new_customers": "NewCustomerList",
    "customer_demographic": "CustomerDemographic",
    "customer_address": "CustomerAddress",
}

STATE_MAP = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "QLD": "QLD",
    "NSW": "NSW",
    "VIC": "VIC",
}

GENDER_MAP = {
    "F": "Female",
    "Femal": "Female",
    "Female": "Female",
    "M": "Male",
    "Male": "Male",
    "U": "Undisclosed",
}


def load_workbook_sheets(workbook_path: str | Path) -> Dict[str, pd.DataFrame]:
    """Load the four analysis sheets from the Excel workbook."""
    workbook_path = Path(workbook_path)
    if not workbook_path.exists():
        raise FileNotFoundError(
            f"Could not find {workbook_path}. Copy the Excel workbook into data/raw/ first."
        )

    return {
        key: pd.read_excel(workbook_path, sheet_name=sheet_name)
        for key, sheet_name in SHEETS.items()
    }


def _clean_gender(series: pd.Series) -> pd.Series:
    """Standardise gender categories used across the workbook."""
    return series.replace(GENDER_MAP).fillna("Unknown")


def _clean_state(series: pd.Series) -> pd.Series:
    """Standardise Australian state labels."""
    return series.replace(STATE_MAP).fillna("Unknown")


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean transaction data and create a profit field."""
    cleaned = df.copy()
    cleaned["profit"] = cleaned["list_price"] - cleaned["standard_cost"]
    cleaned["order_status"] = cleaned["order_status"].fillna("Unknown")
    cleaned["brand"] = cleaned["brand"].fillna("Unknown")
    cleaned["product_size"] = cleaned["product_size"].fillna("Unknown")
    cleaned["online_order"] = cleaned["online_order"].map({1.0: "Online", 0.0: "Offline"}).fillna("Unknown")
    return cleaned


def clean_new_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the new-customer prospect list."""
    cleaned = df.copy()
    cleaned["gender"] = _clean_gender(cleaned["gender"])
    cleaned["state"] = _clean_state(cleaned["state"])

    # Rename unnamed model-score columns to something readable rather than leaving them as Unnamed: 16, etc.
    score_columns = [col for col in cleaned.columns if str(col).startswith("Unnamed")]
    rename_map = {col: f"score_component_{i+1}" for i, col in enumerate(score_columns)}
    cleaned = cleaned.rename(columns=rename_map)
    return cleaned


def clean_customer_demographic(df: pd.DataFrame) -> pd.DataFrame:
    """Clean demographic records for existing customers."""
    cleaned = df.copy()
    cleaned["gender"] = _clean_gender(cleaned["gender"])

    # The original `default` column contains inconsistent placeholder/test values and is not used in this analysis.
    if "default" in cleaned.columns:
        cleaned = cleaned.drop(columns=["default"])
    return cleaned


def clean_customer_address(df: pd.DataFrame) -> pd.DataFrame:
    """Clean customer address data."""
    cleaned = df.copy()
    cleaned["state"] = _clean_state(cleaned["state"])
    return cleaned


def build_summary_tables(
    transactions: pd.DataFrame,
    new_customers: pd.DataFrame,
    customer_demographic: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """Create summary tables used by the notebook, README, and saved outputs."""
    order_status_summary = (
        transactions["order_status"]
        .value_counts()
        .rename_axis("order_status")
        .reset_index(name="transaction_count")
    )
    order_status_summary["percentage"] = (
        order_status_summary["transaction_count"] / order_status_summary["transaction_count"].sum() * 100
    ).round(2)

    brand_profit_summary = (
        transactions.groupby("brand", dropna=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_profit=("profit", lambda values: values.sum(min_count=1)),
            average_profit=("profit", "mean"),
        )
        .sort_values("total_profit", ascending=False)
        .round(2)
        .reset_index()
    )

    new_customer_state_summary = (
        new_customers.groupby("state")
        .agg(
            customer_count=("first_name", "count"),
            total_recent_bike_purchases=("past_3_years_bike_related_purchases", "sum"),
            avg_recent_bike_purchases=("past_3_years_bike_related_purchases", "mean"),
        )
        .sort_values("total_recent_bike_purchases", ascending=False)
        .round(2)
        .reset_index()
    )

    gender_wealth_summary = (
        customer_demographic.groupby(["gender", "wealth_segment"])
        .size()
        .reset_index(name="customer_count")
        .sort_values(["gender", "customer_count"], ascending=[True, False])
    )

    return {
        "order_status_summary": order_status_summary,
        "brand_profit_summary": brand_profit_summary,
        "new_customer_state_summary": new_customer_state_summary,
        "gender_wealth_summary": gender_wealth_summary,
    }


def save_summary_tables(summary_tables: Dict[str, pd.DataFrame], output_dir: str | Path) -> None:
    """Save summary tables as CSV files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, table in summary_tables.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)


def create_visualisations(
    transactions: pd.DataFrame,
    new_customers: pd.DataFrame,
    customer_demographic: pd.DataFrame,
    output_dir: str | Path,
) -> None:
    """Create and save the project visualisations."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 5))
    transactions["order_status"].value_counts().plot(kind="bar")
    plt.title("Transaction order status distribution")
    plt.xlabel("Order status")
    plt.ylabel("Number of transactions")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "order_status_distribution.png", dpi=150)
    plt.close()

    brand_size_table = pd.crosstab(transactions["brand"], transactions["product_size"])
    brand_size_table = brand_size_table.loc[transactions["brand"].value_counts().index]
    brand_size_table.plot(kind="bar", figsize=(12, 6))
    plt.title("Transactions by brand and product size")
    plt.xlabel("Brand")
    plt.ylabel("Number of transactions")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "brand_by_product_size.png", dpi=150)
    plt.close()

    state_summary = (
        new_customers.groupby("state")["past_3_years_bike_related_purchases"]
        .sum()
        .sort_values(ascending=False)
    )
    state_summary.plot(kind="bar", figsize=(9, 5))
    plt.title("New-customer bike purchases by state")
    plt.xlabel("State")
    plt.ylabel("Bike-related purchases in the past 3 years")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "new_customer_purchases_by_state.png", dpi=150)
    plt.close()

    gender_wealth_table = pd.crosstab(customer_demographic["gender"], customer_demographic["wealth_segment"])
    gender_wealth_table.plot(kind="bar", figsize=(10, 6))
    plt.title("Existing customers by gender and wealth segment")
    plt.xlabel("Gender")
    plt.ylabel("Number of customers")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / "gender_by_wealth_segment.png", dpi=150)
    plt.close()


def run_analysis(project_root: str | Path = ".") -> Dict[str, pd.DataFrame]:
    """Run the full analysis pipeline from the project root."""
    project_root = Path(project_root)
    workbook_path = project_root / "data" / "raw" / "Mentor_KPMG_Sprocket_Project_Dataset.xlsx"

    sheets = load_workbook_sheets(workbook_path)
    transactions = clean_transactions(sheets["transactions"])
    new_customers = clean_new_customers(sheets["new_customers"])
    customer_demographic = clean_customer_demographic(sheets["customer_demographic"])
    customer_address = clean_customer_address(sheets["customer_address"])

    summary_tables = build_summary_tables(transactions, new_customers, customer_demographic)
    save_summary_tables(summary_tables, project_root / "reports" / "tables")
    create_visualisations(
        transactions,
        new_customers,
        customer_demographic,
        project_root / "reports" / "figures",
    )

    # Save cleaned datasets that are safe for local analysis. They are not ignored by default because they are derived outputs.
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    transactions.to_csv(processed_dir / "transactions_cleaned.csv", index=False)
    new_customers.to_csv(processed_dir / "new_customers_cleaned.csv", index=False)
    customer_demographic.to_csv(processed_dir / "customer_demographic_cleaned.csv", index=False)
    customer_address.to_csv(processed_dir / "customer_address_cleaned.csv", index=False)

    return summary_tables


if __name__ == "__main__":
    run_analysis(Path(__file__).resolve().parents[1])
