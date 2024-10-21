import numpy as np

TRADING_DAYS_IN_A_YEAR = 256


def calculate_cumulative_returns(returns):
    return returns.cumsum()
    # return (1 + returns).cumprod() - 1


def calculate_drawdown(returns):
    cumulative_returns = calculate_cumulative_returns(returns)
    cumulative_max = cumulative_returns.cummax()

    drawdown_series = cumulative_max - cumulative_returns
    drawdown_series = drawdown_series / (1 + cumulative_max)
    return drawdown_series


def calculate_average_return(returns):
    return returns.mean()


def calculate_std_dev(returns):
    return returns.std()


def annualise_std_dev(std_dev):
    return std_dev * np.sqrt(TRADING_DAYS_IN_A_YEAR)


def calculate_sharpe_ratio(returns):
    excess_return = calculate_average_return(returns)
    sharpe_ratio = excess_return / calculate_std_dev(returns)
    return sharpe_ratio


def annualise_sharpe_ratio(sharpe_ratio):
    return sharpe_ratio * np.sqrt(TRADING_DAYS_IN_A_YEAR)


def calculate_skewness(returns):
    return returns.skew()


def calculate_tail_ratios(returns):
    normalized_returns = returns - calculate_average_return(returns)

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
