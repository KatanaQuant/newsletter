import matplotlib.pyplot as plt

import numpy as np

from scipy.stats import norm, skewnorm

from metrics import calculate_std_dev
from metrics import calculate_cumulative_returns
from metrics import calculate_average_return
from metrics import calculate_skewness
from metrics import calculate_drawdown


def plot_return_series_histogram(returns):
    plt.figure(facecolor='#f7e9e1')
    time_indices = range(len(returns))
    plt.bar(time_indices, returns, color=[
            '#413b3c' if x > 0 else '#de4d39' for x in returns])
    plt.axhline(0, color='gray', linestyle='--')

    plt.xlabel('Time')
    plt.ylabel('Daily Returns')
    plt.title('Daily Returns Over Time')
    plt.savefig('return_series_histogram.png')


def plot_return_distribution(returns):
    std_dev = calculate_std_dev(returns)
    average_return = calculate_average_return(returns)

    plt.figure(facecolor='#f7e9e1')
    plt.hist(returns*100, bins=50, alpha=0.7, density=True,
             label='Daily Returns', histtype='bar', rwidth=0.8, color='#413b3c')

    x = np.linspace(min(returns*100), max(returns*100), 100)
    y = norm.pdf(x, average_return*100, std_dev*100)

    plt.plot(x, y, color='#de4d39', label='Normal Distribution', linewidth=2)

    lower_bound_68 = average_return - std_dev
    upper_bound_68 = average_return + std_dev

    plt.axvline(average_return*100, color='#100d16',
                linestyle='--', linewidth=2, label='Average Daily Return')
    plt.axvline(lower_bound_68*100, color='#de4d39', linestyle='--',
                linewidth=2, label='Lower Bound 68%')
    plt.axvline(upper_bound_68*100, color='#de4d39', linestyle='--',
                linewidth=2, label='Upper Bound 68%')

    lower_bound_95 = average_return - std_dev * 2
    upper_bound_95 = average_return + std_dev * 2

    plt.axvline(lower_bound_95*100, color='#de4d39', linestyle='--',
                linewidth=2, label='Lower Bound 95%')
    plt.axvline(upper_bound_95*100, color='#de4d39', linestyle='--',
                linewidth=2, label='Upper Bound 95%')

    plt.text(average_return*100, plt.ylim()
             [1]*0.45, f'{average_return*100:.2f}%', ha='right', color='#100d16')
    plt.text(lower_bound_68*100, plt.ylim()
             [1]*0.40, f'{lower_bound_68*100:.2f}%', ha='right', color='#100d16')
    plt.text(upper_bound_68*100, plt.ylim()
             [1]*0.40, f'{upper_bound_68*100:.2f}%', ha='left', color='#100d16')
    plt.text(lower_bound_95*100, plt.ylim()
             [1]*0.45, f'{lower_bound_95*100:.2f}%', ha='right', color='#100d16')
    plt.text(upper_bound_95*100, plt.ylim()
             [1]*0.45, f'{upper_bound_95*100:.2f}%', ha='left', color='#100d16')

    plt.xlabel('Daily Returns (%)', fontsize=12, color='#100d16')
    plt.ylabel('Probability Density', fontsize=12, color='#100d16')
    plt.title('Daily BTC/USDT Returns stdDev +1, +2',
              fontsize=14, color='#100d16')
    plt.legend()

    plt.grid(True, which='both', linestyle='--',
             linewidth=0.5, color='#100d16')
    plt.tick_params(colors='#100d16')

    plt.savefig('return_distribution.png')


def plot_skew(returns):
    skewness_value = calculate_skewness(returns)
    average_returns = calculate_average_return(returns)
    std_dev = calculate_std_dev(returns)

    plt.figure(facecolor='#f7e9e1')
    plt.hist(returns*100, bins=50, alpha=0.7, density=True,
             label='Daily Returns', color='#413b3c')

    x = np.linspace(min(returns*100), max(returns*100), 100)

    y_norm = norm.pdf(x, average_returns*100, std_dev*100)
    plt.plot(x, y_norm, color='#de4d39',
             label='Normal Distribution', linewidth=2)

    a = skewness_value
    y_skew = skewnorm.pdf(x, a, loc=average_returns*100, scale=std_dev*100)
    plt.plot(x, y_skew, color='blue', label='Skew-Normal Distribution',
             linestyle='--', linewidth=2)

    plt.xlabel('Daily Returns (%)', fontsize=12, color='#100d16')
    plt.ylabel('Probability Density', fontsize=12, color='#100d16')
    plt.title('Daily BTC/USDT Returns with Skewness',
              fontsize=14, color='#100d16')
    plt.legend()

    plt.grid(True, which='both', linestyle='--',
             linewidth=0.5, color='#100d16')
    plt.tick_params(colors='#100d16')

    plt.savefig('skew.png')


def plot_equity_curve(returns, tickername):
    cumulative_returns = calculate_cumulative_returns(returns)

    plt.figure(facecolor='#f7e9e1')
    time_indices = range(len(cumulative_returns))
    plt.plot(time_indices, cumulative_returns, color='#de4d39', linewidth=2)

    plt.xlabel('Time')
    plt.ylabel('Cumulative Returns')
    plt.title('Equity Curve Over Time')
    plt.grid(True, which='both', linestyle='--',
             linewidth=0.5, color='#100d16')
    plt.tick_params(colors='#100d16')

    plt.savefig(f'equity_curve_{tickername}.png')


def plot_drawdown(returns, tickername):
    drawdown_series = calculate_drawdown(returns) * -1

    plt.figure(facecolor='#f7e9e1')
    time_indices = range(len(drawdown_series))
    plt.fill_between(time_indices, drawdown_series, color='#de4d39', alpha=0.5)

    plt.xlabel('Time')
    plt.ylabel('Drawdown')
    plt.title('Drawdown Over Time')
    plt.grid(True, which='both', linestyle='--',
             linewidth=0.5, color='#100d16')
    plt.tick_params(colors='#100d16')

    plt.savefig(f'drawdown_{tickername}.png')


def plot_equity_and_drawdown(returns, tickername):
    cumulative_returns = calculate_cumulative_returns(returns)
    drawdown_series = calculate_drawdown(returns)

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='#f7e9e1')

    time_indices = range(len(cumulative_returns))
    ax1.plot(time_indices, cumulative_returns, color='#de4d39', linewidth=2)
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Cumulative Returns')
    ax1.set_title('Equity Curve Over Time')
    ax1.grid(True, which='both', linestyle='--',
             linewidth=0.5, color='#100d16')
    ax1.tick_params(colors='#100d16')

    ax2.fill_between(time_indices, drawdown_series, color='#de4d39', alpha=0.7)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Drawdown')
    ax2.set_title('Drawdown Over Time')
    ax2.grid(True, which='both', linestyle='--',
             linewidth=0.5, color='#100d16')
    ax2.tick_params(colors='#100d16')

    plt.tight_layout()
    plt.savefig(f'equity_and_drawdown_{tickername}.png')
