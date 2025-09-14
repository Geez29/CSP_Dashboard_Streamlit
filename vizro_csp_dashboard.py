import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="CSP Dashboard", layout="wide")

# McKinsey Style Colors
MCKINSEY_BLUE = "#1f77b4"
MCKINSEY_LIGHT_BLUE = "#aec7e8" 
MCKINSEY_DARK_BLUE = "#1f4e79"
AWS_COLOR = "#FF9900"
AZURE_COLOR = "#0078D4"

# ------------------ Hardcoded Data ------------------
@st.cache_data
def load_hardcoded_data():
    # Line Chart Data - Monthly CSP Costs
    line_data = {
        'Month': [
            '2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06',
            '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12',
            '2025-01', '2025-02', '2025-03'
        ],
        'AWS_Cost': [
            850000, 920000, 1050000, 1200000, 1180000, 1350000,
            1400000, 1320000, 1450000, 1520000, 1480000, 1600000,
            1650000, 1720000, 1800000
        ],
        'Azure_Cost': [
            650000, 680000, 720000, 850000, 890000, 950000,
            980000, 1020000, 1100000, 1150000, 1200000, 1280000,
            1320000, 1380000, 1420000
        ]
    }
    
    # Convert to long format for plotting
    df_line = pd.DataFrame(line_data)
    df_melted = pd.melt(df_line, id_vars=['Month'], 
                       value_vars=['AWS_Cost', 'Azure_Cost'],
                       var_name='CSP', value_name='Cost')
    df_melted['CSP'] = df_melted['CSP'].str.replace('_Cost', '')
    
    # Calculate Fiscal Year
    def assign_fy(date_str):
        year, month = map(int, date_str.split("-"))
        return f"FY{year+1}" if month >= 4 else f"FY{year}"
    
    df_melted["FY"] = df_melted["Month"].apply(assign_fy)
    
    return df_melted

@st.cache_data
def load_waterfall_data():
    # Services Waterfall Data
    services_data = {
        'Quarter': ['FY24 Q1', 'FY24 Q2', 'FY24 Q3', 'FY24 Q4', 'FY25 Q1', 'FY25 Q2', 'FY25 Q3'],
        'Spend': [527303, -118655, 483800, -36352, 481927, -73350, 496333]
    }
    
    # Marketplace Waterfall Data
    marketplace_data = {
        'Quarter': ['FY24 Q1', 'FY24 Q2', 'FY24 Q3', 'FY24 Q4', 'FY25 Q1', 'FY25 Q2', 'FY25 Q3'],
        'Spend': [592131, 13553, 32365, 3350, 782748, 439201, 131260]
    }
    
    return pd.DataFrame(services_data), pd.DataFrame(marketplace_data)

# Load data
df_line = load_hardcoded_data()
services_df, marketplace_df = load_waterfall_data()

# ------------------ Header ------------------
st.markdown("""
<div style='text-align: center; padding: 20px; margin-bottom: 30px;'>
    <h1 style='color: #1f4e79; font-family: Arial, sans-serif; font-weight: 300; margin-bottom: 10px;'>
        Cloud Service Provider Dashboard
    </h1>
    <p style='color: #666; font-size: 18px; font-family: Arial, sans-serif;'>
        Monthly Cost Analysis & Optimization Tracking
    </p>
</div>
""", unsafe_allow_html=True)

# ------------------ FY Filter ------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    fy_options = sorted(df_line["FY"].unique())
    selected_fy = st.selectbox("📅 Select Fiscal Year", fy_options, 
                              help="Choose fiscal year to analyze monthly trends")

# Filter data
filtered_df = df_line[df_line["FY"] == selected_fy]

# ------------------ McKinsey Style Line Chart ------------------
st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)

