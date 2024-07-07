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
filepath = 'btc_usdt_ohlcv_last_25_days.csv'

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
