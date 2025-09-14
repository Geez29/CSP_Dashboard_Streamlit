import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="CSP Dashboard", layout="wide")
st.title("CSP Services & Marketplace Spend Dashboard")

# 🔹 Hardcoded Excel file name (must exist in repo!)
file_path = "cloud_spend.xlsx"

# Load Excel (first sheet only, since Services & Marketplace are in same sheet)
data = pd.ExcelFile(file_path).parse(0)
data.columns = data.columns.str.strip()

# Quarters to keep
valid_quarters = [
    "FY24 Q1", "FY24 Q2", "FY24 Q3", "FY24 Q4",
    "FY25 Q1", "FY25 Q2", "FY25 Q3", "FY25 Q4",
    "FY26 Q1", "FY26 Q2"
]

# Extract Services
services_data = data[['Services', data.columns[1]]].dropna()
services_data.columns = ['Quarter', 'Spend']
services_data = services_data[services_data['Quarter'].isin(valid_quarters)]

# Extract Marketplace
marketplace_data = data[['Marketplace', data.columns[3]]].dropna()
marketplace_data.columns = ['Quarter', 'Spend']
marketplace_data = marketplace_data[marketplace_data['Quarter'].isin(valid_quarters)]

# Services Waterfall
fig_services = go.Figure(go.Waterfall(
    name="Services Spend",
    orientation="v",
    x=services_data['Quarter'],
    y=services_data['Spend'],
    text=services_data['Spend'],
    textposition="outside",
    connector={"line": {"color": "blue"}},
    decreasing={"marker": {"color": "rgb(0, 112, 192)"}},
    increasing={"marker": {"color": "rgb(91, 155, 213)"}},
    totals={"marker": {"color": "rgb(37, 64, 97)"}}
))
fig_services.update_layout(title="CSP Services Spend", yaxis_title="Spend ($)")

# Marketplace Waterfall
fig_marketplace = go.Figure(go.Waterfall(
    name="Marketplace Spend",
    orientation="v",
    x=marketplace_data['Quarter'],
    y=marketplace_data['Spend'],
    text=marketplace_data['Spend'],
    textposition="outside",
    connector={"line": {"color": "darkblue"}},
    decreasing={"marker": {"color": "rgb(0, 32, 96)"}},
    increasing={"marker": {"color": "rgb(0, 176, 240)"}},
    totals={"marker": {"color": "rgb(31, 78, 121)"}}
))
fig_marketplace.update_layout(title="CSP Marketplace Spend", yaxis_title="Spend ($)")

# Layout
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_services, use_container_width=True)
with col2:
    st.plotly_chart(fig_marketplace, use_container_width=True)
