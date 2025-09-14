import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- Streamlit Page Config ----------------
st.set_page_config(page_title="CSP Monthly Cost Dashboard", layout="wide")

# ---------------- Load Data ----------------
df = pd.read_excel("CSP_Monthly_Cost_Sample Data.xlsx")

# Ensure Month column is YYYY-MM
df["Month"] = pd.to_datetime(df["Month"]).dt.strftime("%Y-%m")

# Fiscal Year calculation
def assign_fy(date_str):
    year, month = map(int, date_str.split("-"))
    return f"FY{year+1}" if month >= 4 else f"FY{year}"

if "FY" not in df.columns:
    df["FY"] = df["Month"].apply(assign_fy)

# ---------------- Sidebar Filter ----------------
fy_options = sorted(df["FY"].unique())
selected_fy = st.sidebar.multiselect("Select Fiscal Year(s):", fy_options, default=fy_options)

# Filter data
filtered_df = df[df["FY"].isin(selected_fy)]

# ---------------- Chart ----------------
max_cost = filtered_df["Cost"].max()

fig = px.line(
    filtered_df,
    x="Month",
    y="Cost",
    color="CSP",
    markers=True,
    hover_data=["FY"]
)

# Add custom title annotation
fig.add_annotation(
    x=filtered_df["Month"].iloc[len(filtered_df)//2],
    y=max_cost * 1.05,
    text="CSP Monthly Cost (AWS vs Azure)",
    showarrow=False,
    font=dict(size=18),
    xanchor="center"
)

# Enable vertical hover line
fig.update_layout(
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
    margin=dict(t=80)
)

# ---------------- Streamlit Display ----------------
st.plotly_chart(fig, use_container_width=True)
