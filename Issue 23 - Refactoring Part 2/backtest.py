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


# calculate signals
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

rebalance_err_threshold = 10  # percentage
# error_thresh_dec = 10 / 100

# simulate trading the signals
annual_cash_risk_target = trading_capital * annual_perc_risk_target
daily_cash_risk = annual_cash_risk_target / np.sqrt(trading_days_in_year)

df['rebalanced_pos_contracts'] = np.nan

slippage_percent = 0.05
slippage_percent_dec = slippage_percent / 100
# slippage_basis_points = 1


for index, row in df.iterrows():
    # calculate units needed based on volatility and risk-target
    notional_per_contract = (row['close'] * 1 * contract_unit)
    daily_usd_vol = notional_per_contract * row['instr_perc_returns_vol']
    units_needed = daily_cash_risk / daily_usd_vol

    # adjust units needed based on forecast
    forecast = row['capped_forecast']
    ideal_pos_contracts = units_needed * forecast / target_avg
    ideal_pos_notional = ideal_pos_contracts * notional_per_contract

    # simulate trading
    if df.index.get_loc(index) > 0:
        prev_idx = df.index[df.index.get_loc(index) - 1]
        current_pos_contracts = df.at[prev_idx, 'rebalanced_pos_contracts']

        if np.isnan(current_pos_contracts):
            current_pos_contracts = 0

        contract_diff = ideal_pos_contracts - current_pos_contracts
        contract_deviation = abs(contract_diff) / abs(ideal_pos_contracts) * 100

        # we're trading
        if contract_deviation > rebalance_err_threshold:
            if ideal_pos_contracts > 0:
                position_direction = 1
            else:
                position_direction = -1
            df.at[index, 'position_direction'] = position_direction

            slippage_amount_per_contract = row['close'] * slippage_percent_dec
            close_slipped = row['close'] + slippage_amount_per_contract if position_direction >= 0 else row['close'] - slippage_amount_per_contract
            df.at[index, 'close_slipped'] = close_slipped

            slippage_paid = abs(contract_diff) * slippage_amount_per_contract * contract_unit
            df.at[index, 'slippage_paid'] = slippage_paid

            rebalanced_pos_contracts = ideal_pos_contracts
            notional_traded = contract_diff * notional_per_contract
        else:
            slippage_paid = 0
            rebalanced_pos_contracts = current_pos_contracts
            notional_traded = 0

        fees_paid = abs(notional_traded) * fee

        df.at[index, 'slippage_paid'] = slippage_paid
        df.at[index, 'current_pos_contracts'] = current_pos_contracts
        df.at[index, 'contract_diff'] = contract_diff
        df.at[index, 'contract_deviation'] = contract_deviation
        df.at[index, 'rebalanced_pos_contracts'] = rebalanced_pos_contracts
        df.at[index, 'notional_traded'] = notional_traded
    else:
        fees_paid = 0

    df.at[index, 'notional_per_contract'] = notional_per_contract
    df.at[index, 'daily_usd_vol'] = daily_usd_vol
    df.at[index, 'units_needed'] = units_needed
    df.at[index, 'ideal_pos_contracts'] = ideal_pos_contracts
    df.at[index, 'ideal_pos_notional'] = ideal_pos_notional
    df.at[index, 'fees_paid'] = fees_paid

# Calculating Turnover
df['unit_value'] = df['close'] * contract_unit * 0.01
daily_unit_risk = df['unit_value'] * df['instr_perc_returns_vol'] * 100

avg_pos = daily_cash_risk / daily_unit_risk

actual_positions = df['rebalanced_pos_contracts'].resample(resample_period).last()
avg_positions = avg_pos.reindex(actual_positions.index, method='ffill')
positions_normalised = actual_positions / avg_positions.ffill()

avg_daily_turnover = positions_normalised.diff().abs().mean()
ann_turnover = avg_daily_turnover * trading_days_in_year


# Calculating Performance
instr_raw_returns = df['instr_price_returns']
strat_raw_usd_returns = df['rebalanced_pos_contracts'].shift(1) * instr_raw_returns
df['strat_raw_usd_returns'] = strat_raw_usd_returns.fillna(0)

# Deduct fees
strat_usd_returns = df['strat_raw_usd_returns'] - df['fees_paid']
df['strat_usd_returns_after_fees'] = strat_usd_returns
df['strat_usd_returns_postcost'] = df['strat_usd_returns_after_fees']


