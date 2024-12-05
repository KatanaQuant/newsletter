from plots import plot_price_series
import numpy as np


def generate_gbm_price_series(S0, mu, sigma, T, N):
    """
    Generates a price series using Geometric Brownian Motion.

    Parameters:
    S0 : float : initial price
    mu : float : drift coefficient
    sigma : float : volatility coefficient
    T : float : total time
    N : int : number of time steps
    """

    dt = T / N
    t = np.linspace(0, T, N)
    W = np.random.standard_normal(size=N)
    W = np.cumsum(W) * np.sqrt(dt)
    X = (mu - 0.5 * sigma**2) * t + sigma * W
    S = S0 * np.exp(X)
    return S, t


def generate_ou_price_series(S0, theta, mu, sigma, T, N):
    """
    Generates a price series using the Ornstein-Uhlenbeck process.

    Parameters:
    S0 : float : initial price
    theta : float : speed of reversion
    mu : float : long-term mean
    sigma : float : volatility coefficient
    T : float : total time
    N : int : number of time steps
    """

    dt = T / N
    t = np.linspace(0, T, N)
    S = np.zeros(N)
    S[0] = S0
    for i in range(1, N):
        dW = np.random.normal(0, np.sqrt(dt))
        S[i] = S[i - 1] + theta * (mu - S[i - 1]) * dt + sigma * dW
    return S, t


def generate_sine_series(N, T, X, sigma):
    """
    Generates a trend of length N, sine wave amplitude X, plus Gaussian W scaled to std_dev (sigma * amplitude).

    Parameters:
    N : int : length of the series
    T : int : length of the trend cycle
    X : float : amplitude of the trend
    sigma : float : volatility
    """

    std_dev = sigma * X
    W = np.random.standard_normal(N) * std_dev

    half_amplitude = X * 0.5
    trend_step = X / T

    cycles = int(np.ceil(N / T))

    trend_up = list(np.arange(start=-half_amplitude, stop=half_amplitude, step=trend_step))
    trend_down = list(np.arange(start=half_amplitude, stop=-half_amplitude, step=-trend_step))
    trend = (trend_up + trend_down) * cycles
    trend = trend[:N]

    combined_price = W + trend

    # Apply exponential transformation to ensure positive prices
    positive_price_series = np.exp(combined_price)
    return positive_price_series, np.arange(N)


# Example usage GBM
S0 = 1  # initial price
mu = 0.1  # drift
sigma = 0.2  # volatility
T = 5.0  # 5 years
N = 365  # number of time steps (e.g., trading days in a year)

price_series, time_series = generate_gbm_price_series(S0, mu, sigma, T, N)
plot_price_series(time_series, price_series, 'gbm_price_series')


# Example usage OU
S0 = 1  # initial price
theta = 0.8  # speed of reversion (increase for faster reversion)
mu = 1  # long-term mean
sigma = 0.15  # volatility (adjust for more or less deviation)
T = 5.0  # total time (e.g., 1 year)
N = 365  # number of time steps (e.g., trading days in a year)

price_series, time_series = generate_ou_price_series(S0, theta, mu, sigma, T, N)
plot_price_series(time_series, price_series, 'ou_price_series')


# Example usage SINE
N = 365  # length of the series (e.g., trading days in a year)
T = 50  # length of the trend cycle
X = 1.0  # amplitude of the trend
sigma = 0.2  # scale of the volatility

price_series, time_series = generate_sine_series(N, T, X, sigma)
plot_price_series(time_series, price_series, 'sine_price_series')
