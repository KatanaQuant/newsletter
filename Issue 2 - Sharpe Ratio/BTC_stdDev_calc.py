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


# Step 2: Plot histogram of daily returns with adjusted parameters
plt.hist(daily_returns*100, bins=50, alpha=0.5,
         label='Daily Returns', histtype='bar', rwidth=0.8)

# Step 3: Calculate x values for the normal distribution curve
x = np.linspace(min(daily_returns*100), max(daily_returns*100), 100)

# Step 4: Calculate y values for the normal distribution curve
y = norm.pdf(x, average_daily_return*100, std_dev*100)

# Step 5: Plot the normal distribution curve
plt.plot(x, y, 'r--', label='Normal Distribution')

# Step 6: Add vertical lines for the average and bounds
plt.axvline(average_daily_return*100, color='g',
            linestyle='--', label='Average Daily Return')
plt.axvline(lower_bound_68*100, color='y',
            linestyle='--', label='Lower Bound 68%')
plt.axvline(upper_bound_68*100, color='y',
            linestyle='--', label='Upper Bound 68%')
plt.axvline(lower_bound_95*100, color='b',
            linestyle='--', label='Lower Bound 95%')
plt.axvline(upper_bound_95*100, color='b',
            linestyle='--', label='Upper Bound 95%')

# Step 7: Customize the plot
plt.xlabel('Daily Returns (%)')
plt.ylabel('Probability Density')
plt.title('Histogram of BTC/USDT Daily Returns with Normal Distribution')
plt.legend()

# Save the figure
plt.savefig('figure.png')
