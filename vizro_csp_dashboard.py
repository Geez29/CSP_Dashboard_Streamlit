import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="CSP Dashboard", layout="wide")
st.title("CSP Services & Marketplace Spend Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read Excel
    data = pd.ExcelFile(uploaded_file).parse(0)
    data.columns = data.columns.str.strip()

    # Valid quarters up to FY26 Q2
    valid_quarters = [
        "FY24 Q1", "FY24 Q2", "FY24 Q3", "FY24 Q4",
        "FY25 Q1", "FY25 Q2", "FY25 Q3", "FY25 Q4",
        "FY26 Q1", "FY26 Q2"
    ]

    # Extract Services data
    services_data = data[['Services', 'Unnamed: 1']].dropna()
    services_data.columns = ['Quarter', 'Spend']
    services_data = services_data[services_data['Quarter'].isin(valid_quarters)]

    # Extract Marketplace data
    marketplace_data = data[['Marketplace', 'Unnamed: 3']].dropna()
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
        connector={"line": {"color": "blue"}}
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
        connector={"line": {"color": "brown"}}
    ))
    fig_marketplace.update_layout(title="CSP Marketplace Spend", yaxis_title="Spend ($)")

    # Layout in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_services, use_container_width=True)
    with col2:
        st.plotly_chart(fig_marketplace, use_container_width=True)

else:
    st.info("👆 Please upload an Excel file to see the dashboard")