# Deduct slippage
strat_usd_returns = df['strat_usd_returns_after_fees'] - df['slippage_paid']
df['strat_usd_returns_after_slippage'] = strat_usd_returns
df['strat_usd_returns_postcost'] = df['strat_usd_returns_after_slippage']


# Deduct funding
funding = pd.read_csv('BTC_funding_rates.csv')
funding['time_close'] = pd.to_datetime(funding['time_close'])
if not pd.api.types.is_datetime64_any_dtype(funding['time_close']):
    funding['time_close'] = pd.to_datetime(funding['time_close'])
funding.set_index('time_close', inplace=True)
funding.sort_values(by='time_close', inplace=True)

funding = funding.resample(resample_period).sum()
funding['funding'] = funding['fundingRate']
funding = funding['funding']


df = df.join(funding, how='left')
df['funding'] = df['funding'].fillna(0)
df['funding_paid'] = df['ideal_pos_notional'].shift(1) * df['funding']

strat_usd_returns = df['strat_usd_returns_postcost'] - df['funding_paid']
df['strat_usd_returns_after_funding'] = strat_usd_returns
df['strat_usd_returns_postcost'] = df['strat_usd_returns_after_funding']


##


# Calculate SR
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

strat_raw_usd_std_dev_pre = strat_raw_usd_returns.ewm(35, min_periods=10).std()
strat_raw_usd_std_dev_post = strat_usd_returns.ewm(35, min_periods=10).std()

rolling_pre_cost_sr = np.sqrt(trading_days_in_year) * (strat_raw_usd_returns.mean() / strat_raw_usd_std_dev_pre)
rolling_post_cost_sr = np.sqrt(trading_days_in_year) * (strat_usd_returns.mean() / strat_raw_usd_std_dev_post)
strat_rolling_trading_costs_sr = rolling_pre_cost_sr - rolling_post_cost_sr

# Create and print performance sheet
print('Strategy Total Return', strat_tot_return)
print('Strategy Avg. Annual Return', strat_mean_ann_return)
print('Strategy Daily Volatility', strat_std_dev.iloc[-1])
print('Strategy Sharpe Ratio', strat_sr.iloc[-1], '\n')

print('Fees paid', df['fees_paid'].sum())
print('Slippage paid', df['slippage_paid'].sum())
print('Funding paid', df['funding_paid'].sum(), '\n')


print('Strategy Ann. Turnover', ann_turnover, '\n')

print('Pre-Cost SR', rolling_pre_cost_sr.iloc[-1])
print('Post-Cost SR', rolling_post_cost_sr.iloc[-1])
print('Risk-Adjusted Costs', strat_rolling_trading_costs_sr.iloc[-1], '\n')


def plot_ann_rolling_trading_costs_sr(rolling_sr):
    _, ax = plt.subplots(figsize=(20, 12), facecolor='#f7e9e1')

    ax.plot(rolling_sr.index, rolling_sr, color='#de4d39')
    ax.set_title(f'Ann. Rolling Trading Costs SR {symbolname}')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.tight_layout()
    plt.savefig(f'{symbolname}_rolling_trading_costs_sr.png', dpi=300)


# plot_ann_rolling_trading_costs_sr(strat_rolling_trading_costs_sr)


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

# pos_debug_df = df[['ideal_pos_contracts', 'current_pos_contracts', 'contract_diff', 'contract_deviation', 'traded', 'rebalanced_pos_contracts', 'notional_traded']]
# pos_debug_df.to_csv('debug.csv')


assert (strat_tot_return == 958.3412684422372)
assert (strat_mean_ann_return == 65.7261486248434)
assert (strat_std_dev.iloc[-1] == 1.8145849936803375)
assert (strat_sr.iloc[-1] == 1.8958956813694106)

assert (df['fees_paid'].sum() == 1038.6238698915147)
assert (df['slippage_paid'].sum() == 944.2035180831953)
assert (df['funding_paid'].sum() == 3130.3644113437113)


assert (ann_turnover == 37.672650094739545)

assert (rolling_pre_cost_sr.iloc[-1] == 1.9914208916281093)
assert (rolling_post_cost_sr.iloc[-1] == 1.8958956813694112)

assert (strat_rolling_trading_costs_sr.iloc[-1] == 0.09552521025869809)
