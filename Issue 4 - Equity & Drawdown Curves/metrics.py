import numpy as np

TRADING_DAYS_IN_A_YEAR = 256  # or 252 for stocks


def calculate_drawdown(returns):
    cumulative_returns = (1 + returns).cumprod() - 1

    running_max = (1 + returns).cumprod().cummax()
    drawdown_series = (cumulative_returns + 1) / running_max - 1
    # avg_drawdown = drawdown.mean()
    # max_drawdown = drawdown.min()

    return drawdown_series


def calculate_drawdown_carver(returns):
    cum_perc_return = returns.cumsum()
    max_cum_perc_return = cum_perc_return.rolling(len(returns)+1,
                                                  min_periods=1).max()
    drawdown_series = max_cum_perc_return - cum_perc_return
    # avg_drawdown = drawdown.mean()
    # max_drawdown = drawdown.max()

    return drawdown_series


def calculate_average_annual_return(daily_returns):
    daily_avg_returns = daily_returns.mean()
    return daily_avg_returns * TRADING_DAYS_IN_A_YEAR


def calculate_std_dev(returns):
    return returns.std()


def annualise_std_dev(std_dev):
    return std_dev * np.sqrt(TRADING_DAYS_IN_A_YEAR)


def calculate_sharpe_ratio(returns):
    average_return = returns.mean()
    excess_return = average_return

    sharpe_ratio = excess_return / calculate_std_dev(returns)
    return sharpe_ratio


def annualise_sharpe_ratio(sharpe_ratio):
    return sharpe_ratio * np.sqrt(TRADING_DAYS_IN_A_YEAR)


def calculate_skewness(returns):
    return returns.skew()


def calculate_tail_ratios(returns):
    normalized_returns = returns - returns.mean()

    # Calculate the left tail ratio
    percentile1 = np.percentile(normalized_returns, 1)
    percentile30 = np.percentile(normalized_returns, 30)
    left_tail_ratio = percentile1 / percentile30

    # Calculate the right tail ratio
    percentile70 = np.percentile(normalized_returns, 70)
    percentile99 = np.percentile(normalized_returns, 99)
    right_tail_ratio = percentile99 / percentile70

    # Calculate the relative left and right tail ratios
    symmetrical_ratio = 4.43
    relative_left_ratio = left_tail_ratio / symmetrical_ratio
    relative_right_ratio = right_tail_ratio / symmetrical_ratio

    return relative_left_ratio, relative_right_ratio
