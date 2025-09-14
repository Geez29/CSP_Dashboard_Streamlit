import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")
st.title("CSP Dashboard")

# ------------------ Load Excel ------------------
file_path = "Cloud_Actual_Optimization Data.xlsx"

xls = pd.ExcelFile(file_path)

# Sheet 1: Monthly CSP Spend (for line chart)
df_line = pd.read_excel(xls, sheet_name=0)
df_line["Month"] = pd.to_datetime(df_line["Month"]).dt.strftime("%Y-%m")

# Fiscal Year Calculation
def assign_fy(date_str):
    year, month = map(int, date_str.split("-"))
    return f"FY{year+1}" if month >= 4 else f"FY{year}"

if "FY" not in df_line.columns:
    df_line["FY"] = df_line["Month"].apply(assign_fy)

# FY Filter
fy_options = sorted(df_line["FY"].unique())
selected_fy = st.selectbox("Select Fiscal Year (FY):", fy_options)
filtered_df = df_line[df_line["FY"] == selected_fy]

# ------------------ Line Chart ------------------
max_cost = filtered_df["Cost"].max()

fig_line = px.line(
    filtered_df,
    x="Month",
    y="Cost",
    color="CSP",
    markers=True,
    hover_data=["FY"]
)

# Add top-centered title
fig_line.add_annotation(
    x=filtered_df["Month"].iloc[len(filtered_df)//2],
    y=max_cost * 1.05,
    text="CSP Monthly Cost AWS vs Azure",
    showarrow=False,
    font=dict(size=18),
    xanchor="center"
)

# Enable vertical hover line
fig_line.update_layout(
    hovermode="x unified",
    xaxis=dict(
        showspikes=True,
        spikecolor="gray",
        spikethickness=1,
        spikemode="across"
    ),
    yaxis=dict(
        showspikes=True,
        spikecolor="gray",
        spikethickness=1,
        spikemode="across"
    ),
    margin=dict(t=100)
)

st.plotly_chart(fig_line, use_container_width=True)

# ------------------ Waterfall Data ------------------
# Single sheet with Services + Marketplace table
df_waterfall = pd.read_excel(xls, sheet_name=1)
df_waterfall.columns = df_waterfall.columns.str.strip()

# Quarters to include
valid_quarters = [
    "FY24 Q1","FY24 Q2","FY24 Q3","FY24 Q4",
    "FY25 Q1","FY25 Q2","FY25 Q3","FY25 Q4",
    "FY26 Q1","FY26 Q2"
]

# Extract Services
services_data = df_waterfall[['Services', df_waterfall.columns[1]]].dropna()
services_data.columns = ['Quarter', 'Spend']
services_data = services_data[services_data['Quarter'].isin(valid_quarters)]

# Extract Marketplace
marketplace_data = df_waterfall[['Marketplace', df_waterfall.columns[3]]].dropna()
marketplace_data.columns = ['Quarter', 'Spend']
marketplace_data = marketplace_data[marketplace_data['Quarter'].isin(valid_quarters)]

# ------------------ Waterfall Charts ------------------
# Services
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

# Marketplace
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

# ------------------ Layout ------------------
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_services, use_container_width=True)
with col2:
    st.plotly_chart(fig_marketplace, use_container_width=True)
