from abc import ABC, abstractmethod
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv


class DataStoreError(Exception):
    """Base exception for all data store errors"""
    pass


class NoDataFoundError(DataStoreError):
    """Raised when a query returns no data"""
    pass


# Abstract interface for data stores - defines minimal contract
class DataStore(ABC):
    @abstractmethod
    def fetch_raw_data(self, symbol, frequency):
        """Implementation specific data fetching"""
        pass

    def fetch_raw_data_with_validation(self, symbol, frequency):
        """Template method that handles common error cases"""
        data = self.fetch_raw_data(symbol, frequency)
        if data.empty:
            raise NoDataFoundError(f"No data found for symbol '{symbol}' with frequency '{frequency}'")
        return data


# Concrete implementation for DB access - only responsible for DB operations
class DBStore(DataStore):
    def fetch_raw_data(self, symbol, frequency):
        load_dotenv()

        conn = psycopg2.connect(
            dbname=os.environ.get("DB_DB"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PW"),
            host=os.environ.get("DB_HOST"),
            port=os.environ.get("DB_PORT")
        )

        cur = conn.cursor()
        cur.execute(f"""
            SELECT ohlcv.time_close, ohlcv.close
            FROM ohlcv
            JOIN coins ON ohlcv.coin_id = coins.id
            WHERE coins.symbol = '{symbol}'
            AND ohlcv.interval = '{frequency}'
            ORDER BY ohlcv.time_close ASC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return pd.DataFrame(rows)


# Concrete implementation for CSV access - only responsible for file operations
class CSVStore(DataStore):
    def __init__(self, base_path):
        self.base_path = base_path

    def fetch_raw_data(self, symbol, frequency):
        file_path = f"{self.base_path}/{symbol}_{frequency}.csv"
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError:
            return pd.DataFrame()  # Return empty DataFrame to trigger NoDataFoundError


# Main price processing class - uses composition via DataStore dependency
class PriceReader:
    TARGET_INDEX_COLUMN_NAME = 'time_close'
    TARGET_PRICE_COLUMN_NAME = 'close'

    def __init__(self, store, index_column, price_column):
        # Dependency injection of data store
        self.store = store

        self.index_column_name = index_column
        self.price_column_name = price_column

    def fetch_price_series(self, symbol, frequency):
        # Delegates data fetching to injected store
        raw_df = self.store.fetch_raw_data_with_validation(symbol, frequency)
        return self.prepare_price_series(raw_df, frequency)

    def transform_columns(self, df):
        column_mapping = {
            self.index_column_name: self.TARGET_INDEX_COLUMN_NAME,
            self.price_column_name: self.TARGET_PRICE_COLUMN_NAME
        }
        return df.rename(columns=column_mapping)

    def prepare_price_series(self, df, frequency):
        df = self.transform_columns(df)

        # Data processing logic isolated from data access
        df[self.TARGET_INDEX_COLUMN_NAME] = pd.to_datetime(df[self.TARGET_INDEX_COLUMN_NAME]).dt.tz_localize(None)
        df.set_index(self.TARGET_INDEX_COLUMN_NAME, inplace=True)
        df.sort_index(inplace=True)

        resampled = df.resample(frequency).last()
        resampled[self.TARGET_PRICE_COLUMN_NAME] = resampled[self.TARGET_PRICE_COLUMN_NAME].ffill()

        self.check_nan_values(resampled)
        return resampled

    def check_nan_values(self, df):
        nan_after_fill = df[self.TARGET_PRICE_COLUMN_NAME].isna().sum()
        if nan_after_fill > 0:
            print(f"\nWarning: Still found {nan_after_fill} NaN values after forward filling")
            print("First and last dates with NaN:")
            print(df[df[self.TARGET_PRICE_COLUMN_NAME].isna()].index[[0, -1]])
