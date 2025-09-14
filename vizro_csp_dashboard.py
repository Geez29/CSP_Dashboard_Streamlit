import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")
st.title("CSP Dashboard")

# ------------------ Load Excel Files ------------------
line_chart_file = "CSP_Monthly_Cost_Sample Data.xlsx"
waterfall_file = "Cloud_Actual_Optimization Data.xlsx"

try:
    # ------------------ Load Line Chart Data ------------------
    df_line = pd.read_excel(line_chart_file, sheet_name=0)
    st.success("✅ Line chart data loaded successfully")
    
    # Clean and process line chart data
    df_line.columns = df_line.columns.str.strip()
    
    # Convert Month to datetime and then to string format
    if 'Month' in df_line.columns:
        df_line["Month"] = pd.to_datetime(df_line["Month"], errors='coerce').dt.strftime("%Y-%m")
        df_line = df_line.dropna(subset=['Month'])
        
        # Fiscal Year Calculation
        def assign_fy(date_str):
            try:
                year, month = map(int, date_str.split("-"))
                return f"FY{year+1}" if month >= 4 else f"FY{year}"
            except:
                return "Unknown"

        if "FY" not in df_line.columns:
            df_line["FY"] = df_line["Month"].apply(assign_fy)

        # FY Filter
        fy_options = sorted(df_line["FY"].unique())
        selected_fy = st.selectbox("Select Fiscal Year (FY):", fy_options)
        filtered_df = df_line[df_line["FY"] == selected_fy]

        # ------------------ Line Chart ------------------
        if not filtered_df.empty and 'Cost' in filtered_df.columns and 'CSP' in filtered_df.columns:
            max_cost = filtered_df["Cost"].max()

            fig_line = px.line(
                filtered_df,
                x="Month",
                y="Cost",
                color="CSP",
                markers=True,
                hover_data=["FY"],
                title="CSP Monthly Cost AWS vs Azure"
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
                    spikemode="across",
                    title="Cost ($)"
                ),
                margin=dict(t=60, b=60, l=60, r=60),
                height=500
            )

            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Line chart data missing required columns (Month, Cost, CSP) or no data for selected FY")
    else:
        st.warning("Month column not found in line chart data")

except FileNotFoundError:
    st.error(f"❌ Line chart file not found: {line_chart_file}")
except Exception as e:
    st.error(f"❌ Error loading line chart data: {str(e)}")

