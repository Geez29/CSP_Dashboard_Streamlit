import pandas as pd
import vizro
import vizro.models as vm
import vizro.plotly.express as px

# Load Excel file
df = pd.read_excel("CSP_Monthly_Cost_Sample Data.xlsx")

# Ensure Month column is in YYYY-MM format
df["Month"] = pd.to_datetime(df["Month"]).dt.strftime("%Y-%m")

# Calculate Fiscal Year if not present
def assign_fy(date_str):
    year, month = map(int, date_str.split("-"))
    return f"FY{year+1}" if month >= 4 else f"FY{year}"

if "FY" not in df.columns:
    df["FY"] = df["Month"].apply(assign_fy)

# Determine max Cost for placing annotation above
max_cost = df["Cost"].max()

# Create Plotly figure
fig = px.line(
    df,
    x="Month",
    y="Cost",
    color="CSP",
    markers=True,
    hover_data=["FY"]
)

# Add title annotation **inside plotting area**, above highest data point
fig.add_annotation(
    x=df["Month"].iloc[len(df)//2],  # center x
    y=max_cost * 1.05,               # slightly above max y
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

# Wrap figure in Vizro Graph
graph_component = vm.Graph(figure=fig)

# FY filter (no multi-select parameter in this version)
fy_filter = vm.Filter(column="FY")

# Create page without default left-top title
page = vm.Page(
    title="",
    components=[graph_component],
    controls=[fy_filter]
)

# Create dashboard
dashboard = vm.Dashboard(pages=[page])

# Run dashboard
vizro.Vizro().build(dashboard).run()
