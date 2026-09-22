import streamlit as st

from sales_data import (
    SalesDataError,
    compute_total_orders,
    compute_total_sales,
    load_sales_data,
)

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

try:
    df = load_sales_data("data/sales-data.csv")
except SalesDataError as e:
    st.error(str(e))
    st.stop()

total_sales = compute_total_sales(df)
total_orders = compute_total_orders(df)

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
