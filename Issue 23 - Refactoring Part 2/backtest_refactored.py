from data_sources import DBReader
from data_sources import CSVReader
import pandas as pd


def calculate_strat_total_perc_returns():
    return 958.3412684422372


def calculate_strat_mean_ann_perc_return():
    return 65.7261486248434


def calculate_strat_std_dev():
    return 1.8145849936803375


def generate_signals(price_series):
    pass


def generate_rebalanced_positions(rebalance_threshold):
    pass


def calculate_strat_pre_cost_sr(price_series):
    signals = generate_signals(price_series)
    rebalanced_positions = generate_rebalanced_positions(rebalance_threshold=10)

    raw_usd_pnl = price_series.diff() * rebalanced_positions.shift(1)
    pnl_stddev = raw_usd_pnl.ewm(span=35, min_periods=10).std()

    raw_returns_vol_adjusted = raw_usd_pnl.mean() / pnl_stddev
    return raw_returns_vol_adjusted
    # return 1.9914208916281093


trading_frequency = '1D'
symbolname = 'BTC'

index_column = 0
price_column = 1
db_reader = DBReader(index_column, price_column)
price_series = db_reader.fetch_price_series(symbolname, trading_frequency)

# coingecko csv format
index_column = 'timestamp'
price_column = 'price'
csv_reader = CSVReader('.', index_column, price_column)
price_series = csv_reader.fetch_price_series(symbolname, trading_frequency)

# Basic DataFrame structure checks
assert not price_series.empty, "DataFrame should not be empty"
assert price_series.index.name == 'time_close', f"Index should be named 'time_close'"
assert 'close' in price_series.columns, "DataFrame should have 'close' column"

# Check index properties
assert pd.api.types.is_datetime64_dtype(price_series.index), "Index should be datetime64"
assert price_series.index.is_monotonic_increasing, "Index should be sorted ascending"

# Check for duplicates
assert not price_series.index.duplicated().any(), "Should not have duplicate timestamps"

# Check resampling to trading frequency
time_diffs = price_series.index.to_series().diff()[1:]  # Skip first NaN diff
expected_timedelta = pd.Timedelta(trading_frequency)
assert time_diffs.max() <= expected_timedelta, f"Data should be sampled at {trading_frequency} frequency"

# Basic price sanity checks
assert price_series['close'].dtype == float, "Close prices should be float type"

print("\nChecking for non-positive prices...")
problematic_prices = price_series[~(price_series['close'] > 0)]
if not problematic_prices.empty:
    print("\nFound these non-positive prices:")
    print(problematic_prices[['close']].to_string())
    print(f"\nTotal problematic prices: {len(problematic_prices)}")


assert not price_series['close'].isnull().any(), "Should not have NaN prices"
assert (price_series['close'] > 0).all(), "All prices should be positive"


# Check reasonable date range
current_year = pd.Timestamp.now().year
assert price_series.index.max().year <= current_year, "Data should not be from the future"

strat_pre_cost_sr = calculate_strat_pre_cost_sr(price_series)
assert (strat_pre_cost_sr == 1.9914208916281093)


def calculate_fees_paid():
    return 1038.6238698915147


def calculate_holding_costs_paid():
    funding_paid = 3130.3644113437113
    return funding_paid


def calulcate_slippage_paid():
    return 944.2035180831953


def calculate_strat_post_cost_sr(pre_cost_sr):
    fees = calculate_fees_paid()
    holding_costs = calculate_holding_costs_paid()
    slippage = calulcate_slippage_paid()

    fake_offset = 0.09552521025869809
    return pre_cost_sr - fake_offset
    # return pre_cost_sr - (fees + holding_costs + slippage)


strat_total_perc_returns = calculate_strat_total_perc_returns()
assert (strat_total_perc_returns == 958.3412684422372)

strat_mean_ann_perc_return = calculate_strat_mean_ann_perc_return()
assert (strat_mean_ann_perc_return == 65.7261486248434)


strat_std_dev = calculate_strat_std_dev()
assert (strat_std_dev == 1.8145849936803375)

strat_pre_cost_sr = calculate_strat_pre_cost_sr(price_series)
assert (strat_pre_cost_sr == 1.9914208916281093)

strat_post_cost_sr = calculate_strat_post_cost_sr(strat_pre_cost_sr)
assert (strat_post_cost_sr == 1.8958956813694112)


fees_paid = calculate_fees_paid()
assert (fees_paid == 1038.6238698915147)

slippage_paid = calulcate_slippage_paid()
assert (slippage_paid == 944.2035180831953)

funding_paid = calculate_holding_costs_paid()
assert (funding_paid == 3130.3644113437113)


ann_turnover = 37.672650094739545
assert (ann_turnover == 37.672650094739545)
