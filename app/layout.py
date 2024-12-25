from dash import html, dcc
import plotly.graph_objs as go
import pandas as pd
import os

# Load simulation data from file
def load_simulation_data():
    filepath = "data/simulation_results.csv"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Simulation results not found in {filepath}. Please run the simulation script first.")
    return pd.read_csv(filepath)

# Create 3D scatter plot of portfolio data
def create_3d_scatter(simulation_df):
    fig = go.Figure(data=[go.Scatter3d(
        x=simulation_df["Volatility"],
        y=simulation_df["Return"],
        z=simulation_df["Sharpe Ratio"],
        mode="markers",
        marker=dict(
            size=5,
            color=simulation_df["Sharpe Ratio"],
            colorscale="purpor",
            colorbar=dict(thickness=20),
            colorbar_title_text='Sharpe Ratio and Return'
        ),
        customdata=simulation_df.index  # Store index for callback reference
    )])
    fig.update_layout(scene=dict(
        xaxis_title="Volatility",
        yaxis_title="Return",
        zaxis_title="Sharpe Ratio"
    ))
    return fig

# Create initial bar chart for portfolio weights
def create_bar_chart(simulation_df):
    tickers = simulation_df.columns[3:]
    initial_weights = simulation_df.iloc[0, 3:].values
    bar_data = pd.DataFrame({"Tickers": tickers, "Weights": initial_weights})
    return go.Figure(data=[go.Bar(
        x=bar_data["Tickers"],
        y=bar_data["Weights"],
        marker=dict(color='rgb(71, 71, 135)')
    )])

# Layout definition for the app
def create_layout():
    return html.Div(
        style={'font-family': 'Arial, sans-serif', 'background-color': '#f8f8f8', 'padding': '30px'},
        children=[ 
            html.H1("Monte Carlo Portfolio Simulation", style={'text-align': 'center', 'color': '#333'}),
            
            html.Div(
                style={'background-color': 'white', 'padding': '20px', 'border-radius': '8px', 'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.1)', 'margin-top': '20px'},
                children=[
                    html.H4("Work In Progress Comments", style={'text-align': 'center', 'color': '#333'}),
                    html.P("This section provides comments and feedback of the following features. As of now the scatter plot is fully interactable to showcase portfolio, volatility, Sharpe ratio and expected return. To interact, please click any scatter plot point which will cause the bar graph to update along with the stats attached.", style={'text-align': 'justify', 'font-size': '16px'})
                ]
            ),
            
            html.Div(
                style={'display': 'flex', 'justify-content': 'space-between', 'gap': '30px', 'margin-top': '30px'},
                children=[
                    dcc.Graph(id="3d-plot", figure=create_3d_scatter(load_simulation_data()), style={'height': '600px', 'width': '48%'}),

                    html.Div(
                        style={'display': 'flex', 'flex-direction': 'column', 'width': '48%'},
                        children=[
                            dcc.Graph(id="bar-chart", figure=create_bar_chart(load_simulation_data()), style={'height': '400px'}),
                            html.Div(id="portfolio-stats", style={'background-color': 'white', 'padding': '20px', 'border-radius': '8px', 'box-shadow': '0 4px 12px rgba(0, 0, 0, 0.1)', 'font-size': '18px', 'margin-top': '20px'})
                        ]
                    )
                ]
            )
        ]
    )
