# vizro_csp_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------ Streamlit Page Config ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")

# ------------------ Logo ------------------
col1, col2 = st.columns([1, 8])
with col1:
    st.image("flex_logo.png", width=120)
with col2:
    st.title("CSP Dashboard")

# ------------------ Load Excel file ------------------
file_path = "Cloud_Actual_Optimization Data.xlsx"
xls = pd.ExcelFile(file_path)

# Assume sheet names are "Services" and "Marketplace"
df_services = pd.read_excel(xls, sheet_name="Services")
df_marketplace = pd.read_excel(xls, sheet_name="Marketplace")

# ------------------ Data Preprocessing ------------------
# For line chart we assume "Month", "CSP", "Cost"
# You can merge both tables if needed, here only Services is used for line
if "Month" in df_services.columns:
    df_services["Month"] = pd.to_datetime(df_services["Month"]).dt.strftime("%Y-%m")

    def assign_fy(date_str):
        year, month = map(int, date_str.split("-"))
        return f"FY{year+1}" if month >= 4 else f"FY{year}"

    if "FY" not in df_services.columns:
        df_services["FY"] = df_services["Month"].apply(assign_fy)

# ------------------ Filters ------------------
fy_options = sorted(df_services["FY"].unique())
selected_fy = st.selectbox("Select Fiscal Year (FY):", fy_options)

filtered_df = df_services[df_services["FY"] == selected_fy]

# ------------------ Line Chart ------------------
fig_line = px.line(
    filtered_df,
    x="Month",
    y="Cost",
    color="CSP",
    markers=True,
    hover_data=["FY"]
)

fig_line.add_annotation(
    x=filtered_df["Month"].iloc[len(filtered_df)//2],
    y=filtered_df["Cost"].max() * 1.05,
    text="CSP Monthly Cost (AWS vs Azure)",
    showarrow=False,
    font=dict(size=18),
    xanchor="center"
)

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

# ------------------ Waterfall Chart Function ------------------
def create_waterfall(df, title, color):
    fig = go.Figure(go.Waterfall(
        x=df.iloc[:, 0],  # first column (e.g. Service / Category)
        y=df.iloc[:, 1],  # second column (e.g. Cost / Value)
        measure=["relative"] * (len(df) - 1) + ["total"],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": color}},
        decreasing={"marker": {"color": color}},
        totals={"marker": {"color": "darkblue"}}
    ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=18)),
        waterfallgap=0.3
    )
    return fig

# Create waterfall charts
fig_services = create_waterfall(df_services, "CSP Services Spend", "royalblue")
fig_marketplace = create_waterfall(df_marketplace, "CSP Marketplace Spend", "deepskyblue")

# ------------------ Layout ------------------
st.plotly_chart(fig_line, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_services, use_container_width=True)
with col2:
    st.plotly_chart(fig_marketplace, use_container_width=True)
