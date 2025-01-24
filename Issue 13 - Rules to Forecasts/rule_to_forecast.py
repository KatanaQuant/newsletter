import pandas as pd

import psycopg2

from dotenv import load_dotenv
import os

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt


def create_plot(df, y_col, symbolname):
    fig, ax = plt.subplots(figsize=(20, 6), facecolor='#f7e9e1')
    ax.plot(df.index, df[y_col], color='#de4d39', label=y_col)
    ax.set_title(f'{symbolname} {y_col}')
    ax.set_ylabel(y_col)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    plt.tight_layout()
    plt.savefig(f'{symbolname}_{y_col}.png', dpi=300)
    plt.close(fig)


load_dotenv()


conn = psycopg2.connect(
    dbname=os.environ.get("DB_DB"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PW"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT")
)

symbolname = 'TRX'

cur = conn.cursor()
cur.execute(f"""
    SELECT ohlcv.time_close, ohlcv.close
    FROM ohlcv
    JOIN coins ON ohlcv.coin_id = coins.id
    WHERE coins.symbol = '{symbolname}';
""")

rows = cur.fetchall()
cur.close()
conn.close()

df = pd.DataFrame(rows, columns=['time_close', 'close'])
df['time_close'] = pd.to_datetime(df['time_close']).dt.strftime('%Y-%m-%d')
df.set_index('time_close', inplace=True)


fast_lookback = 8
slow_lookback = fast_lookback * 4

df['ema_fast'] = df['close'].ewm(span=fast_lookback).mean()
df['ema_slow'] = df['close'].ewm(span=slow_lookback).mean()
df['raw_forecast'] = df['ema_fast'] - df['ema_slow']
# create_plot(df, 'raw_forecast', symbolname)

# price_vol = df['close'].diff().rolling(25, min_periods=10).std()
df['price_vol'] = df['close'].ewm(span=35, min_periods=10).std()
df['fc_vol_adj'] = df['raw_forecast'] / df['price_vol']
# create_plot(df, 'fc_vol_adj', symbolname)
# print(f'Forecasts for {symbolname}')
# print(df[['close', 'raw_forecast', 'fc_vol_adj']].tail(5))

print(symbolname)
abs_values = df['fc_vol_adj'].abs().expanding(min_periods=720)
df['avg_abs_value'] = abs_values.median()
# print('avg_abs_val', df['avg_abs_value'].tail(5))
# create_plot(df, 'avg_abs_value', symbolname)


target_avg = 10.0
df['scaling_factor'] = target_avg / df['avg_abs_value']
df['scaling_factor'] = df['scaling_factor'].bfill()
# print(df[['close', 'raw_forecast', 'fc_vol_adj', 'scaling_factor']].tail(5))
# create_plot(df, 'scaling_factor', symbolname)


df['scaled_forecast'] = df['fc_vol_adj'] * df['scaling_factor']
df['capped_forecast'] = df['scaled_forecast'].clip(lower=-20, upper=20)
# create_plot(df, 'scaled_forecast', symbolname)
# create_plot(df, 'capped_forecast', symbolname)

print('avg_rescaled_abs_fc_capped', df['capped_forecast'].abs().mean())
print(df[['close', 'raw_forecast', 'fc_vol_adj', 'scaling_factor', 'capped_forecast']].tail(5))


fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(20, 12),
                               facecolor='#f7e9e1',
                               gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(df['close'].index, df['close'], color='#de4d39', label=f'Price {symbolname}')
ax1.set_yscale('log')
ax1.set_title(f'Price Curve {symbolname} (Log Scale)')

ax2.plot(df['close'].index, df['capped_forecast'], color='#de4d39', label=f'Forecast EMA {fast_lookback}_{slow_lookback}')
ax2.axhline(y=0, color='#100d16', linestyle='--', label='Zero Line')
ax2.set_title(f'Forecast EMA {fast_lookback}_{slow_lookback}')
ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

plt.tight_layout()
plt.savefig(f'{ſymbolname}_price_and_forecast.png', dpi=300)