if not filtered_df.empty:
    # Create the line chart with McKinsey styling
    fig = go.Figure()
    
    # Add AWS line
    aws_data = filtered_df[filtered_df['CSP'] == 'AWS']
    fig.add_trace(go.Scatter(
        x=aws_data['Month'],
        y=aws_data['Cost'],
        mode='lines+markers',
        name='AWS',
        line=dict(color=AWS_COLOR, width=3),
        marker=dict(size=8, color=AWS_COLOR, symbol='circle'),
        hovertemplate='<b>AWS</b><br>Month: %{x}<br>Cost: $%{y:,.0f}<extra></extra>'
    ))
    
    # Add Azure line  
    azure_data = filtered_df[filtered_df['CSP'] == 'Azure']
    fig.add_trace(go.Scatter(
        x=azure_data['Month'],
        y=azure_data['Cost'],
        mode='lines+markers',
        name='Azure',
        line=dict(color=AZURE_COLOR, width=3),
        marker=dict(size=8, color=AZURE_COLOR, symbol='circle'),
        hovertemplate='<b>Azure</b><br>Month: %{x}<br>Cost: $%{y:,.0f}<extra></extra>'
    ))
    
    # McKinsey style layout
    fig.update_layout(
        title=dict(
            text="CSP Monthly Cost Trend (AWS vs Azure)",
            x=0.5,
            font=dict(size=24, color=MCKINSEY_DARK_BLUE, family="Arial"),
            pad=dict(t=20)
        ),
        xaxis=dict(
            title="Month",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showspikes=True,
            spikecolor="rgba(128,128,128,0.5)",
            spikethickness=1,
            spikemode="across",
            tickangle=-45,
            title_font=dict(size=14, color=MCKINSEY_DARK_BLUE),
            tickfont=dict(size=12, color='#333')
        ),
        yaxis=dict(
            title="Cost (USD)",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)',
            showspikes=True,
            spikecolor="rgba(128,128,128,0.5)",
            spikethickness=1,
            spikemode="across",
            title_font=dict(size=14, color=MCKINSEY_DARK_BLUE),
            tickfont=dict(size=12, color='#333'),
            tickformat='$,.0f'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(t=80, b=60, l=80, r=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color=MCKINSEY_DARK_BLUE)
        ),
        font=dict(family="Arial", size=12, color='#333')
    )
    
    # Add subtle background
    fig.update_layout(
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                fillcolor="rgba(248,249,250,0.8)",
                layer="below",
                line_width=0,
            )
        ]
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Metrics Row
    st.markdown("<div style='margin: 40px 0 20px 0;'></div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        aws_total = aws_data['Cost'].sum()
        st.metric(
            label="🔶 AWS Total",
            value=f"${aws_total:,.0f}",
            delta=f"{aws_data['Cost'].pct_change().iloc[-1]:.1%}" if len(aws_data) > 1 else None
        )
    
    with col2:
        azure_total = azure_data['Cost'].sum()
        st.metric(
            label="🔷 Azure Total", 
            value=f"${azure_total:,.0f}",
            delta=f"{azure_data['Cost'].pct_change().iloc[-1]:.1%}" if len(azure_data) > 1 else None
        )
    
    with col3:
        combined_total = aws_total + azure_total
        st.metric(
            label="💰 Combined Total",
            value=f"${combined_total:,.0f}"
        )
    
    with col4:
        aws_share = aws_total / combined_total * 100
        st.metric(
            label="📊 AWS Share",
            value=f"{aws_share:.1f}%"
        )

else:
    st.warning("⚠️ No data available for the selected Fiscal Year.")

# ------------------ Waterfall Charts Section ------------------
st.markdown("""
<div style='margin: 60px 0 30px 0;'>
    <h2 style='color: #1f4e79; font-family: Arial, sans-serif; text-align: center; font-weight: 300;'>
        Quarterly Spend Analysis
    </h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# Services Waterfall
with col1:
    if not services_df.empty:
        fig_services = go.Figure(go.Waterfall(
            name="Services Spend",
            orientation="v",
            x=services_df['Quarter'],
            y=services_df['Spend'],
            text=[f"${x:,.0f}" for x in services_df['Spend']],
            textposition="outside",
            connector={"line": {"color": MCKINSEY_BLUE}},
            decreasing={"marker": {"color": "#FF6B6B"}},
            increasing={"marker": {"color": MCKINSEY_BLUE}},
            totals={"marker": {"color": MCKINSEY_DARK_BLUE}}
        ))
        
        fig_services.update_layout(
            title=dict(
                text="CSP Services Spend Waterfall",
                x=0.5,
                font=dict(size=18, color=MCKINSEY_DARK_BLUE, family="Arial")
            ),
            yaxis=dict(
                title="Spend (USD)",
                tickformat='$,.0f',
                title_font=dict(color=MCKINSEY_DARK_BLUE),
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            xaxis=dict(
                tickangle=-45,
                title_font=dict(color=MCKINSEY_DARK_BLUE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=450,
            margin=dict(t=60, b=100, l=60, r=60),
            font=dict(family="Arial", size=11, color='#333')
        )
        
        st.plotly_chart(fig_services, use_container_width=True)

# Marketplace Waterfall
with col2:
    if not marketplace_df.empty:
        fig_marketplace = go.Figure(go.Waterfall(
            name="Marketplace Spend",
            orientation="v",
            x=marketplace_df['Quarter'],
            y=marketplace_df['Spend'],
            text=[f"${x:,.0f}" for x in marketplace_df['Spend']],
            textposition="outside",
            connector={"line": {"color": MCKINSEY_LIGHT_BLUE}},
            decreasing={"marker": {"color": "#FF6B6B"}},
            increasing={"marker": {"color": MCKINSEY_LIGHT_BLUE}},
            totals={"marker": {"color": MCKINSEY_DARK_BLUE}}
        ))
        
        fig_marketplace.update_layout(
            title=dict(
                text="CSP Marketplace Spend Waterfall",
                x=0.5,
                font=dict(size=18, color=MCKINSEY_DARK_BLUE, family="Arial")
            ),
            yaxis=dict(
                title="Spend (USD)",
                tickformat='$,.0f',
                title_font=dict(color=MCKINSEY_DARK_BLUE),
                showgrid=True,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            xaxis=dict(
                tickangle=-45,
                title_font=dict(color=MCKINSEY_DARK_BLUE)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=450,
            margin=dict(t=60, b=100, l=60, r=60),
            font=dict(family="Arial", size=11, color='#333')
        )
        
        st.plotly_chart(fig_marketplace, use_container_width=True)

# ------------------ Summary Statistics ------------------
st.markdown("""
<div style='margin: 40px 0 20px 0;'>
    <h3 style='color: #1f4e79; font-family: Arial, sans-serif; text-align: center; font-weight: 300;'>
        Quarterly Summary
    </h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    services_total = services_df['Spend'].sum()
    st.metric(
        label="🔧 Total Services",
        value=f"${services_total:,.0f}",
        help="Sum of all services spend across quarters"
    )

with col2:
    marketplace_total = marketplace_df['Spend'].sum()
    st.metric(
        label="🛒 Total Marketplace", 
        value=f"${marketplace_total:,.0f}",
        help="Sum of all marketplace spend across quarters"
    )

with col3:
    combined_quarterly = services_total + marketplace_total
    st.metric(
        label="💼 Combined Quarterly",
        value=f"${combined_quarterly:,.0f}",
        help="Total of services and marketplace spend"
    )

with col4:
    avg_quarterly = combined_quarterly / max(len(services_df), len(marketplace_df))
    st.metric(
        label="📈 Avg per Quarter",
        value=f"${avg_quarterly:,.0f}",
        help="Average spend per quarter"
    )

# ------------------ Footer ------------------
st.markdown("""
<div style='margin-top: 60px; padding: 20px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #eee;'>
    <p>📊 CSP Dashboard | Data Coverage: FY24 (Complete) | FY25 (Complete) | FY26 (Apr-Jun) | For internal use only</p>
    <p style='margin-top: 5px; font-size: 10px;'>Fiscal Year: April 1st - March 31st | Q1: Apr-Jun | Q2: Jul-Sep | Q3: Oct-Dec | Q4: Jan-Mar</p>
</div>
""", unsafe_allow_html=True)

# ------------------ CSS Styling ------------------
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric > label {
        font-size: 14px !important;
        color: #1f4e79 !important;
        font-weight: 600 !important;
    }
    
    .stMetric > div > div {
        font-size: 24px !important;
        color: #1f4e79 !important;
        font-weight: 700 !important;
    }
    
    .stSelectbox > label {
        font-weight: 600 !important;
        color: #1f4e79 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
