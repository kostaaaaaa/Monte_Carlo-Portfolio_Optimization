import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import minimize

# Predefined example tickers
example_tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "SPY", "QQQ", "VTI", "BND", "GLD"]

# Prompt user for tickers
input_tickers = input("Enter the tickers to simulate (comma-separated, e.g., AAPL, MSFT, GOOG), or type 'default': ").strip()

if input_tickers.lower() == "default":
    tickers = example_tickers
    print("Using default tickers:", tickers)
else:
    tickers = [ticker.strip().upper() for ticker in input_tickers.split(",")]

# Fixed parameters
risk_free_rate = 0.02 #FredAPI can be used here
bounds = [(0, 0.4) for _ in tickers]
initial_weights = np.array([1 / len(tickers)] * len(tickers))
years_range = [1, 3]
n_simulations = 100

# Download adjusted close data
start_date = datetime.today() - timedelta(days=int(max(years_range) * 365))
end_date = datetime.today()
adj_close_df = pd.DataFrame()

valid_tickers = []
for ticker in tickers:
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if not data.empty:
            adj_close_df[ticker] = data['Adj Close']
            valid_tickers.append(ticker)
    except Exception:
        print(f"Ticker {ticker} not found or failed to fetch data. Skipping.")

# Exit if no valid tickers
if adj_close_df.empty:
    print("No valid tickers were provided. Exiting.")
    exit()

# Calculate log returns and covariance matrix
log_returns = np.log(adj_close_df / adj_close_df.shift(1)).dropna()
cov_matrix = log_returns.cov() * 252

# Monte Carlo Simulation
simulation_data = []
for _ in range(n_simulations):
    years = np.random.uniform(*years_range)
    num_days = int(years * 252)
    sampled_returns = log_returns.tail(num_days)
    sampled_cov_matrix = sampled_returns.cov() * 252

    # Objective functions
    def standard_deviation(weights):
        return np.sqrt(weights.T @ sampled_cov_matrix @ weights)

    def expected_return(weights):
        return np.sum(sampled_returns.mean() * weights) * 252

    def sharpe_ratio(weights):
        return (expected_return(weights) - risk_free_rate) / standard_deviation(weights)

    def neg_sharpe_ratio(weights):
        return -sharpe_ratio(weights)

    # Optimization for maximum Sharpe Ratio
    constraints = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
    result = minimize(neg_sharpe_ratio, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    # Collect results
    optimal_weights = result.x
    optimal_return = expected_return(optimal_weights)
    optimal_volatility = standard_deviation(optimal_weights)
    optimal_sharpe = sharpe_ratio(optimal_weights)

    simulation_data.append([optimal_volatility, optimal_return, optimal_sharpe] + list(optimal_weights))

# Save results to CSV
columns = ["Volatility", "Return", "Sharpe Ratio"] + valid_tickers
simulation_df = pd.DataFrame(simulation_data, columns=columns)
simulation_df.to_csv("data/simulation_results.csv", index=False)

print("Simulation complete. Results saved to 'simulation_results.csv'")
