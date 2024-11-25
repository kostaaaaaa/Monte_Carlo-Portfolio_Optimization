# app.py

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

app = Dash(__name__)

# Load simulation data
simulation_df = pd.read_csv("simulation_results.csv")
tickers = simulation_df.columns[3:]  # Adjust to select ticker columns only

# Define initial bar chart data
initial_weights = simulation_df.iloc[0, 3:].values  # Initial weights for the first point
bar_data = pd.DataFrame({"Tickers": tickers, "Weights": initial_weights})

# 3D Scatter Plot
fig_3d = go.Figure(data=[go.Scatter3d(
    x=simulation_df["Volatility"],
    y=simulation_df["Return"],
    z=simulation_df["Sharpe Ratio"],
    mode="markers",
    marker=dict(size=5, color=simulation_df["Sharpe Ratio"], colorscale="Viridis", colorbar=dict(thickness=20), colorbar_title_text='Sharpe Ratio'),
    customdata=simulation_df.index  # Custom data to store the index for easy lookup
)])
fig_3d.update_layout(scene=dict(
    xaxis_title="Volatility",
    yaxis_title="Return",
    zaxis_title="Sharpe Ratio"
))

app.layout = html.Div([
    dcc.Graph(id="3d-plot", figure=fig_3d),
    dcc.Graph(id="bar-chart", figure=px.bar(bar_data, x="Tickers", y="Weights")),
    html.Div(id="portfolio-stats")  # Container for additional stats display
])

# Callback for updating bar chart on click
@app.callback(
    [Output("bar-chart", "figure"), Output("portfolio-stats", "children")],
    Input("3d-plot", "clickData")
)
def update_bar_chart(clickData):
    if clickData is None:
        # No data clicked, return initial figure
        bar_fig = px.bar(bar_data, x="Tickers", y="Weights")
        return bar_fig, "Click a point to view portfolio stats."

    # Retrieve index of clicked point
    point_index = clickData["points"][0]["customdata"]

    # Get weights and stats for the clicked point
    weights = simulation_df.iloc[point_index, 3:].values
    volatility = simulation_df.iloc[point_index]["Volatility"]
    ret = simulation_df.iloc[point_index]["Return"]
    sharpe_ratio = simulation_df.iloc[point_index]["Sharpe Ratio"]

    # Update bar chart with new weights
    new_bar_data = pd.DataFrame({"Tickers": tickers, "Weights": weights})
    bar_fig = px.bar(new_bar_data, x="Tickers", y="Weights")
    bar_fig.update_layout(title="Portfolio Weights")

    # Display volatility, return, and Sharpe ratio stats
    stats = [
        html.P(f"Volatility: {volatility:.4f}"),
        html.P(f"Expected Return: {ret:.4f}"),
        html.P(f"Sharpe Ratio: {sharpe_ratio:.4f}")
    ]

    return bar_fig, stats

if __name__ == "__main__":
    app.run_server(debug=True)
