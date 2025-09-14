import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ------------------ Load Excel file ------------------
file_path = "Cloud_Actual_Optimization Data.xlsx"

# Read full sheet without headers (first row is the table header)
df_raw = pd.read_excel(file_path, header=0)

# Split into two DataFrames
df_services = df_raw.iloc[:, 0:2].dropna()      # First 2 columns
df_marketplace = df_raw.iloc[:, 2:4].dropna()   # Next 2 columns

df_services.columns = ["Category", "Cost"]
df_marketplace.columns = ["Category", "Cost"]

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")

st.title("CSP Dashboard")

# ------------------ Line Chart (dummy for now, if needed keep from before) ------------------
# You can re-use your CSP monthly cost line chart logic here if it comes from another Excel.

# ------------------ Waterfall 1: Services ------------------
fig_services = go.Figure(go.Waterfall(
    x=df_services["Category"],
    y=df_services["Cost"],
    textposition="outside",
    connector=dict(line=dict(color="blue")),
    increasing=dict(marker=dict(color="#1f77b4")),  # McKinsey Blue
    decreasing=dict(marker=dict(color="#1f77b4")),
    totals=dict(marker=dict(color="#1f77b4"))
))
fig_services.update_layout(title="CSP Services Spend")

# ------------------ Waterfall 2: Marketplace ------------------
fig_marketplace = go.Figure(go.Waterfall(
    x=df_marketplace["Category"],
    y=df_marketplace["Cost"],
    textposition="outside",
    connector=dict(line=dict(color="darkblue")),
    increasing=dict(marker=dict(color="#005eb8")),  # Different Blue
    decreasing=dict(marker=dict(color="#005eb8")),
    totals=dict(marker=dict(color="#005eb8"))
))
fig_marketplace.update_layout(title="CSP Marketplace Spend")

# ------------------ Display charts ------------------
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_services, use_container_width=True)
with col2:
    st.plotly_chart(fig_marketplace, use_container_width=True)
