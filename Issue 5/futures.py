# def calculate_drawdown_chanep(returns):
#     cumret = calculate_cum_compounded_returns(returns)

#     highwatermark = np.zeros(cumret.shape)
#     drawdown = np.zeros(cumret.shape)
#     drawdownduration = np.zeros(cumret.shape)

#     for t in np.arange(1, cumret.shape[0]):
#         highwatermark[t] = np.maximum(highwatermark[t-1], cumret[t])
#         drawdown[t] = (1 + cumret[t]) / (1 + highwatermark[t]) - 1
#         if drawdown[t] == 0:
#             drawdownduration[t] = 0
#         else:
#             drawdownduration[t] = drawdownduration[t-1] + 1

#     maxDD, i = np.min(drawdown), np.argmin(drawdown)
#     maxDDD = np.max(drawdownduration)
#     return maxDD, maxDDD, i, drawdown


daily_returns = df['price'].pct_change().dropna()

df['perc_returns'] = df['price'].pct_change().dropna()

df['notional_futures'] = df['underlying'] * 5
df['price_diff'] = df['price'] - df['price'].shift(1)
df['price_return'] = df['price_diff'] * 5
df['perc_returns'] = df['price_return'] / df['notional_futures']

daily_returns = df['perc_returns'].dropna()


def calculate_cumulative_returns(returns):
    return returns.cumsum()


def calculate_drawdown(returns):
    cum_perc_return = calculate_cumulative_returns(returns)
    max_cum_perc_return = cum_perc_return.rolling(len(returns)+1,
                                                  min_periods=1).max()
    drawdown_series = max_cum_perc_return - cum_perc_return
    return drawdown_series


def calculate_average_annual_return(returns):
    return calculate_average_return(returns) * TRADING_DAYS_IN_A_YEAR
