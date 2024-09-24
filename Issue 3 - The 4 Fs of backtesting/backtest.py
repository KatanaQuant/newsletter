from tabulate import tabulate
from data import update_data, read_ohlcv_from_csv
from metrics import calculate_std_dev
from metrics import calculate_sharpe_ratio, annualise_sharpe_ratio
from metrics import calculate_skewness
from metrics import calculate_tail_ratios
from plots import plot_return_series
from plots import plot_return_distribution
from plots import plot_skew

CSV_FILE = 'btc-usd-max.csv'
update_data(CSV_FILE)


df = read_ohlcv_from_csv(CSV_FILE)
daily_returns = df['price'].pct_change().dropna()


std_dev = calculate_std_dev(daily_returns)
sharpe_ratio = calculate_sharpe_ratio(daily_returns)
annualised_sharpe_ratio = annualise_sharpe_ratio(sharpe_ratio)

skewness = calculate_skewness(daily_returns)

relative_left_ratio, relative_right_ratio = calculate_tail_ratios(
    daily_returns)

plot_return_series(daily_returns)
plot_return_distribution(daily_returns)
plot_skew(daily_returns)

# Print the backtest report
report_template = """
Backtest Report
===============

Ticker: {ticker}
Timeframe: {timeframe}
Strategy Name: {strategy_name}

Standard Deviation: {std_dev:.4f}

Sharpe Ratio: {sharpe_ratio:.4f}
Annualised Sharpe Ratio: {annualised_sharpe_ratio:.4f}

Skew: {skew:.4f}
Left Tail: {relative_left_ratio:.4f}
Right Tail: {relative_right_ratio:.4f}
"""

print(report_template.format(
    ticker="BTCUSDT",
    timeframe="1d",
    strategy_name="Long Only Spot 1 Unit",
    std_dev=std_dev,
    sharpe_ratio=sharpe_ratio,
    annualised_sharpe_ratio=annualised_sharpe_ratio,
    skew=skewness,
    relative_left_ratio=relative_left_ratio,
    relative_right_ratio=relative_right_ratio
))


# Prepare data for the table
table_data = [
    ["Ticker", "BTCUSDT"],
    ["Timeframe", "1d"],
    ["Strategy Name", "Long Only Spot 1 Unit"],
    ["Standard Deviation", f"{std_dev:.4f}"],
    ["Sharpe Ratio", f"{sharpe_ratio:.4f}"],
    ["Annualised Sharpe Ratio", f"{annualised_sharpe_ratio:.4f}"],
    ["Skew", f"{skewness:.4f}"],
    ["Left Tail", f"{relative_left_ratio:.4f}"],
    ["Right Tail", f"{relative_right_ratio:.4f}"]
]

# Print the table
print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))
