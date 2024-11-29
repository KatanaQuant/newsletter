from metrics import calculate_std_dev
from metrics import calculate_sharpe_ratio, annualise_sharpe_ratio
from metrics import calculate_cumulative_returns
import numpy as np
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)


# Function to generate synthetic returns
def generate_returns(mu, sigma, periods):
    return np.random.normal(mu, sigma, periods)


# Parameters for two strategies
periods = 1500
annual_return_strategy1 = 0.07  # 7% annual return
annual_return_strategy2 = 0.12  # 12% annual return
annual_volatility_strategy1 = 0.12  # 12% annual volatility
annual_volatility_strategy2 = 0.24  # 24% annual volatility

trading_days_in_a_year = 365

# Calculate daily returns from annual returns
strategy1_mu = (1 + annual_return_strategy1) ** (1 /
                                                 trading_days_in_a_year) - 1
strategy2_mu = (1 + annual_return_strategy2) ** (1 /
                                                 trading_days_in_a_year) - 1

# Calculate daily volatilities from annual volatilities
strategy1_sigma = annual_volatility_strategy1 / np.sqrt(trading_days_in_a_year)
strategy2_sigma = annual_volatility_strategy2 / np.sqrt(trading_days_in_a_year)

# Generate returns
returns1 = generate_returns(strategy1_mu, strategy1_sigma, periods)
returns2 = generate_returns(strategy2_mu, strategy2_sigma, periods)

# Calculate cumulative returns
cumulative_returns1 = calculate_cumulative_returns(returns1)
cumulative_returns2 = calculate_cumulative_returns(returns2)

sharpe1 = annualise_sharpe_ratio(calculate_sharpe_ratio(returns1))
sharpe2 = annualise_sharpe_ratio(calculate_sharpe_ratio(returns2))

print('Sharpe Ratio of Strategy 1: {:.2f}'.format(sharpe1))
print('Sharpe Ratio of Strategy 2: {:.2f}'.format(sharpe2))
print('\n')

usd_bet = 10_000
risk1 = usd_bet * annual_volatility_strategy1
risk2 = usd_bet * annual_volatility_strategy2

print('Returns of Strategy 1: ${:,.2f}'.format(
    usd_bet * annual_return_strategy1))
print('Risk of Strategy 1: ${:,.2f}'.format(risk1))
print('\n')

print('Returns of Strategy 2: ${:,.2f}'.format(
    usd_bet * annual_return_strategy2))
print('Risk of Strategy 2: ${:,.2f}'.format(risk2))
print('\n')


scale_factor = risk2 / risk1
print('Scale Factor: {}'.format(scale_factor))
print('\n')

print('Scaled Returns of Strategy 1: ${:,.2f}'.format(
    usd_bet * annual_return_strategy1 * scale_factor))
print('Risk of Scaled Strategy 1: ${:,.2f}'.format(risk1 * scale_factor))
print('\n')
print('Returns of Strategy 2: ${:,.2f}'.format(
    usd_bet * annual_return_strategy2))
print('Risk of Strategy 2: ${:,.2f}'.format(risk2))
print('\n')

plt.figure(figsize=(14, 7), facecolor='#f7e9e1')

plt.subplot(1, 2, 1)
plt.plot(cumulative_returns1, label='Strategy 1 - Lower Risk', color='#de4d39')
plt.plot(cumulative_returns2, label='Strategy 2 - Higher Risk', color='#d3d3d3')
plt.title('Equity Curves of Two Synthetic Strategies')
plt.xlabel('Time')
plt.ylabel('Equity Value')
plt.legend()


plt.tight_layout()
# plt.savefig('eq_curves_synth.png')

plt.subplot(1, 2, 2)
strategies = ['Strategy 1', 'Strategy 2']
sharpe_ratios = [sharpe1, sharpe2]
plt.bar(strategies, sharpe_ratios, color=['#de4d39', '#d3d3d3'])
plt.title('Sharpe Ratios')
plt.ylabel('Sharpe Ratio')

plt.tight_layout()
plt.savefig('eq_vs_sr.png')
