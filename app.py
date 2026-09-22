import plotly.express as px
import streamlit as st

from sales_data import (
    SalesDataError,
    compute_monthly_trend,
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

trend = compute_monthly_trend(df)
trend["month_label"] = trend["month"].astype(str)

st.subheader("Sales Trend")
trend_fig = px.line(trend, x="month_label", y="total_sales", markers=True)
trend_fig.update_traces(
    line_color="#2a78d6",
    hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
)
trend_fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
st.plotly_chart(trend_fig, use_container_width=True)
