class Instrument:
    CLOSE_COLUMN = 'close'

    def __init__(self, name, price_data, trading_days_in_year, contract_unit):
        self.__price_data = price_data
        self.name = name
        self.trading_days_in_year = trading_days_in_year
        self.contract_unit = contract_unit

    def get_notional_value(self, contracts):
        return contracts * self.get_feature(self.CLOSE_COLUMN) * self.contract_unit

    def get_raw_returns(self):
        return self.get_feature(self.CLOSE_COLUMN).diff()

    def get_perc_returns(self):
        return self.get_feature(self.CLOSE_COLUMN).pct_change().dropna()

    def get_feature(self, feature_name):
        """Get a specific feature from the instrument's data, e.g. close prices

        Args:
            feature_name (str): Name of the feature to retrieve

        Returns:
            pd.Series: The requested feature data

        Raises:
            ValueError: If feature doesn't exist
        """
        if feature_name not in self.__price_data.columns:
            raise ValueError(f"Feature '{feature_name}' not available for {self.symbol}")
        return self.__price_data[feature_name]

    def available_features(self):
        """List all available features for this instrument"""
        return list(self._price_data.columns)
