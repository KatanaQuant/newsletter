from tabulate import tabulate
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, skewnorm


def read_ohlcv_from_xlsx(filepath):
    df = pd.read_excel(filepath)

    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    df.set_index('timestamp', inplace=True)
    df.sort_values(by='timestamp', inplace=True)

    return df


filepath = 'stdDev_and_SR.xlsx'
df = read_ohlcv_from_xlsx(filepath)
daily_returns = df['close'].pct_change().dropna()

# - - - -

# Plotting the return series as histogram
plt.figure(facecolor='#f7e9e1')
time_indices = range(len(daily_returns))
plt.bar(time_indices, daily_returns, color=[
        '#413b3c' if x > 0 else '#de4d39' for x in daily_returns])
plt.axhline(0, color='gray', linestyle='--')

plt.xlabel('Time')
plt.ylabel('Daily Returns')
plt.title('Daily Returns Over Time')
plt.savefig('return_series_histogram.png')

# - - - -

# Calculating the standard deviation of daily returns
std_dev = daily_returns.std()
print(f'stdDev: {std_dev}')
print(f'stdDev%: {std_dev*100: .2f}%')
print('')
# stdDev: 0.021651410970632726
# stdDev%:  2.17%

# - - - -

# Calculating the average daily return
average_daily_return = daily_returns.mean()
print(f'Avg daily return {average_daily_return}')
print(f'Avg daily return% {average_daily_return*100: .2f}%')
print('')
# Avg daily return -0.006210788542243306
# Avg daily return -0.62%

# - - - -

# Calculating the bounds for 68% probability
lower_bound_68 = average_daily_return - std_dev
upper_bound_68 = average_daily_return + std_dev
print(f'Within 1 stdDev (68% probability):')
print(f'μ - σ: {lower_bound_68*100: .2f}%')
print(f'μ + σ: {upper_bound_68*100: .2f}%')
print('')
# Within 1 stdDev (68% probability):
# μ - σ: -2.79%
# μ + σ:  1.54%

# - - - -

# Calculating the bounds for 95% probability
lower_bound_95 = average_daily_return - std_dev * 2
upper_bound_95 = average_daily_return + std_dev * 2
print(f'Within 2 stdDev (95% probability):')
print(f'μ - 2σ: {lower_bound_95*100: .2f}%')
print(f'μ + 2σ: {upper_bound_95*100: .2f}%')
print('')
# Within 2 stdDev (95% probability):
# μ - 2σ: -4.95%
# μ + 2σ:  3.71%

# - - - -

# Plotting the daily returns
plt.figure(facecolor='#f7e9e1')
plt.hist(daily_returns*100, bins=50, alpha=0.7, density=True,
         label='Daily Returns', histtype='bar', rwidth=0.8, color='#413b3c')

# Calculating x and y values for the normal distribution curve
x = np.linspace(min(daily_returns*100), max(daily_returns*100), 100)
y = norm.pdf(x, average_daily_return*100, std_dev*100)

# Plotting the normal distribution curve
plt.plot(x, y, color='#de4d39', label='Normal Distribution', linewidth=2)

# Adding vertical lines for the average and bounds
plt.axvline(average_daily_return*100, color='#100d16',
            linestyle='--', linewidth=2, label='Average Daily Return')
plt.axvline(lower_bound_68*100, color='#de4d39', linestyle='--',
            linewidth=2, label='Lower Bound 68%')
plt.axvline(upper_bound_68*100, color='#de4d39', linestyle='--',
            linewidth=2, label='Upper Bound 68%')
plt.axvline(lower_bound_95*100, color='#de4d39', linestyle='--',
            linewidth=2, label='Lower Bound 95%')
plt.axvline(upper_bound_95*100, color='#de4d39', linestyle='--',
            linewidth=2, label='Upper Bound 95%')

# Annotating the vertical lines with their literal values, adjusted to plot lower on the y-axis
plt.text(average_daily_return*100, plt.ylim()
         [1]*0.45, f'{average_daily_return*100:.2f}%', ha='right', color='#100d16')
plt.text(lower_bound_68*100, plt.ylim()
         [1]*0.40, f'{lower_bound_68*100:.2f}%', ha='right', color='#100d16')
plt.text(upper_bound_68*100, plt.ylim()
         [1]*0.40, f'{upper_bound_68*100:.2f}%', ha='left', color='#100d16')
plt.text(lower_bound_95*100, plt.ylim()
         [1]*0.45, f'{lower_bound_95*100:.2f}%', ha='right', color='#100d16')
plt.text(upper_bound_95*100, plt.ylim()
         [1]*0.45, f'{upper_bound_95*100:.2f}%', ha='left', color='#100d16')

