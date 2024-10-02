from tabulate import tabulate
from data import update_data, read_ohlcv_from_csv
from metrics import calculate_average_annual_return
from metrics import calculate_std_dev, annualise_std_dev
from metrics import calculate_sharpe_ratio, annualise_sharpe_ratio
from metrics import calculate_skewness, calculate_tail_ratios
from metrics import calculate_drawdown
from plots import plot_return_series_histogram
from plots import plot_return_distribution
from plots import plot_skew
from plots import plot_equity_curve
from plots import plot_buy_and_hold_vs_eq_curve
from plots import plot_drawdown
from plots import plot_equity_and_drawdown

ticker = "BTCUSDT"
CSV_FILE = 'btc-usd-max.csv'
update_data(CSV_FILE)

# ticker = "SP500"
# CSV_FILE = 'sp500.csv'

df = read_ohlcv_from_csv(CSV_FILE)


daily_returns = df['price'].pct_change().dropna()


# df['perc_returns'] = df['price'].pct_change().dropna()

# df['notional_futures'] = df['underlying'] * 5
# df['price_diff'] = df['price'] - df['price'].shift(1)
# df['price_return'] = df['price_diff'] * 5
# df['perc_returns'] = df['price_return'] / df['notional_futures']

# daily_returns = df['perc_returns'].dropna()


avg_annual_return = calculate_average_annual_return(daily_returns)

std_dev = calculate_std_dev(daily_returns)
annualised_std_dev = annualise_std_dev(std_dev)
sharpe_ratio = calculate_sharpe_ratio(daily_returns)
annualised_sharpe_ratio = annualise_sharpe_ratio(sharpe_ratio)


skewness = calculate_skewness(daily_returns)

relative_left_ratio, relative_right_ratio = calculate_tail_ratios(
    daily_returns)

drawdowns = calculate_drawdown(daily_returns)
avg_drawdown = drawdowns.mean()
max_drawdown = drawdowns.max()

# Prepare data for the table
table_data = [
    ["Ticker", ticker],
    ["Timeframe", "1d"],
    ["Backtest Length", len(daily_returns)],
    ["Strategy Name", "Long Only 1 Spot Unit"],
    ["Avg. Annual Return", f"{avg_annual_return * 100:.2f}%"],
    # ["Standard Deviation", f"{std_dev*100:.2f}%"],
    ["Ann. stdDev", f"{annualised_std_dev*100:.2f}%"],
    # ["Sharpe Ratio", f"{sharpe_ratio:.4f}"],
    ["Ann. SR", f"{annualised_sharpe_ratio:.4f}"],
    ["Avg. Drawdown", f"{avg_drawdown*100:.2f}%"],
    ["Skew", f"{skewness:.4f}"],
    ["Left Tail", f"{relative_left_ratio:.4f}"],
    ["Right Tail", f"{relative_right_ratio:.4f}"]
]


# Print the table
print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))

# plot_return_series_histogram(daily_returns)
# plot_return_distribution(daily_returns)
# plot_skew(daily_returns)

# plot_equity_curve(daily_returns)
# plot_drawdown(daily_returns)

plot_equity_and_drawdown(daily_returns, ticker)
