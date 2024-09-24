import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, skewnorm
from metrics import calculate_std_dev


def plot_return_series(returns):
    # Plotting the return series as histogram
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
    average_return = returns.mean()

    # Plotting the daily returns
    plt.figure(facecolor='#f7e9e1')
    plt.hist(returns*100, bins=50, alpha=0.7, density=True,
             label='Daily Returns', histtype='bar', rwidth=0.8, color='#413b3c')

    # Calculating x and y values for the normal distribution curve
    x = np.linspace(min(returns*100), max(returns*100), 100)
    y = norm.pdf(x, average_return*100, std_dev*100)

    # Plotting the normal distribution curve
    plt.plot(x, y, color='#de4d39', label='Normal Distribution', linewidth=2)

    lower_bound_68 = average_return - std_dev
    upper_bound_68 = average_return + std_dev

    # Adding vertical lines for the average and bounds
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

    # Annotating the vertical lines with their literal values, adjusted to plot lower on the y-axis
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

    # Adding labels and title
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
    # Calculate the skewness of daily returns
    skewness_value = returns.skew()
    average_returns = returns.mean()
    std_dev = calculate_std_dev(returns)

    # Plotting the daily returns with skewness
    plt.figure(facecolor='#f7e9e1')
    # Plotting the histogram of daily returns
    plt.hist(returns*100, bins=50, alpha=0.7, density=True,
             label='Daily Returns', color='#413b3c')

    # Calculating x values for the distribution curves
    x = np.linspace(min(returns*100), max(returns*100), 100)

    # Normal distribution curve
    y_norm = norm.pdf(x, average_returns*100, std_dev*100)
    plt.plot(x, y_norm, color='#de4d39',
             label='Normal Distribution', linewidth=2)

    # Skew-normal distribution curve
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

    # Saving the figure with improved styling
    plt.savefig('skew.png')