# Adding labels and title
plt.xlabel('Daily Returns (%)', fontsize=12, color='#100d16')
plt.ylabel('Probability Density', fontsize=12, color='#100d16')
plt.title('Daily BTC/USDT Returns stdDev +1, +2', fontsize=14, color='#100d16')
plt.legend()

plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='#100d16')
plt.tick_params(colors='#100d16')

plt.savefig('return_distribution.png')

# - - - -

# Calculating Excess returns
excess_return = average_daily_return

print(f'Excess Return: {excess_return}')
print(f'Excess Return%: {excess_return*100:.2f}')
print('')
# Excess Return: -0.006210788542243306
# Excess Return%: -0.62

# - - - -

# Calculating the Sharpe Ratio
sharpe_ratio = excess_return / std_dev
print(f'Sharpe Ratio: {sharpe_ratio}')
# Sharpe Ratio: -0.2868537551971748

# - - - -

# Annualising the Sharpe Ratio
trading_days_in_a_year = 365  # or 252 for stocks
annualised_sharpe_ratio = sharpe_ratio * np.sqrt(trading_days_in_a_year)
print(f'Annualised Sharpe Ratio: {annualised_sharpe_ratio}')
print('')
# Annualised Sharpe Ratio: -5.480333298058892

# - - - -

# Calculate the skewness of daily returns
skewness_value = daily_returns.skew()

# Plotting the daily returns with skewness
plt.figure(facecolor='#f7e9e1')
# Plotting the histogram of daily returns
plt.hist(daily_returns*100, bins=50, alpha=0.7, density=True,
         label='Daily Returns', color='#413b3c')

# Calculating x values for the distribution curves
x = np.linspace(min(daily_returns*100), max(daily_returns*100), 100)

# Normal distribution curve
y_norm = norm.pdf(x, average_daily_return*100, std_dev*100)
plt.plot(x, y_norm, color='#de4d39', label='Normal Distribution', linewidth=2)

# Skew-normal distribution curve
a = skewness_value
y_skew = skewnorm.pdf(x, a, loc=average_daily_return*100, scale=std_dev*100)
plt.plot(x, y_skew, color='blue', label='Skew-Normal Distribution',
         linestyle='--', linewidth=2)

plt.xlabel('Daily Returns (%)', fontsize=12, color='#100d16')
plt.ylabel('Probability Density', fontsize=12, color='#100d16')
plt.title('Daily BTC/USDT Returns with Skewness', fontsize=14, color='#100d16')
plt.legend()

plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='#100d16')
plt.tick_params(colors='#100d16')

# Saving the figure with improved styling
plt.savefig('skew.png')


print(f'Skewness: {skewness_value}')
print('')
# Skewness: -0.3653467665541139

# - - - -

# Calculate the left tail ratio
normalized_returns = daily_returns - daily_returns.mean()

percentile1 = np.percentile(normalized_returns, 1)
percentile30 = np.percentile(normalized_returns, 30)
left_tail_ratio = percentile1 / percentile30
print(f'Left tail ratio: {left_tail_ratio}')
print('')
# Left tail ratio: 5.325151810198803

# - - - -

# Calculate the right tail ratio
percentile70 = np.percentile(normalized_returns, 70)
percentile99 = np.percentile(normalized_returns, 99)
right_tail_ratio = percentile99 / percentile70
print(f'Right tail ratio: {right_tail_ratio}')
print('')
# Right tail ratio: 3.98234197984283

# - - - -

# Calculate the relative left and right tail ratios
symmetrical_ratio = 4.43
relative_left_ratio = left_tail_ratio / symmetrical_ratio
relative_right_ratio = right_tail_ratio / symmetrical_ratio
print(f'Relative left ratio: {relative_left_ratio}')
print(f'Relative right ratio: {relative_right_ratio}')
print('')
# Relative left ratio: 1.2020658713767052
# Relative right ratio: 0.8989485281812257

# - - - -

# Print the backtest report
report_template = """
Backtest Report
===============

Ticker: {ticker}
Timeframe: {timeframe}
Strategy Name: {strategy_name}

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
    sharpe_ratio=sharpe_ratio,
    annualised_sharpe_ratio=annualised_sharpe_ratio,
    skew=skewness_value,
    relative_left_ratio=relative_left_ratio,
    relative_right_ratio=relative_right_ratio
))


# Prepare data for the table
table_data = [
    ["Ticker", "BTCUSDT"],
    ["Timeframe", "1d"],
    ["Strategy Name", "Long Only Spot 1 Unit"],
    ["Sharpe Ratio", f"{sharpe_ratio:.4f}"],
    ["Annualised Sharpe Ratio", f"{annualised_sharpe_ratio:.4f}"],
    ["Skew", f"{skewness_value:.4f}"],
    ["Left Tail", f"{relative_left_ratio:.4f}"],
    ["Right Tail", f"{relative_right_ratio:.4f}"]
]

# Print the table
print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))
