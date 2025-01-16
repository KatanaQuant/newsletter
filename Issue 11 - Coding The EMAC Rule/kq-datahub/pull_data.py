import matplotlib.pyplot as plt
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


cur = conn.cursor()
cur.execute("""
    SELECT ohlcv.time_close, ohlcv.close
    FROM ohlcv
    JOIN coins ON ohlcv.coin_id = coins.id
    WHERE coins.symbol = 'BTC';
""")

rows = cur.fetchall()
cur.close()
conn.close()


df = pd.DataFrame(rows, columns=['time_close', 'close'])
df['ema_fast'] = df['close'].ewm(span=8).mean()
df['ema_slow'] = df['close'].ewm(span=32).mean()

# print(df.tail())

# df_plot = df.tail(80)

# plt.plot(df_plot['time_close'], df_plot['close'], label='close')
# plt.plot(df_plot['time_close'], df_plot['ema_fast'], label='ema_fast')
# plt.plot(df_plot['time_close'], df_plot['ema_slow'], label='ema_slow')
# plt.legend()
# plt.show()

df['ema_crossover'] = df['ema_fast'] - df['ema_slow']
print(df.tail())
