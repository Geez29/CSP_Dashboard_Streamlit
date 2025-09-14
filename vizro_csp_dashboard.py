import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html

# Load Excel file
file_path = "cloud_spend.xlsx"  # replace with your file name
df = pd.ExcelFile(file_path)

# Since both Services and Marketplace are in the same sheet
data = pd.read_excel(file_path, sheet_name=0)

# Clean column names
data.columns = data.columns.str.strip()

# Keep only till FY26 Q2
valid_quarters = [
    "FY24 Q1", "FY24 Q2", "FY24 Q3", "FY24 Q4",
    "FY25 Q1", "FY25 Q2", "FY25 Q3", "FY25 Q4",
    "FY26 Q1", "FY26 Q2"
]

# Filter data
services_data = data[['Services', 'Unnamed: 1']].dropna()
services_data.columns = ['Quarter', 'Spend']
services_data = services_data[services_data['Quarter'].isin(valid_quarters)]

marketplace_data = data[['Marketplace', 'Unnamed: 3']].dropna()
marketplace_data.columns = ['Quarter', 'Spend']
marketplace_data = marketplace_data[marketplace_data['Quarter'].isin(valid_quarters)]

# Create Services Waterfall Chart (with cost optimization as negative values)
fig_services = go.Figure(go.Waterfall(
    name="Services Spend",
    orientation="v",
    x=services_data['Quarter'],
    y=services_data['Spend'],
    text=services_data['Spend'],
    textposition="outside",
    connector={"line": {"color": "blue"}}
))

fig_services.update_layout(
    title="CSP Services Spend",
    waterfallgap=0.3,
    yaxis_title="Spend ($)"
)

# Create Marketplace Waterfall Chart
fig_marketplace = go.Figure(go.Waterfall(
    name="Marketplace Spend",
    orientation="v",
    x=marketplace_data['Quarter'],
    y=marketplace_data['Spend'],
    text=marketplace_data['Spend'],
    textposition="outside",
    connector={"line": {"color": "brown"}}
))

fig_marketplace.update_layout(
    title="CSP Marketplace Spend",
    waterfallgap=0.3,
    yaxis_title="Spend ($)"
)

# Build Dashboard
app = Dash(__name__)

app.layout = html.Div([
    html.H1("CSP Services & Marketplace Spend Dashboard"),
    html.Div([
        html.Div([dcc.Graph(figure=fig_services)], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(figure=fig_marketplace)], style={'width': '48%', 'display': 'inline-block'})
    ])
])

if __name__ == "__main__":
    app.run_server(debug=True)
