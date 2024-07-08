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


# Fetch historical data for BTC/USDT
# Specify the file path where the data is saved
filepath = './btc_usdt_ohlcv_last_25_days.csv'

# Read data from CSV
df = read_ohlcv_from_csv(filepath)
# df = pd.DataFrame(btc_data, columns=[
#     'timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Calculate daily returns
df['daily_return'] = df['close'].pct_change()

# Calculate average daily return and standard deviation of daily returns
average_daily_return = df['daily_return'].mean()
std_dev_daily_return = df['daily_return'].std()

# Annualize the average daily return and the standard deviation of daily returns
trading_days_in_a_year = 365  # or 252 for trading days
annual_average_return = average_daily_return * trading_days_in_a_year
annualized_std_dev = std_dev_daily_return * np.sqrt(trading_days_in_a_year)

# Define the annual risk-free rate
annual_risk_free_rate = 0.02  # 2% risk-free rate

# Calculate daily risk-free rate
risk_free_rate_daily = annual_risk_free_rate / trading_days_in_a_year

# Calculate Sharpe Ratio using annualized returns and annualized standard deviation
sharpe_ratio = (annual_average_return -
                annual_risk_free_rate) / annualized_std_dev

print(f"Sharpe Ratio: {sharpe_ratio}")

# Alternatively: Excess return directly on daily returns for Sharpe Ratio
excess_daily_return = df['daily_return'] - risk_free_rate_daily
sharpe_ratio_alternative = np.sqrt(
    trading_days_in_a_year) * excess_daily_return.mean() / excess_daily_return.std()

print(f"Alternative Sharpe Ratio: {sharpe_ratio_alternative}")
