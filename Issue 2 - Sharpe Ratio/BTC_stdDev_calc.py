from scipy.stats import norm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def read_ohlcv_from_csv(filepath):
    """
    Read OHLCV data from a CSV file into a DataFrame.

    :param filepath: Path to the CSV file
    :return: DataFrame with columns [timestamp, open, high, low, close, volume]
    """
    df = pd.read_csv(filepath)

    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def calculate_daily_returns(df):
    """
    Calculate daily returns from the close prices and convert to percentage terms.

    :param df: DataFrame with historical OHLCV data
    :return: Series of daily returns in percentage terms
    """
    df['daily_return'] = df['close'].pct_change()  # Multiply by 100 here
    return df['daily_return'].dropna()


def calculate_standard_deviation(daily_returns):
    """
    Calculate the standard deviation of daily returns.

    :param daily_returns: Series of daily returns
    :return: Standard deviation of daily returns
    """
    return np.std(daily_returns)


# Specify the file path where the data is saved
filepath = './btc_usdt_ohlcv_last_25_days.csv'

# Read data from CSV
df = read_ohlcv_from_csv(filepath)

# Calculate daily returns
daily_returns = calculate_daily_returns(df)

# Calculate the standard deviation of daily returns
std_dev = calculate_standard_deviation(daily_returns)

# Print the standard deviation in % terms (x100)
print(
    f'The standard deviation of the last {len(daily_returns)} daily returns for BTC/USDT is {std_dev*100: .2f}%')


def calculate_daily_returns(df):
    """
    Calculate daily returns from the close prices and convert to percentage terms.
    Also, calculate the average daily return.

    :param df: DataFrame with historical OHLCV data
    :return: Tuple containing:
             - Series of daily returns in percentage terms
             - Average daily return in percentage terms
    """
    df['daily_return'] = df['close'].pct_change()  # Calculate daily returns
    daily_returns = df['daily_return'].dropna()  # Drop the first NaN value
    # Calculate the average daily return
    average_daily_return = daily_returns.mean()
    return daily_returns, average_daily_return


# Calculate daily returns and average daily return
daily_returns, average_daily_return = calculate_daily_returns(df)
# Print the average daily return in % terms (x100)
print(
    f'The average daily return for BTC/USDT over the last {len(daily_returns)} days is {average_daily_return*100: .2f}%')


def calculate_daily_returns(df):
    """
    Calculate daily returns from the close prices and convert to percentage terms.
    Also, calculate the average daily return and the bounds within which the daily returns
    are expected to fall most of the time (assuming a normal distribution).

    :param df: DataFrame with historical OHLCV data
    :return: Tuple containing:
             - Series of daily returns in percentage terms
             - Average daily return in percentage terms
             - Lower bound of the 68% probability range
             - Upper bound of the 68% probability range
    """
    df['daily_return'] = df['close'].pct_change()  # Calculate daily returns
    daily_returns = df['daily_return'].dropna()  # Drop the first NaN value
    # Calculate the average daily return
    average_daily_return = daily_returns.mean()
    std_dev = daily_returns.std()  # Calculate the standard deviation

    # Calculate the bounds for the 68% probability range
    lower_bound = average_daily_return - std_dev
    upper_bound = average_daily_return + std_dev

    return daily_returns, average_daily_return, lower_bound, upper_bound


# Calculate daily returns, average daily return, and the 68% probability bounds
daily_returns, average_daily_return, lower_bound, upper_bound = calculate_daily_returns(
    df)

# Print the average daily return and the 68% probability bounds in % terms (x100)
print(
    f'The average daily return for BTC/USDT over the last {len(daily_returns)} days is {average_daily_return*100: .2f}%')
print(f'Within 1 Standard Deviation (68% probability):')
print(f'Lower Bound: {lower_bound*100: .2f}%')
print(f'Upper Bound: {upper_bound*100: .2f}%')


def calculate_daily_returns(df):
    """
    Calculate daily returns from the close prices and convert to percentage terms.
    Also, calculate the average daily return and the bounds within which the daily returns
    are expected to fall most of the time (assuming a normal distribution), for both 1 and 2
    standard deviations.

    :param df: DataFrame with historical OHLCV data
    :return: Tuple containing:
             - Series of daily returns in percentage terms
             - Average daily return in percentage terms
             - Lower bound of the 68% probability range
             - Upper bound of the 68% probability range
             - Lower bound of the 95% probability range
             - Upper bound of the 95% probability range
    """
    df['daily_return'] = df['close'].pct_change()  # Calculate daily returns
    daily_returns = df['daily_return'].dropna()  # Drop the first NaN value
    # Calculate the average daily return
    average_daily_return = daily_returns.mean()
    std_dev = daily_returns.std()  # Calculate the standard deviation

    # Calculate the bounds for the 68% probability range
    lower_bound_68 = average_daily_return - std_dev
    upper_bound_68 = average_daily_return + std_dev

    # Calculate the bounds for the 95% probability range
    lower_bound_95 = average_daily_return - 2 * std_dev
    upper_bound_95 = average_daily_return + 2 * std_dev

    return daily_returns, average_daily_return, lower_bound_68, upper_bound_68, lower_bound_95, upper_bound_95


# Calculate daily returns, average daily return, and the probability bounds
daily_returns, average_daily_return, lower_bound_68, upper_bound_68, lower_bound_95, upper_bound_95 = calculate_daily_returns(
    df)

# Print the average daily return and the probability bounds in % terms (x100)
print(
    f'The average daily return for BTC/USDT over the last {len(daily_returns)} days is {average_daily_return*100: .2f}%')
print(f'Within 1 Standard Deviation (68% probability):')
print(f'Lower Bound: {lower_bound_68*100: .2f}%')
print(f'Upper Bound: {upper_bound_68*100: .2f}%')
print(f'Within 2 Standard Deviations (95% probability):')
print(f'Lower Bound: {lower_bound_95*100: .2f}%')
print(f'Upper Bound: {upper_bound_95*100: .2f}%')

plt.figure(facecolor='#f7e9e1')

# Plotting the histogram
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

# Customizing the plot with enhanced labels, title, and grid
plt.xlabel('Daily Returns (%)', fontsize=12, color='#100d16')
plt.ylabel('Probability Density', fontsize=12, color='#100d16')
plt.title('Daily BTC/USDT Returns stdDev +1, +2', fontsize=14, color='#100d16')
plt.legend()

plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='#100d16')

plt.tick_params(colors='#100d16')

# Saving the figure with improved styling
plt.savefig('daily_btc_stdDev.png')
