# streamlit_csp_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ Load Excel file ------------------
@st.cache_data
def load_data():
    df = pd.read_excel("CSP_Monthly_Cost_Sample Data.xlsx")
    # Ensure Month column is in YYYY-MM format
    df["Month"] = pd.to_datetime(df["Month"]).dt.strftime("%Y-%m")

    # Calculate Fiscal Year if not present
    def assign_fy(date_str):
        year, month = map(int, date_str.split("-"))
        return f"FY{year+1}" if month >= 4 else f"FY{year}"

    if "FY" not in df.columns:
        df["FY"] = df["Month"].apply(assign_fy)

    return df

df = load_data()

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")

# App Title
st.markdown("<h2 style='text-align: center;'>CSP Monthly Cost Dashboard</h2>", unsafe_allow_html=True)

# FY Filter
fy_options = sorted(df["FY"].unique())
selected_fy = st.selectbox("Select Fiscal Year (FY):", fy_options)

# Filter data
filtered_df = df[df["FY"] == selected_fy]

# ------------------ Line Chart ------------------
if not filtered_df.empty:
    max_cost = filtered_df["Cost"].max()

    fig = px.line(
        filtered_df,
        x="Month",
        y="Cost",
        color="CSP",
        markers=True,
        hover_data=["FY"]
    )

    # Add top-centered annotation title inside chart
    fig.add_annotation(
        x=filtered_df["Month"].iloc[len(filtered_df) // 2],
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
        margin=dict(t=100)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected Fiscal Year.")
