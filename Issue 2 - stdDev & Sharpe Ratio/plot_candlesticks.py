import pandas as pd
import mplfinance as mpf

filepath = 'stdDev_and_SR.xlsx'
df = pd.read_excel(filepath, index_col='timestamp', parse_dates=True)
df.sort_index(inplace=True)

market_colors = mpf.make_marketcolors(up='#de4d39', down='#413b3c', edge='inherit',
                                      wick={'up': '#de4d39', 'down': '#413b3c'}, volume='gray', ohlc='i')

s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=market_colors,
                       figcolor='#f7e9e1', gridcolor='#100d16', gridstyle='--',
                       y_on_right=False)

mpf.plot(df,
         type='candle',
         style=s,
         volume=True,
         title=dict(title='BTC/USDT Last 25 Days', color='#100d16'),
         savefig=dict(fname='btcusdt_klines.png', facecolor='#f7e9e1'))
