import plotly.express as px
import streamlit as st

from sales_data import (
    SalesDataError,
    compute_monthly_trend,
    compute_sales_by_category,
    compute_sales_by_region,
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
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Orders", f"{total_orders:,}")

trend = compute_monthly_trend(df)
trend["month_label"] = trend["month"].dt.strftime("%b %Y")

st.subheader("Sales Trend")
trend_fig = px.line(trend, x="month_label", y="total_sales", markers=True)
trend_fig.update_traces(
    line_color="#2a78d6",
    hovertemplate="%{x}: $%{y:,.2f}<extra></extra>",
)
trend_fig.update_layout(xaxis_title="Month", yaxis_title="Sales ($)")
trend_fig.update_xaxes(tickvals=trend["month_label"][::2])
st.plotly_chart(trend_fig, use_container_width=True)

by_category = compute_sales_by_category(df)
by_region = compute_sales_by_region(df)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Sales by Category")
    category_fig = px.bar(by_category, x="total_sales", y="category", orientation="h")
    category_fig.update_traces(
        marker_color="#2a78d6",
        hovertemplate="%{y}: $%{x:,.2f}<extra></extra>",
    )
    category_fig.update_layout(xaxis_title="Sales ($)", yaxis_title="Category")
    category_fig.update_yaxes(autorange="reversed")
    st.plotly_chart(category_fig, use_container_width=True)

with col4:
    st.subheader("Sales by Region")
    region_fig = px.bar(by_region, x="total_sales", y="region", orientation="h")
    region_fig.update_traces(
        marker_color="#2a78d6",
        hovertemplate="%{y}: $%{x:,.2f}<extra></extra>",
    )
    region_fig.update_layout(xaxis_title="Sales ($)", yaxis_title="Region")
    region_fig.update_yaxes(autorange="reversed")
    st.plotly_chart(region_fig, use_container_width=True)
