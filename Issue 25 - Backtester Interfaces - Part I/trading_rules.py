from abc import ABC, abstractmethod


class TradingRule(ABC):
    @abstractmethod
    def get_raw_forecast(self, data_series):
        """Generate raw (unscaled) forecast from price series"""
        pass


class EMAC(TradingRule):
    def __init__(self, fast_lookback=2, slow_lookback=None):
        self.fast_lookback = fast_lookback
        self.slow_lookback = slow_lookback or fast_lookback * 4

    def get_raw_forecast(self, data_series):
        emac_fast = data_series.ewm(
            span=self.fast_lookback,
            min_periods=self.fast_lookback
        ).mean()

        emac_slow = data_series.ewm(
            span=self.slow_lookback,
            min_periods=self.slow_lookback
        ).mean()

        return emac_fast - emac_slow
