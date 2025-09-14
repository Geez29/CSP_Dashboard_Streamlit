import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")
st.title("CSP Dashboard")

# ------------------ Load Excel ------------------
file_path = "Cloud_Actual_Optimization Data.xlsx"

try:
    # Load the waterfall data (this appears to be your main sheet)
    df_waterfall = pd.read_excel(file_path, sheet_name=0)
    st.success("✅ Excel file loaded successfully")
    
    # Clean up the data based on your screenshot
    # The data appears to have Services and Marketplace sections side by side
    
    # Extract Services data (left side)
    services_data = []
    for i, row in df_waterfall.iterrows():
        if pd.notna(row.iloc[0]) and str(row.iloc[0]).startswith('FY'):  # Quarter column
            quarter = row.iloc[0]
            
            # Get the spend values (positive and negative)
            if pd.notna(row.iloc[2]):  # Assuming spend is in 3rd column after removing $
                spend_str = str(row.iloc[2]).replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                try:
                    spend = float(spend_str)
                    services_data.append({'Quarter': quarter, 'Spend': spend})
                except:
                    pass
    
    services_df = pd.DataFrame(services_data)
    
    # Extract Marketplace data (right side)
    marketplace_data = []
    # Look for Marketplace data starting from column index around 4-6
    for i, row in df_waterfall.iterrows():
        if pd.notna(row.iloc[4]) and str(row.iloc[4]).startswith('FY'):  # Marketplace quarter column
            quarter = row.iloc[4]
            
            # Get the spend values
            if pd.notna(row.iloc[6]):  # Assuming marketplace spend is in 7th column
                spend_str = str(row.iloc[6]).replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                try:
                    spend = float(spend_str)
                    if spend != 0:  # Only add non-zero values
                        marketplace_data.append({'Quarter': quarter, 'Spend': spend})
                except:
                    pass
    
    marketplace_df = pd.DataFrame(marketplace_data)
    
    # If the above extraction doesn't work, let's try a different approach
    if services_df.empty or marketplace_df.empty:
        st.warning("Trying alternative data extraction method...")
        
        # Method 2: Based on your screenshot structure
        # Services data (columns 0 and 2)
        services_quarters = []
        services_spends = []
        
        # Marketplace data (columns 4 and 6) 
        marketplace_quarters = []
        marketplace_spends = []
        
        for i, row in df_waterfall.iterrows():
            # Services
            if pd.notna(row.iloc[0]):
                quarter = str(row.iloc[0])
                if quarter.startswith('FY') and 'Q' in quarter:
                    services_quarters.append(quarter)
                    
                    # Look for spend value in next rows or same row
                    spend_val = None
                    if len(row) > 2 and pd.notna(row.iloc[2]):
                        spend_str = str(row.iloc[2]).replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
                        try:
                            spend_val = float(spend_str)
                        except:
                            spend_val = 0
                    services_spends.append(spend_val if spend_val is not None else 0)
            
            # Marketplace
            if len(row) > 4 and pd.notna(row.iloc[4]):
                quarter = str(row.iloc[4])
                if quarter.startswith('FY') and 'Q' in quarter:
                    marketplace_quarters.append(quarter)
                    
                    # Look for spend value
                    spend_val = None
                    if len(row) > 6 and pd.notna(row.iloc[6]):
                        spend_str = str(row.iloc[6]).replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
                        try:
                            spend_val = float(spend_str)
                        except:
                            spend_val = 0
                    marketplace_spends.append(spend_val if spend_val is not None else 0)
        
        # Create DataFrames
        if services_quarters:
            services_df = pd.DataFrame({
                'Quarter': services_quarters,
                'Spend': services_spends
            })
        
        if marketplace_quarters:
            marketplace_df = pd.DataFrame({
                'Quarter': marketplace_quarters,
                'Spend': marketplace_spends
            })
    
    # Display debug info
    st.subheader("Data Extraction Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Services Data:**")
        if not services_df.empty:
            st.dataframe(services_df)
        else:
            st.write("No services data found")
    
    with col2:
        st.write("**Marketplace Data:**")
        if not marketplace_df.empty:
            st.dataframe(marketplace_df)
        else:
            st.write("No marketplace data found")
    
    # ------------------ Create Waterfall Charts ------------------
    st.subheader("Waterfall Charts")
    
    col1, col2 = st.columns(2)
    
    # Services Waterfall Chart
    with col1:
        if not services_df.empty and len(services_df) > 0:
            # Filter out zero values for waterfall
            services_filtered = services_df[services_df['Spend'] != 0].copy()
            
            if not services_filtered.empty:
                fig_services = go.Figure(go.Waterfall(
                    name="Services Spend",
                    orientation="v",
                    x=services_filtered['Quarter'],
                    y=services_filtered['Spend'],
                    text=[f"${x:,.0f}" for x in services_filtered['Spend']],
                    textposition="outside",
                    connector={"line": {"color": "blue"}},
                    decreasing={"marker": {"color": "rgb(244, 101, 101)"}},  # Red for negative
                    increasing={"marker": {"color": "rgb(91, 155, 213)"}},   # Blue for positive
                    totals={"marker": {"color": "rgb(37, 64, 97)"}}
                ))
                fig_services.update_layout(
                    title="CSP Services Spend Waterfall",
                    yaxis_title="Spend ($)",
                    xaxis_tickangle=-45,
                    height=500
                )
                st.plotly_chart(fig_services, use_container_width=True)
            else:
                st.write("No valid services data for waterfall chart")
        else:
            st.write("No services data available")
    
    # Marketplace Waterfall Chart
    with col2:
        if not marketplace_df.empty and len(marketplace_df) > 0:
            # Filter out zero values and NaN for waterfall
            marketplace_filtered = marketplace_df[
                (marketplace_df['Spend'] != 0) & 
                (marketplace_df['Spend'].notna())
            ].copy()
            
            if not marketplace_filtered.empty:
                fig_marketplace = go.Figure(go.Waterfall(
                    name="Marketplace Spend",
                    orientation="v",
                    x=marketplace_filtered['Quarter'],
                    y=marketplace_filtered['Spend'],
                    text=[f"${x:,.0f}" for x in marketplace_filtered['Spend']],
                    textposition="outside",
                    connector={"line": {"color": "darkblue"}},
                    decreasing={"marker": {"color": "rgb(244, 67, 54)"}},   # Red for negative
                    increasing={"marker": {"color": "rgb(0, 176, 240)"}},   # Light blue for positive
                    totals={"marker": {"color": "rgb(31, 78, 121)"}}
                ))
                fig_marketplace.update_layout(
                    title="CSP Marketplace Spend Waterfall",
                    yaxis_title="Spend ($)",
                    xaxis_tickangle=-45,
                    height=500
                )
                st.plotly_chart(fig_marketplace, use_container_width=True)
            else:
                st.write("No valid marketplace data for waterfall chart")
        else:
            st.write("No marketplace data available")
    
    # ------------------ Summary Statistics ------------------
    st.subheader("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not services_df.empty:
            total_services = services_df['Spend'].sum()
            st.metric("Total Services Spend", f"${total_services:,.0f}")
    
    with col2:
        if not marketplace_df.empty:
            total_marketplace = marketplace_df['Spend'].sum()
            st.metric("Total Marketplace Spend", f"${total_marketplace:,.0f}")
    
    with col3:
        if not services_df.empty and not marketplace_df.empty:
            total_combined = services_df['Spend'].sum() + marketplace_df['Spend'].sum()
            st.metric("Combined Total", f"${total_combined:,.0f}")
    
    with col4:
        if not services_df.empty:
            avg_services = services_df['Spend'].mean()
            st.metric("Avg Services per Quarter", f"${avg_services:,.0f}")

except FileNotFoundError:
    st.error("❌ Excel file not found. Please ensure 'Cloud_Actual_Optimization Data.xlsx' is in the repository.")
except Exception as e:
    st.error(f"❌ Error loading or processing the Excel file: {str(e)}")
    st.write("Please check that the file structure matches the expected format.")
    
    # Show raw data for debugging
    try:
        df_raw = pd.read_excel(file_path, sheet_name=0)
        st.subheader("Raw Data (First 10 rows)")
        st.dataframe(df_raw.head(10))
        st.write("Columns:", list(df_raw.columns))
        st.write("Shape:", df_raw.shape)
    except:
        st.write("Could not load raw data for debugging.")

# ------------------ Manual File Upload Option ------------------
st.subheader("Alternative: Upload Excel File")
uploaded_file = st.file_uploader("Upload your Excel file here", type=['xlsx'])

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_excel(uploaded_file, sheet_name=0)
        st.success("✅ File uploaded successfully!")
        st.write("Shape:", df_uploaded.shape)
        st.dataframe(df_uploaded.head())
        
        st.write("**Instructions for your data format:**")
        st.write("Based on your screenshot, the app expects:")
        st.write("- Services data in the left columns (Quarter and Spend)")
        st.write("- Marketplace data in the right columns (Quarter and Spend)")
        st.write("- Quarters in format: FY24 Q1, FY24 Q2, etc.")
        st.write("- Spend values with $ signs and parentheses for negative values")
        
    except Exception as e:
        st.error(f"Error with uploaded file: {str(e)}")
