import psycopg2

from dotenv import load_dotenv
import os


import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


load_dotenv()

conn = psycopg2.connect(
    dbname=os.environ.get("DB_DB"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PW"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT")
)


# Configure Instrument Spec (BTC)
symbolname = 'BTC'

contract_unit = 1
trading_days_in_year = 365


# ByBit fees
# fee_perc = 0.1 #spot
fee_perc = 0.055  # perp & futures

# convert percentage to decimal
fee = fee_perc / 100


# Configure Account Spec
trading_capital = 10_000
annual_perc_risk_target = 0.20


# Confgure Strategy Spec
resample_period = '1D'


cur = conn.cursor()
cur.execute(f"""
    SELECT ohlcv.time_close, ohlcv.close
    FROM ohlcv
    JOIN coins ON ohlcv.coin_id = coins.id
    WHERE coins.symbol = '{symbolname}'
    ORDER BY ohlcv.time_close ASC;
""")
rows = cur.fetchall()
cur.close()
conn.close()

current_price = rows[-1][-1]
print(f'current {symbolname} current_price', current_price)
print(f'contract value', current_price * contract_unit, '\n')


df = pd.DataFrame(rows, columns=['time_close', 'close'])

df['time_close'] = pd.to_datetime(df['time_close'])
if not pd.api.types.is_datetime64_any_dtype(df['time_close']):
    df['time_close'] = pd.to_datetime(df['time_close'])
df.set_index('time_close', inplace=True)
df.sort_values(by='time_close', inplace=True)

df = df.resample(resample_period).last()

df['instr_perc_returns'] = df['close'].pct_change(fill_method=None).dropna()
df['instr_perc_returns_vol'] = df['instr_perc_returns'].ewm(span=35, min_periods=10).std()


fast_lookback = 8
slow_lookback = fast_lookback * 4
df['ema_fast'] = df['close'].ewm(span=fast_lookback, min_periods=fast_lookback).mean()
df['ema_slow'] = df['close'].ewm(span=slow_lookback, min_periods=slow_lookback).mean()
df['raw_forecast'] = df['ema_fast'] - df['ema_slow']

df['instr_price_returns'] = df['close'].diff()
df['instr_price_returns_vol'] = df['instr_price_returns'].ewm(span=35, min_periods=10).std()
df['fc_vol_adj'] = df['raw_forecast'] / df['instr_price_returns_vol'].ffill()


abs_values = df['fc_vol_adj'].abs().expanding(min_periods=trading_days_in_year * 2)
df['avg_abs_value'] = abs_values.median()

target_avg = 10.0
df['scaling_factor'] = target_avg / df['avg_abs_value']
df['scaling_factor'] = df['scaling_factor'].bfill()

df['scaled_forecast'] = (df['fc_vol_adj'] * df['scaling_factor'])
df['capped_forecast'] = df['scaled_forecast'].clip(lower=-20, upper=20)


annual_cash_risk_target = trading_capital * annual_perc_risk_target
daily_cash_risk = annual_cash_risk_target / np.sqrt(trading_days_in_year)
for index, row in df.iterrows():
    annual_cash_risk_target = trading_capital * annual_perc_risk_target
    daily_cash_risk = annual_cash_risk_target / np.sqrt(trading_days_in_year)

    notional_per_contract = (row['close'] * 1 * contract_unit)

    daily_usd_vol = notional_per_contract * row['instr_perc_returns_vol']
    df.at[index, 'daily_usd_vol'] = daily_usd_vol

    units_needed = daily_cash_risk / daily_usd_vol
    df.at[index, 'units_needed'] = units_needed

    forecast = row['capped_forecast']
    pos_size_contracts = units_needed * forecast / target_avg
    df.at[index, 'pos_size_contracts'] = pos_size_contracts

    notional_pos = pos_size_contracts * notional_per_contract
    df.at[index, 'notional_pos'] = notional_pos

    daily_usd_fees = notional_pos * fee
    df.at[index, 'daily_usd_fees'] = daily_usd_fees


# Calculating Turnover
df['unit_value'] = df['close'] * contract_unit * 0.01
daily_unit_risk = df['unit_value'] * df['instr_perc_returns_vol'] * 100

avg_pos = daily_cash_risk / daily_unit_risk
# print('avg position', avg_pos)

positions = df['pos_size_contracts']
actual_positions = positions.resample(resample_period).last()
avg_positions = avg_pos.reindex(actual_positions.index, method='ffill')

positions_normalised = actual_positions / avg_positions.ffill()
avg_daily_turnover = positions_normalised.diff().abs().mean()
# print('avg_daily_turnover', avg_daily_turnover)

ann_turnover = avg_daily_turnover * trading_days_in_year
# print('ann_turnover', ann_turnover)


# Calculating Performance
strat_raw_usd_returns = df['pos_size_contracts'].shift(1) * df['close'].diff()
df['instr_returns'] = df['close'].diff()
df['strat_raw_usd_returns'] = strat_raw_usd_returns.fillna(0)

