from instrument import Instrument

from trading_rules import EMAC

from data_sources import DBStore
from data_sources import PriceReader

import pandas as pd
import numpy as np


# def calculate_fees_paid():
#     return 1038.6238698915147


# def calculate_holding_costs_paid():
#     funding_paid = 3130.3644113437113
#     return funding_paid


# def calulcate_slippage_paid():
#     return 944.2035180831953


# def calculate_strat_post_cost_sr(pre_cost_sr):
#     fees = calculate_fees_paid()
#     holding_costs = calculate_holding_costs_paid()
#     slippage = calulcate_slippage_paid()

#     fake_offset = 0.09552521025869809
#     return pre_cost_sr - fake_offset
# return pre_cost_sr - (fees + holding_costs + slippage)


# def calculate_strat_total_perc_returns():
#     return 958.3412684422372


# def calculate_strat_mean_ann_perc_return():
#     return 65.7261486248434


# def calculate_strat_std_dev():
#     return 1.8145849936803375

# def calculate_strat_pre_cost_sr(price_series):
#     signals = generate_signals(price_series)
#     rebalanced_positions = generate_rebalanced_positions(rebalance_threshold=10)

#     raw_usd_pnl = price_series.diff() * rebalanced_positions.shift(1)
#     pnl_stddev = calculate_vol(price_series.diff())

#     raw_returns_vol_adjusted = raw_usd_pnl.mean() / pnl_stddev
#     return raw_returns_vol_adjusted
#     # return 1.9914208916281093


# helper functions
def calculate_vol(feature_series, lookback, min_periods=10):
    return feature_series.ewm(span=lookback, min_periods=min_periods).std()


def calculate_annual_risk_target(account_balance, ann_perc_risk_target):
    return account_balance * ann_perc_risk_target


def calculate_daily_risk_target(annual_risk_target, trading_days_per_year):
    return annual_risk_target / np.sqrt(trading_days_per_year)


def zero_safe_divide(a, b, epsilon=1e-9):
    # epsilon offset for cases where 0 is valid
    # like in the case of ideal positions
    return a / (b + epsilon)


# strategy specifics
def generate_signals(trading_rule, instrument, feature_name):
    try:
        feature_series = instrument.get_feature(feature_name)
    except ValueError as e:
        available = instrument.available_features()
        raise ValueError(f"{str(e)}. Available features: {available}")

    raw_forecast = trading_rule.get_raw_forecast(feature_series)

    instr_vol = calculate_vol(
        feature_series.diff(),
        VOL_LOOKBACK
    )
    vol_normalized_forecast = raw_forecast / instr_vol

    abs_values = vol_normalized_forecast.abs().expanding(
        min_periods=instrument.trading_days_in_year * 2
    )
    avg_abs_value = abs_values.median()
    scaling_factor = TARGET_AVG_FORECAST / avg_abs_value
    scaling_factor = scaling_factor.bfill()

    scaled_forecast = vol_normalized_forecast * scaling_factor

    capped_forecast = scaled_forecast.clip(lower=-20, upper=20)
    return capped_forecast


def calculate_ideal_positions(instrument, daily_cash_risk_target, signals):
    notional_exp_1_contract = instrument.get_notional_value(contracts=1)
    daily_instr_perc_risk = calculate_vol(
        instrument.get_perc_returns(),
        VOL_LOOKBACK
    )
    daily_contract_risk = notional_exp_1_contract * daily_instr_perc_risk

    # scale down to account size
    contracts_needed = daily_cash_risk_target / daily_contract_risk

    # absolute_avg_forecast = signals.abs().median()
    absolute_avg_forecast = TARGET_AVG_FORECAST
    ideal_pos_series = contracts_needed * signals / absolute_avg_forecast
    return ideal_pos_series.fillna(0)


def generate_rebalanced_positions(ideal_positions, rebalance_threshold):
    rebalanced = pd.Series(index=ideal_positions.index, dtype=float)
    for idx in ideal_positions.index:
        if idx == ideal_positions.index[0]:
            rebalanced[idx] = ideal_positions[idx]
            continue

        prev_pos = ideal_positions.index.get_loc(idx) - 1
        current_position = rebalanced.iloc[prev_pos]
        if pd.isna(current_position):
            current_position = 0

        deviation = zero_safe_divide(
            abs(ideal_positions[idx] - current_position),
            abs(ideal_positions[idx])
        )
        rebalanced[idx] = ideal_positions[idx] if deviation > rebalance_threshold else current_position
    return rebalanced


TARGET_AVG_FORECAST = 10.0
VOL_LOOKBACK = 35  # EMA


if __name__ == "__main__":
    # Setup
    trading_frequency = '1D'
    symbolname = 'BTC'
    feature_name = 'close'

    db_store = DBStore()
    db_reader = PriceReader(db_store, index_column=0, price_column=1)
    price_series = db_reader.fetch_price_series(symbolname, trading_frequency)

    instrument = Instrument(
        symbolname,
        price_series,
        trading_days_in_year=365,
        contract_unit=1
    )

    from tests import (
        test_price_data_integrity,
        test_raw_forecast_validity,
        test_scaled_forecast_properties,
        test_position_rebalancing,
        check_positions_against_expected
    )

    print("Testing price data integrity...")
    test_price_data_integrity(instrument.get_feature(feature_name), trading_frequency)

    print("Testing raw forecast generation...")
    fast_lookback = 8
    slow_lookback = fast_lookback * 4
    emac = EMAC(fast_lookback, slow_lookback)
    raw_forecast = emac.get_raw_forecast(instrument.get_feature(feature_name))
    test_raw_forecast_validity(raw_forecast, price_series)

    print("Testing scaled forecast properties...")
    signals = generate_signals(emac, instrument, feature_name)
    test_scaled_forecast_properties(
        signals,
        expected_abs_avg=TARGET_AVG_FORECAST,
        dev_threshold=0.10
    )

   # Step 1: Annual risk target
    account_balance = 10_000
    ann_perc_risk_target = 0.20  # 20%
    ann_cash_risk_target = calculate_annual_risk_target(
        account_balance,
        ann_perc_risk_target
    )

    # Step 2: Convert to daily cash risk target
    daily_cash_risk_target = calculate_daily_risk_target(
        ann_cash_risk_target,
        instrument.trading_days_in_year
    )

    # Step 3: Calculate ideal position
    ideal_positions = calculate_ideal_positions(
        instrument,
        daily_cash_risk_target,
        signals
    )
    expected_ideal_positions = pd.read_csv('ideal_pos_contracts.csv')
    check_positions_against_expected(
        ideal_positions,
        expected_ideal_positions,
        'ideal'
    )

    # Step 4 & 5: Calculate deviation and rebalance
    rebalance_err_threshold = 0.10
    rebalanced_positions = generate_rebalanced_positions(
        ideal_positions=ideal_positions,
        rebalance_threshold=rebalance_err_threshold
    )

    print("Testing rebalanced positions...")
    test_position_rebalancing(
        rebalanced_positions,
        instrument.get_feature(feature_name),
        rebalance_err_threshold
    )

    exit()

    # print("Testing strategy metrics...")
    # test_strategy_metrics(price_series)

    # print("Testing trading costs...")
    # test_trading_costs()

    # print("All tests passed successfully!")
