import pandas as pd
from abc import ABC, abstractmethod


class PriceDataSource(ABC):
    TARGET_INDEX_COLUMN_NAME = 'time_close'
    TARGET_PRICE_COLUMN_NAME = 'close'

    def __init__(self, index_column, price_column):
        self.index_column_name = index_column
        self.price_column_name = price_column

    @abstractmethod
    def fetch_raw_price_series(self, symbol, frequency):
        pass

    def transform_columns(self, df):
        column_mapping = {
            self.index_column_name: self.TARGET_INDEX_COLUMN_NAME,
            self.price_column_name: self.TARGET_PRICE_COLUMN_NAME
        }

        return df.rename(columns=column_mapping)

    def prepare_price_series(self, df, frequency):
        df = self.transform_columns(df)

        df[self.TARGET_INDEX_COLUMN_NAME] = pd.to_datetime(df[self.TARGET_INDEX_COLUMN_NAME]).dt.tz_localize(None)
        df.set_index(self.TARGET_INDEX_COLUMN_NAME, inplace=True)
        df.sort_index(inplace=True)

        # Resample and handle missing values
        resampled = df.resample(frequency).last()
        resampled[self.TARGET_PRICE_COLUMN_NAME] = resampled[self.TARGET_PRICE_COLUMN_NAME].ffill()

        # Print diagnostic NaN info
        nan_after_fill = resampled[self.TARGET_PRICE_COLUMN_NAME].isna().sum()
        if nan_after_fill > 0:
            print(f"\nWarning: Still found {nan_after_fill} NaN values after forward filling")
            print("First and last dates with NaN:")
            print(resampled[resampled[self.TARGET_PRICE_COLUMN_NAME].isna()].index[[0, -1]])

        return resampled

    def fetch_price_series(self, symbol, frequency):
        raw_df = self.fetch_raw_price_series(symbol, frequency)
        return self.prepare_price_series(raw_df, frequency)


class CSVReader(PriceDataSource):
    def __init__(self, base_path, index_column, price_column):
        super().__init__(index_column, price_column)
        self.base_path = base_path

    def fetch_raw_price_series(self, symbol, frequency):
        file_path = f"{self.base_path}/{symbol}_{frequency}.csv"
        return pd.read_csv(file_path)


class DBReader(PriceDataSource):
    def fetch_raw_price_series(self, symbolname, trading_frequency):
        from dotenv import load_dotenv
        load_dotenv()

        import psycopg2
        import os

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
            WHERE coins.symbol = '{symbolname}'
            ORDER BY ohlcv.time_close ASC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return pd.DataFrame(rows)