# deduct fees
strat_usd_returns = df['strat_raw_usd_returns'] - df['daily_usd_fees']
df['strat_usd_returns'] = strat_usd_returns


df['daily_usd_pnl'] = strat_usd_returns
df['cumulative_usd_pnl'] = strat_usd_returns.cumsum()


strat_daily_perc_returns = df['close'].pct_change(fill_method=None)
df['daily_perc_pnl'] = strat_daily_perc_returns
strat_daily_cum_perc_returns = strat_daily_perc_returns.cumsum()
df['cumulative_perc_pnl'] = strat_daily_cum_perc_returns

strat_pct_returns = (strat_usd_returns / trading_capital) * 100
strat_tot_return = strat_pct_returns.sum()
strat_mean_ann_return = strat_pct_returns.mean() * trading_days_in_year

strat_std_dev = strat_pct_returns.ewm(35, min_periods=10).std()
strat_sr = np.sqrt(trading_days_in_year) * (strat_pct_returns.mean() / strat_std_dev)


print('Strategy Total Return', strat_tot_return)
print('Strategy Avg. Annual Return', strat_mean_ann_return)
print('Strategy Daily Volatility', strat_std_dev.iloc[-1])
print('Strategy Sharpe Ratio', strat_sr.iloc[-1], '\n')

print('Fees paid', df['daily_usd_fees'].sum(), '\n')


def plot_cum_pnl(pnl_column):
    _, ax = plt.subplots(figsize=(20, 12), facecolor='#f7e9e1')

    ax.plot(df['close'].index, df[pnl_column], color='#de4d39')
    ax.set_title(f'{pnl_column} {symbolname}')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.tight_layout()
    plt.savefig(f'{symbolname}_{pnl_column}.png', dpi=300)


# plot_cum_pnl('cumulative_usd_pnl')


def plot(column_name1, column_name2):
    _, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, figsize=(20, 24),
                                           facecolor='#f7e9e1',
                                           gridspec_kw={'height_ratios': [2, 1, 1, 1]})

    instr_cumulative_perc_returns = df['instr_perc_returns'].cumsum()
    instr_mean_ret = df['instr_perc_returns'].mean()
    instr_vol = df['instr_perc_returns'].ewm(35, min_periods=10).std()
    ann_instr_sharpe = np.sqrt(trading_days_in_year) * (instr_mean_ret / instr_vol)

    print('Instr Daily Mean Return', instr_mean_ret)
    print('Instr Daily Volatility', instr_vol.iloc[-1])
    print('Instr Ann. Sharpe Ratio', ann_instr_sharpe.iloc[-1], '\n')

    ax1.plot(df['close'].index, instr_cumulative_perc_returns * 100, color='#de4d39', label=f'Price {symbolname}')
    ax1.set_title(f'Cum. Percent Returns {symbolname}')
    ax1.set_ylabel('% Returns')
    ax1.text(
        0.05, 0.95,
        (
            f"{'Ann. SR:':<15}{ann_instr_sharpe.iloc[-1]:>16.2f}\n"
            f"{'Ann. std_dev(%):':<15}{(np.sqrt(trading_days_in_year) * instr_vol.iloc[-1] * 100):>10.2f}\n"
            f"{'Cum. ret(%):':<15}{(instr_cumulative_perc_returns.iloc[-1] * 100):>13.0f}"
        ),
        transform=ax1.transAxes,
        fontsize=20,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.5)
    )

    ax2.plot(df['close'].index, df['capped_forecast'], color='#de4d39', label=f'Forecast EMA {fast_lookback}_{slow_lookback}')
    ax2.axhline(y=0, color='#100d16', linestyle='--', label='Zero Line')
    ax2.set_title(f'Forecast EMA {fast_lookback}_{slow_lookback}')
    ax2.set_ylabel('Forecast')
    ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    ax3.plot(df['close'].index, df[column_name1], color='#de4d39', label=column_name1)
    ax3.set_title(column_name1)
    ax3.set_ylabel(column_name1)

    ax4.plot(df['close'].index, df[column_name2], color='#de4d39', label=column_name2)
    ax4.set_title(column_name2)
    ax4.set_xlabel('Time')
    ax4.set_ylabel(column_name2)
    ax4.text(
        0.05, 0.95,
        (
            f"{'SR:':<15}{strat_sr.iloc[-1]:>21.2f}\n"
            f"{'Ann. std_dev(%):':<15}{(np.sqrt(trading_days_in_year) * strat_std_dev.iloc[-1]):>11.2f}\n"
            f"{'Ann. Turnover:':<15}{ann_turnover:>15.0f}"
        ),
        transform=ax4.transAxes,
        fontsize=20,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.5)
    )

    plt.tight_layout()
    plt.savefig(f'{symbolname}_plots.png', dpi=300)


plot('daily_perc_pnl', 'cumulative_usd_pnl')
