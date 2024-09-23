
import matplotlib.patches as mpatches
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt


def calculate_probability_of_outcome(target_outcome_count, total_outcome_count):
    return target_outcome_count / total_outcome_count


def calculate_win_percentage_needed_to_break_even(risk, reward):
    return risk / (risk + reward)


def calculate_risk_reward_ratio(risk, reward):
    return reward / risk


def calculate_ev(win_percentage, amount_won, amount_lost):
    return win_percentage * amount_won - (1 - win_percentage) * amount_lost


def simulate_coin_flip(bankroll, amount_won, amount_lost, win_percent, num_tries):
    bankrolls = [bankroll]
    for _ in range(num_tries):
        if np.random.rand() < win_percent:
            bankroll += amount_won
        else:
            bankroll -= amount_lost
        bankrolls.append(bankroll)
    return bankrolls


def monte_carlo_simulation(initial_bankroll, amount_won, amount_lost, win_percent, num_tries, num_simulations):
    busts = 0
    for _ in tqdm(range(num_simulations), desc="Simulating"):
        bankrolls = simulate_coin_flip(
            initial_bankroll, amount_won, amount_lost, win_percent, num_tries)
        plt.plot(bankrolls, alpha=0.5)
        if bankrolls[-1] <= 0:
            busts += 1
    plt.axhline(0, color='black')

    bust_percent = (busts / num_simulations) * 100
    plt.text(0.1, 0.1, f'{bust_percent:.2f}% of simulations went bust',
             transform=plt.gca().transAxes)

    ev = calculate_ev(win_percent, amount_won, amount_lost)
    rr = calculate_risk_reward_ratio(amount_won, amount_lost)

    info_text = f'EV: ${ev:.2f}, R:R: {rr:.2f}, Win Amount: ${
        amount_won}, Loss Amount: ${amount_lost}, Win%: {win_percent:.2f}'
    plt.gcf().suptitle(info_text, fontsize=8)

    legend_elements = [mpatches.Patch(label=f'Initial Bankroll: {initial_bankroll}'),
                       mpatches.Patch(label=f'# of Tries: {num_tries}'),
                       mpatches.Patch(label=f'# of Players: {num_players}')]

    plt.legend(handles=legend_elements, loc='upper left')

    plt.title('Equity Curves', fontsize=14)
    plt.xlabel('Number of Tries', fontsize=12)
    plt.ylabel('Bankroll', fontsize=12)
    plt.gca().tick_params()


amount_of_5_on_die = 1
sides_of_die = 6
probability_fraction = calculate_probability_of_outcome(
    amount_of_5_on_die, sides_of_die)

as_percent = probability_fraction * 100
print("{:.2f}% chance".format(as_percent))


amount_won = 110  # risk
amount_lost = 100  # reward
rr = calculate_risk_reward_ratio(amount_won, amount_lost)
print("{:.2f} units risked for every 1 unit won".format(rr))


print("{:.2f}% win needed to be breakeven".format(
    calculate_win_percentage_needed_to_break_even(amount_lost, amount_won) * 100))


win_percent = 0.5
loss_percent = 1 - win_percent
print("EV is ${}".format(calculate_ev(
    win_percent, amount_won, amount_lost)))

# Run the simulation
initial_bankroll = 100
num_tries = 300
num_players = 20
monte_carlo_simulation(initial_bankroll, amount_won,
                       amount_lost, win_percent, num_tries, num_players)

plt.savefig('./equity_curves.png')
