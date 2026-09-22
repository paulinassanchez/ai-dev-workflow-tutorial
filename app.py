import streamlit as st

from sales_data import SalesDataError, load_sales_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

try:
    df = load_sales_data("data/sales-data.csv")
except SalesDataError as e:
    st.error(str(e))
    st.stop()
