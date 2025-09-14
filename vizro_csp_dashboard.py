# vizro_csp_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ Load Data ------------------
file_path = "Cloud_Actual_Optimization Data.xlsx"

# Load Excel with two side-by-side tables (Services, Marketplace)
df_raw = pd.read_excel(file_path, header=0)

# Split Services (first 2 columns) & Marketplace (next 2 columns)
df_services = df_raw.iloc[:, 0:2].dropna()
df_marketplace = df_raw.iloc[:, 2:4].dropna()
df_services.columns = ["Category", "Cost"]
df_marketplace.columns = ["Category", "Cost"]

# Load CSP Monthly Cost file (separate Excel you had earlier)
df_line = pd.read_excel("CSP_Monthly_Cost_Sample Data.xlsx")
df_line["Month"] = pd.to_datetime(df_line["Month"]).dt.strftime("%Y-%m")

# Add Fiscal Year
def assign_fy(date_str):
    year, month = map(int, date_str.split("-"))
    return f"FY{year+1}" if month >= 4 else f"FY{year}"

if "FY" not in df_line.columns:
    df_line["FY"] = df_line["Month"].apply(assign_fy)

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")

# Flex logo top-left
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("flex_logo.png", width=120)
with col_title:
    st.title("CSP Dashboard")

# ------------------ FY Filter ------------------
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

# Add top-centered annotation title
fig_line.add_annotation(
    x=filtered_df["Month"].iloc[len(filtered_df)//2],
    y=max_cost * 1.05,
    text="CSP Monthly Cost (AWS vs Azure)",
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
        spikedash="dot",
        spikemode="across"
    ),
    yaxis=dict(
        showspikes=True,
        spikecolor="gray",
        spikethickness=1,
        spikedash="dot",
        spikemode="across"
    ),
    margin=dict(t=100)
)

st.plotly_chart(fig_line, use_container_width=True)

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

# ------------------ Display both Waterfalls side by side ------------------
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_services, use_container_width=True)
with col2:
    st.plotly_chart(fig_marketplace, use_container_width=True)
