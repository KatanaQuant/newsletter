import numpy as np


def calculate_std_dev(returns):
    return returns.std()


def calculate_sharpe_ratio(returns):
    average_return = returns.mean()
    excess_return = average_return

    sharpe_ratio = excess_return / calculate_std_dev(returns)
    return sharpe_ratio


def annualise_sharpe_ratio(sharpe_ratio):
    trading_days_in_a_year = 365  # or 252 for stocks
    return sharpe_ratio * np.sqrt(trading_days_in_a_year)


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
