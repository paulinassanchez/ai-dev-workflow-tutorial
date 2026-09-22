"""Data loading and calculation functions for the sales dashboard."""

import pandas as pd

REQUIRED_COLUMNS = [
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
]


class SalesDataError(Exception):
    """Raised when the sales CSV is missing or malformed."""


def load_sales_data(csv_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise SalesDataError(f"Sales data file not found: {csv_path}") from exc

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise SalesDataError(
            f"Sales data is missing required columns: {', '.join(missing)}"
        )

    try:
        df["date"] = pd.to_datetime(df["date"])
        df["quantity"] = pd.to_numeric(df["quantity"])
        df["unit_price"] = pd.to_numeric(df["unit_price"])
        df["total_amount"] = pd.to_numeric(df["total_amount"])
    except (ValueError, TypeError) as exc:
        raise SalesDataError(
            f"Sales data contains values that could not be parsed: {exc}"
        ) from exc

    return df


def compute_total_sales(df: pd.DataFrame) -> float:
    return float(df["total_amount"].sum())


def compute_total_orders(df: pd.DataFrame) -> int:
    return int(df["order_id"].nunique())
