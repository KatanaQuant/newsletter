import pandas as pd
import numpy as np


def read_ohlcv_from_csv(filepath):
    df = pd.read_excel(filepath)

    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def calculate_daily_returns(df):
    df['daily_return'] = df['close'].pct_change()
    return df['daily_return'].dropna()


filepath = 'stdDev.xlsx'
df = read_ohlcv_from_csv(filepath)

daily_returns = calculate_daily_returns(df)
std_dev = np.std(daily_returns)

print(f'stdDev: {std_dev}')
print(f'stdDev%: {std_dev*100: .2f}%')
print('')

average_daily_return = daily_returns.mean()
print(f'Avg daily return {average_daily_return*100: .2f}%')
