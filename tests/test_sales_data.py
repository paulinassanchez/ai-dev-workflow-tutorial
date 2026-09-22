import pandas as pd
import pytest

from sales_data import SalesDataError, load_sales_data

VALID_COLUMNS = [
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
]


def _write_csv(tmp_path, rows, columns):
    path = tmp_path / "sales.csv"
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False)
    return str(path)


def test_load_sales_data_returns_dataframe_with_parsed_types(tmp_path):
    rows = [
        ["2024-01-03", "ORD-001", "Wireless Earbuds", "Audio", "North", 2, 79.99, 159.98],
        ["2024-02-04", "ORD-002", "Phone Case", "Accessories", "South", 3, 24.99, 74.97],
    ]
    path = _write_csv(tmp_path, rows, VALID_COLUMNS)

    df = load_sales_data(path)

    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df["total_amount"].tolist() == [159.98, 74.97]


def test_load_sales_data_missing_file_raises_sales_data_error(tmp_path):
    missing_path = str(tmp_path / "does-not-exist.csv")

    with pytest.raises(SalesDataError, match="not found"):
        load_sales_data(missing_path)


def test_load_sales_data_missing_column_raises_sales_data_error(tmp_path):
    rows = [["2024-01-03", "ORD-001", "Wireless Earbuds", "Audio", "North", 2, 79.99]]
    columns = VALID_COLUMNS[:-1]  # drop total_amount
    path = _write_csv(tmp_path, rows, columns)

    with pytest.raises(SalesDataError, match="missing required columns"):
        load_sales_data(path)
