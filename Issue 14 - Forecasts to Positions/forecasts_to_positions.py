import numpy as np
import pandas as pd

import psycopg2

from dotenv import load_dotenv
import os


load_dotenv()


conn = psycopg2.connect(
    dbname=os.environ.get("DB_DB"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PW"),
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT")
)

symbolname = 'BTC'

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

price = rows[-1][-1]
date = rows[-1][0]
print(f'Current {symbolname} price as of {date}', price)

df = pd.DataFrame(rows, columns=['time_close', 'close'])
df['time_close'] = pd.to_datetime(df['time_close']).dt.strftime('%Y-%m-%d')
df.set_index('time_close', inplace=True)
df['perc_change'] = df['close'].pct_change()
df['perc_change_ewm_vol'] = df['perc_change'].ewm(adjust=True, span=35, min_periods=10).std()

daily_price_vol_perc = df['perc_change_ewm_vol'].iloc[-1]
print(f'Daily price VOL %', daily_price_vol_perc, '\n')

contract_unit = 1
units_bought = 1
notional_exp = units_bought * price * contract_unit
print(f'Notional exposure of {units_bought} unit {symbolname}', notional_exp)

daily_vol_risk = notional_exp * daily_price_vol_perc
print(f'PnL for {daily_price_vol_perc * 100}% move owning {units_bought} units {symbolname}', daily_vol_risk, '\n')


trading_capital = 10_000
print(f'Trading capital', trading_capital)
annual_perc_risk_target = 0.20
annual_cash_risk_target = trading_capital * annual_perc_risk_target
print(f'Annual cash risk target', annual_cash_risk_target)

trading_days_in_year = 365
daily_cash_risk = annual_cash_risk_target / np.sqrt(trading_days_in_year)
print(f'Daily cash risk target', daily_cash_risk, '\n')


units_needed_for_daily_risk = daily_cash_risk / daily_vol_risk
print(f'Units needed for daily risk', units_needed_for_daily_risk)

forecast = 13.439369
pos = units_needed_for_daily_risk * forecast / 10
print(f'Position size', pos)
