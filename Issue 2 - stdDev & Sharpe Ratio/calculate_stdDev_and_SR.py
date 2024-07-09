import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def read_ohlcv_from_csv(filepath):
    df = pd.read_excel(filepath)

    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def calculate_daily_returns(df):
    df['daily_return'] = df['close'].pct_change()
    return df['daily_return'].dropna()


filepath = 'stdDev_and_SR.xlsx'
df = read_ohlcv_from_csv(filepath)

daily_returns = calculate_daily_returns(df)
std_dev = np.std(daily_returns)

print(f'stdDev: {std_dev}')
print(f'stdDev%: {std_dev*100: .2f}%')
print('')
# stdDev: 0.021213963635739217
# stdDev%:  2.12%

average_daily_return = daily_returns.mean()
print(f'Avg daily return {average_daily_return}')
print(f'Avg daily return% {average_daily_return*100: .2f}%')
print('')
# Avg daily return -0.006210788542243306
# Avg daily return -0.62%


lower_bound_68 = average_daily_return - std_dev
upper_bound_68 = average_daily_return + std_dev
print(f'Within 1 stdDev (68% probability):')
print(f'μ - σ: {lower_bound_68*100: .2f}%')
print(f'μ + σ: {upper_bound_68*100: .2f}%')
print('')
# Within 1 stdDev (68% probability):
# μ - σ: -2.74%
# μ + σ:  1.50%

lower_bound_95 = average_daily_return - std_dev * 2
upper_bound_95 = average_daily_return + std_dev * 2
print(f'Within 1 stdDev (68% probability):')
print(f'μ - 2σ: {lower_bound_95*100: .2f}%')
print(f'μ + 2σ: {upper_bound_95*100: .2f}%')
print('')
# Within 1 stdDev (68% probability):
# μ - 2σ: -4.86%
# μ + 2σ:  3.62%


plt.figure(facecolor='#f7e9e1')

# Plotting the daily returns
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

# Saving the figure with improved styling
plt.savefig('return_distribution.png')


annual_rfr = 0.02
trading_days_in_a_year = 365  # or 252 for stocks
daily_rfr = annual_rfr / trading_days_in_a_year
# daily_rfr_cmp = (1 + annual_rfr) ** (1/365) - 1
# print(f'Daily RFR CMP: {daily_rfr_cmp}')

excess_return = average_daily_return - daily_rfr

print(f'Daily RFR: {daily_rfr}')
print(f'Average Daily Return: {average_daily_return}')
print(f'Average Daily Return%: {average_daily_return*100:.2f}')
print(f'Excess Return: {excess_return}')
print(f'Excess Return%: {excess_return*100:.2f}')
print('')
# Daily RFR: 5.479452054794521e-05
# Average Daily Return: -0.006210788542243306
# Average Daily Return%: -0.62
# Excess Return: -0.006265583062791251
# Excess Return%: -0.63

sharpe_ratio = excess_return / std_dev
print(f'Sharpe Ratio: {sharpe_ratio}')
# Sharpe Ratio: -0.29535183383814273

annualised_sharpe_ratio = sharpe_ratio * np.sqrt(trading_days_in_a_year)
print(f'Annualised Sharpe Ratio: {annualised_sharpe_ratio}')
print('')
# Annualised Sharpe Ratio: -5.642688862529739
