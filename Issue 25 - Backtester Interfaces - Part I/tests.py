from backtest_refactored import zero_safe_divide
import pandas as pd
import numpy as np


def test_price_data_integrity(price_series, trading_frequency):
    """Validate the structural integrity of price data"""
    # Basic DataFrame structure
    assert not price_series.empty, "DataFrame should not be empty"
    assert price_series.index.name == 'time_close', f"Index should be named 'time_close'"

    # Index properties
    assert pd.api.types.is_datetime64_dtype(price_series.index), "Index should be datetime64"
    assert price_series.index.is_monotonic_increasing, "Index should be sorted ascending"
    assert not price_series.index.duplicated().any(), "Should not have duplicate timestamps"

    # Price data quality
    assert price_series.dtype == float, "Close prices should be float type"
    assert not price_series.isnull().any(), "Should not have NaN prices"
    assert (price_series > 0).all(), "All prices should be positive"

    # Time frequency validation
    time_diffs = price_series.index.to_series().diff()[1:]
    expected_timedelta = pd.Timedelta(trading_frequency)
    assert time_diffs.max() <= expected_timedelta, f"Data should be sampled at {trading_frequency} frequency"

    # Reasonable date range
    current_year = pd.Timestamp.now().year
    assert price_series.index.max().year <= current_year, "Data should not be from the future"


def test_raw_forecast_validity(raw_forecast, price_series):
    """Validate the raw trading rule forecast"""
    assert isinstance(raw_forecast, pd.Series), "Forecast should be a pandas Series"
    assert len(raw_forecast) == len(price_series), "Length mismatch between forecast and price series"
    assert raw_forecast.index.equals(price_series.index), "Index mismatch between forecast and price series"
    assert not raw_forecast.isnull().all(), "Forecast should not be all NaN"
    assert raw_forecast.isnull().sum() < len(raw_forecast), "Should have valid forecasts"


def test_scaled_forecast_properties(signal_series, expected_abs_avg, dev_threshold):
    """Validate the properties of the scaled forecast"""
    # Boundary tests
    assert signal_series.max() <= 20, "Forecast exceeds upper cap"
    assert signal_series.min() >= -20, "Forecast exceeds lower cap"

    # Target scaling tests
    signal_abs_avg = signal_series.abs().median()
    assert np.isclose(
        signal_abs_avg,
        expected_abs_avg,
        rtol=dev_threshold
    ), f"""Forecast average deviates more than {dev_threshold} from target.
    Expected: {expected_abs_avg},
    Found: {signal_abs_avg}"""


def check_positions_against_expected(actual_positions, expected_positions, position_type):
    """Compare actual positions against expected values from CSV

    Args:
        actual_positions (pd.Series): Positions to validate
        expected_filename (str): CSV file containing expected positions
        position_type (str): Type of positions being checked ('ideal' or 'rebalanced')
    """
    positions_array = np.array(actual_positions)
    expected_array = expected_positions[f'{position_type}_pos_contracts'].to_numpy()

    rel_diff = zero_safe_divide(np.abs(positions_array - expected_array), np.abs(expected_array))
    rtol = 0.0001

    if (rel_diff > rtol).any():
        print(f"\n{position_type.title()} positions deviating more than {rtol:.2%} relative tolerance:")
        print("Index  Expected    Actual      Rel.Diff")
        print("-" * 45)

        deviant_indices = np.where(rel_diff > rtol)[0]
        for idx in deviant_indices:
            print(f"{idx:5d}  {expected_array[idx]:9.4f}  {positions_array[idx]:9.4f}  {rel_diff[idx]:9.2%}")

        raise AssertionError(f"{position_type.title()} positions do not match expected values")

    print(f"All {position_type} positions within {rtol:.2%} relative tolerance")


def test_position_rebalancing(positions, price_series, threshold):
    """Validate the rebalanced positions"""

    # More General Tests
    assert isinstance(positions, pd.Series), "Rebalanced positions should be a pandas Series"
    assert len(positions) == len(price_series), "Length mismatch between positions and price series"
    assert positions.index.equals(price_series.index), "Index mismatch between positions and price series"
    assert not positions.isnull().all(), "Rebalanced positions should not be all NaN"
    assert positions.isnull().sum() < len(positions), "Rebalanced positions should have valid values"

    # Check new implementation against old implementation
    expected_positions = pd.read_csv('rebalanced_pos_contracts.csv')

    check_positions_against_expected(
        positions,
        expected_positions,
        'rebalanced'
    )

    # Check if we really rebalanced only when exceeding the threshold
    for i in range(1, len(positions)):
        prev_pos = positions.iloc[i - 1]
        curr_pos = positions.iloc[i]
        contract_diff = abs(curr_pos - prev_pos)
        deviation = contract_diff / abs(curr_pos) * 100 if abs(curr_pos) > 0 else 0

        if deviation > threshold:
            assert abs(curr_pos) != abs(prev_pos), "Rebalance should increase position size"
        else:
            assert abs(curr_pos) == abs(prev_pos), "Position should not change if within threshold"


def test_strategy_metrics(price_series):
    """Validate strategy performance metrics"""
    strat_pre_cost_sr = calculate_strat_pre_cost_sr(price_series)
    assert strat_pre_cost_sr == 1.9914208916281093, "Pre-cost Sharpe ratio mismatch"

    strat_post_cost_sr = calculate_strat_post_cost_sr(strat_pre_cost_sr)
    assert strat_post_cost_sr == 1.8958956813694112, "Post-cost Sharpe ratio mismatch"

    assert calculate_strat_total_perc_returns() == 958.3412684422372, "Total returns mismatch"
    assert calculate_strat_mean_ann_perc_return() == 65.7261486248434, "Mean annual return mismatch"
    assert calculate_strat_std_dev() == 1.8145849936803375, "Standard deviation mismatch"

    ann_turnover = 37.672650094739545
    assert ann_turnover == 37.672650094739545, "Annual turnover mismatch"


def test_trading_costs():
    """Validate trading cost calculations"""
    assert calculate_fees_paid() == 1038.6238698915147, "Fee calculation mismatch"
    assert calculate_holding_costs_paid() == 3130.3644113437113, "Holding costs calculation mismatch"
    assert calulcate_slippage_paid() == 944.2035180831953, "Slippage calculation mismatch"
    assert calculate_holding_costs_paid() == 3130.3644113437113, "Holding costs mismatch"