try:
    # ------------------ Load Waterfall Data ------------------
    df_waterfall = pd.read_excel(waterfall_file, sheet_name=0)
    st.success("✅ Waterfall data loaded successfully")
    
    # Extract Services and Marketplace data from your specific format
    services_data = []
    marketplace_data = []
    
    # Process each row to extract quarterly data
    for i, row in df_waterfall.iterrows():
        # Services data (left side columns)
        if pd.notna(row.iloc[0]):
            quarter_str = str(row.iloc[0]).strip()
            if quarter_str.startswith('FY') and 'Q' in quarter_str:
                # Look for spend values in subsequent rows or columns
                spend_values = []
                
                # Check multiple columns for spend data
                for col_idx in [1, 2, 3]:
                    if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                        val_str = str(row.iloc[col_idx]).replace('$', '').replace(',', '').strip()
                        if val_str and val_str != '-':
                            # Handle negative values in parentheses
                            if val_str.startswith('(') and val_str.endswith(')'):
                                val_str = '-' + val_str[1:-1]
                            try:
                                spend_val = float(val_str)
                                spend_values.append(spend_val)
                            except:
                                pass
                
                # Add all spend values for this quarter
                for spend_val in spend_values:
                    if spend_val != 0:
                        services_data.append({'Quarter': quarter_str, 'Spend': spend_val})
        
        # Marketplace data (right side columns, typically starting from column 4)
        if len(row) > 4 and pd.notna(row.iloc[4]):
            quarter_str = str(row.iloc[4]).strip()
            if quarter_str.startswith('FY') and 'Q' in quarter_str:
                # Look for spend values in marketplace columns
                for col_idx in [5, 6, 7]:
                    if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                        val_str = str(row.iloc[col_idx]).replace('$', '').replace(',', '').strip()
                        if val_str and val_str != '-':
                            # Handle negative values in parentheses
                            if val_str.startswith('(') and val_str.endswith(')'):
                                val_str = '-' + val_str[1:-1]
                            try:
                                spend_val = float(val_str)
                                if spend_val != 0:
                                    marketplace_data.append({'Quarter': quarter_str, 'Spend': spend_val})
                            except:
                                pass
    
    # Create DataFrames
    services_df = pd.DataFrame(services_data)
    marketplace_df = pd.DataFrame(marketplace_data)
    
    # Remove duplicates and sort by quarter
    if not services_df.empty:
        services_df = services_df.drop_duplicates().sort_values('Quarter')
    if not marketplace_df.empty:
        marketplace_df = marketplace_df.drop_duplicates().sort_values('Quarter')
    
    # Display debug info
    st.subheader("Waterfall Data Extraction Results")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Services Data:**")
        if not services_df.empty:
            st.dataframe(services_df, use_container_width=True)
        else:
            st.write("No services data found")
    
    with col2:
        st.write("**Marketplace Data:**")
        if not marketplace_df.empty:
            st.dataframe(marketplace_df, use_container_width=True)
        else:
            st.write("No marketplace data found")
    
    # ------------------ Create Waterfall Charts ------------------
    st.subheader("Waterfall Charts")
    
    col1, col2 = st.columns(2)
    
    # Services Waterfall Chart
    with col1:
        if not services_df.empty:
            # Group by quarter and sum spend values
            services_grouped = services_df.groupby('Quarter')['Spend'].sum().reset_index()
            
            fig_services = go.Figure(go.Waterfall(
                name="Services Spend",
                orientation="v",
                x=services_grouped['Quarter'],
                y=services_grouped['Spend'],
                text=[f"${x:,.0f}" for x in services_grouped['Spend']],
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
                height=500,
                margin=dict(t=60, b=100, l=60, r=60)
            )
            st.plotly_chart(fig_services, use_container_width=True)
        else:
            st.write("No services data available for waterfall chart")
    
    # Marketplace Waterfall Chart
    with col2:
        if not marketplace_df.empty:
            # Group by quarter and sum spend values
            marketplace_grouped = marketplace_df.groupby('Quarter')['Spend'].sum().reset_index()
            
            fig_marketplace = go.Figure(go.Waterfall(
                name="Marketplace Spend",
                orientation="v",
                x=marketplace_grouped['Quarter'],
                y=marketplace_grouped['Spend'],
                text=[f"${x:,.0f}" for x in marketplace_grouped['Spend']],
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
                height=500,
                margin=dict(t=60, b=100, l=60, r=60)
            )
            st.plotly_chart(fig_marketplace, use_container_width=True)
        else:
            st.write("No marketplace data available for waterfall chart")
    
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
        elif not services_df.empty:
            st.metric("Total Services Only", f"${services_df['Spend'].sum():,.0f}")
        elif not marketplace_df.empty:
            st.metric("Total Marketplace Only", f"${marketplace_df['Spend'].sum():,.0f}")
    
    with col4:
        if not services_df.empty:
            avg_services = services_df.groupby('Quarter')['Spend'].sum().mean()
            st.metric("Avg Services/Quarter", f"${avg_services:,.0f}")

except FileNotFoundError:
    st.error(f"❌ Waterfall file not found: {waterfall_file}")
except Exception as e:
    st.error(f"❌ Error loading waterfall data: {str(e)}")
    
    # Show raw data for debugging
    try:
        df_raw = pd.read_excel(waterfall_file, sheet_name=0)
        st.subheader("Raw Waterfall Data (First 10 rows)")
        st.dataframe(df_raw.head(10))
        st.write("Columns:", list(df_raw.columns))
        st.write("Shape:", df_raw.shape)
    except:
        st.write("Could not load raw waterfall data for debugging.")

# ------------------ Data Quality Information ------------------
st.subheader("Data Files Information")
col1, col2 = st.columns(2)

with col1:
    st.write("**Line Chart Data File:**")
    st.write(f"📄 {line_chart_file}")
    st.write("Expected format: Month, Cost, CSP columns")

with col2:
    st.write("**Waterfall Data File:**")
    st.write(f"📄 {waterfall_file}")
    st.write("Expected format: Services and Marketplace quarterly data")

# ------------------ Manual File Upload Options ------------------
st.subheader("Alternative: Upload Files Manually")
col1, col2 = st.columns(2)

with col1:
    st.write("**Upload Line Chart Data:**")
    uploaded_line = st.file_uploader("Upload CSP Monthly Cost data", type=['xlsx'], key="line")
    if uploaded_line is not None:
        try:
            df_uploaded_line = pd.read_excel(uploaded_line, sheet_name=0)
            st.success("✅ Line chart file uploaded!")
            st.dataframe(df_uploaded_line.head())
        except Exception as e:
            st.error(f"Error: {str(e)}")

with col2:
    st.write("**Upload Waterfall Data:**")
    uploaded_waterfall = st.file_uploader("Upload Optimization data", type=['xlsx'], key="waterfall")
    if uploaded_waterfall is not None:
        try:
            df_uploaded_waterfall = pd.read_excel(uploaded_waterfall, sheet_name=0)
            st.success("✅ Waterfall file uploaded!")
            st.dataframe(df_uploaded_waterfall.head())
        except Exception as e:
            st.error(f"Error: {str(e)}")
