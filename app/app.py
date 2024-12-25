from dash import Dash, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
from layout import create_layout, load_simulation_data, create_3d_scatter, create_bar_chart

# Initialize the Dash app
app = Dash(__name__)

# Load simulation data
simulation_df = load_simulation_data()

# Generate initial figures
fig_3d = create_3d_scatter(simulation_df)
bar_fig = create_bar_chart(simulation_df)

# Define the layout
app.layout = create_layout()

# Callback to update bar chart and portfolio stats on click
@app.callback(
    [Output("bar-chart", "figure"), Output("portfolio-stats", "children")],
    Input("3d-plot", "clickData")
)
def update_bar_chart(clickData):
    if clickData is None:
        return bar_fig, "Click a point to view portfolio stats."
    
    point_index = clickData["points"][0]["customdata"]
    tickers = simulation_df.columns[3:]
    weights = simulation_df.iloc[point_index, 3:].values
    volatility = simulation_df.iloc[point_index]["Volatility"]
    ret = simulation_df.iloc[point_index]["Return"]
    sharpe_ratio = simulation_df.iloc[point_index]["Sharpe Ratio"]

    # Update bar chart with new weights
    new_bar_data = pd.DataFrame({"Tickers": tickers, "Weights": weights})
    updated_bar_fig = go.Figure(data=[go.Bar(x=new_bar_data["Tickers"], y=new_bar_data["Weights"], marker=dict(color='rgb(71, 71, 135)'))])
    updated_bar_fig.update_layout(title="Portfolio Weights")

    # Portfolio stats
    stats = [
        html.P(f"Volatility: {volatility*100:.4f}%", style={'font-weight': '600', 'color': '#333'}),
        html.P(f"Expected Return: {ret*100:.4f}%", style={'font-weight': '600', 'color': '#333'}),
        html.P(f"Sharpe Ratio: {sharpe_ratio:.4f}", style={'font-weight': '600', 'color': '#333'})
    ]

    return updated_bar_fig, stats

if __name__ == "__main__":
    app.run_server(debug=False)
