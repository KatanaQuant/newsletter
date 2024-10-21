from tabulate import tabulate

from data import update_data, read_ohlcv_from_csv

from metrics import calculate_std_dev, annualise_std_dev
from metrics import calculate_sharpe_ratio, annualise_sharpe_ratio
from metrics import calculate_skewness, calculate_tail_ratios
from metrics import calculate_drawdown

from plots import plot_equity_curve
from plots import plot_drawdown
from plots import plot_equity_and_drawdown

ticker = "BTCUSDT"
CSV_FILE = 'btc-usd-max.csv'
update_data(CSV_FILE)

df = read_ohlcv_from_csv(CSV_FILE)

daily_returns = df['price'].pct_change().dropna()

std_dev = calculate_std_dev(daily_returns)
annualised_std_dev = annualise_std_dev(std_dev)
sharpe_ratio = calculate_sharpe_ratio(daily_returns)
annualised_sharpe_ratio = annualise_sharpe_ratio(sharpe_ratio)


# average_daily_return = daily_returns.mean()
# avg_annual_return = average_daily_return * 256

skewness = calculate_skewness(daily_returns)

relative_left_ratio, relative_right_ratio = calculate_tail_ratios(
    daily_returns)

drawdowns = calculate_drawdown(daily_returns)
avg_drawdown = drawdowns.mean()


# Prepare data for the table
table_data = [
    ["Ticker", ticker],
    ["Timeframe", "1d"],
    ["Backtest Length", len(daily_returns)],
    ["Strategy Name", "Long Only 1 Spot Unit"],
    # ["Standard Deviation", f"{std_dev*100:.2f}%"],
    # ["Ann. stdDev", f"{annualised_std_dev*100:.2f}%"],
    # ["Sharpe Ratio", f"{sharpe_ratio:.4f}"],
    # ["Avg. Annual Return", f"{avg_annual_return * 100:.2f}%"],
    ["Ann. SR", f"{annualised_sharpe_ratio:.4f}"],
    ["Avg. Drawdown", f"{avg_drawdown*100:.2f}%"],
    ["Skew", f"{skewness:.4f}"],
    ["Left Tail", f"{relative_left_ratio:.4f}"],
    ["Right Tail", f"{relative_right_ratio:.4f}"]
]


# Print the table
print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))

# Plot EQ & Drawdown
plot_equity_curve(daily_returns, ticker)
plot_drawdown(daily_returns, ticker)
plot_equity_and_drawdown(daily_returns, ticker)
