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


from sales_data import compute_total_orders, compute_total_sales


def _kpi_sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-03", "2024-01-04", "2024-02-01"]),
        "order_id": ["ORD-001", "ORD-002", "ORD-002"],
        "category": ["Audio", "Accessories", "Accessories"],
        "region": ["North", "South", "South"],
        "total_amount": [159.98, 74.97, 24.99],
    })


def test_compute_total_sales_sums_total_amount():
    df = _kpi_sample_df()

    assert compute_total_sales(df) == 259.94


def test_compute_total_orders_counts_unique_order_ids():
    df = _kpi_sample_df()  # ORD-002 appears twice

    assert compute_total_orders(df) == 2


from sales_data import compute_monthly_trend


def test_compute_monthly_trend_groups_and_sorts_chronologically():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-02-01", "2024-01-03", "2024-01-04"]),
        "total_amount": [100.0, 50.0, 25.0],
    })

    trend = compute_monthly_trend(df)

    assert trend["month"].astype(str).tolist() == ["2024-01", "2024-02"]
    assert trend["total_sales"].tolist() == [75.0, 100.0]


from sales_data import compute_sales_by_category, compute_sales_by_region


def _breakdown_sample_df():
    return pd.DataFrame({
        "category": ["Audio", "Accessories", "Audio"],
        "region": ["North", "South", "South"],
        "total_amount": [100.0, 30.0, 50.0],
    })


def test_compute_sales_by_category_sums_and_sorts_descending():
    df = _breakdown_sample_df()

    result = compute_sales_by_category(df)

    assert result["category"].tolist() == ["Audio", "Accessories"]
    assert result["total_sales"].tolist() == [150.0, 30.0]


def test_compute_sales_by_region_sums_and_sorts_descending():
    df = _breakdown_sample_df()

    result = compute_sales_by_region(df)

    assert result["region"].tolist() == ["North", "South"]
    assert result["total_sales"].tolist() == [100.0, 80.0]
