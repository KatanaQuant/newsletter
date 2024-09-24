import pandas as pd
import os
import requests
from datetime import datetime, timedelta


def read_ohlcv_from_xlsx(filepath):
    df = pd.read_excel(filepath)

    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    df.set_index('timestamp', inplace=True)
    df.sort_values(by='timestamp', inplace=True)

    return df


def read_ohlcv_from_csv(filepath):
    df = pd.read_csv(filepath)

    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    df.set_index('timestamp', inplace=True)
    df.sort_values(by='timestamp', inplace=True)

    return df


def fetch_btcusdt_daily_data():
    # CoinGecko API endpoint for historical market data
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"

    # Parameters: vs_currency (USD), days (365), and interval (daily)
    params = {
        'vs_currency': 'usd',
        'days': '365',
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the required columns from the data
    extracted_data = []
    for i in range(len(data['prices'])):
        extracted_data.append([
            data['prices'][i][0],  # timestamp
            data['prices'][i][1],  # price price
            data['market_caps'][i][1],  # market cap
            data['total_volumes'][i][1]  # total_volume
        ])

    # Convert the extracted data to a pandas DataFrame
    df = pd.DataFrame(
        extracted_data, columns=['timestamp', 'price', 'market_cap', 'total_volume'])

    # Drop the latest row because it may not be a complete day
    df = df[:-1]

    # Convert timestamps to readable dates
    df['timestamp'] = pd.to_datetime(
        df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S UTC')

    return df


def save_data_to_csv(df, CSV_FILE):
    df.to_csv(CSV_FILE, index=False)


def load_existing_data(CSV_FILE):
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, parse_dates=['timestamp'])
    return pd.DataFrame()


def update_data(CSV_FILE):
    existing_data = load_existing_data(CSV_FILE)

    if not existing_data.empty:
        last_entry_date = existing_data['timestamp'].max()
        last_entry_date = pd.to_datetime(
            last_entry_date, utc=True)
        if last_entry_date >= datetime.now(tz=last_entry_date.tzinfo) - timedelta(days=1):
            print("Data is up to date.")
            return

    new_data = fetch_btcusdt_daily_data()
    if not existing_data.empty:
        # Convert the timestamp column back to datetime for comparison
        new_data['timestamp'] = pd.to_datetime(
            new_data['timestamp'], utc=True)
        combined_data = pd.concat(
            [existing_data, new_data]).drop_duplicates(subset=['timestamp'])
        new_rows = combined_data[combined_data['timestamp'] > last_entry_date]
    else:
        combined_data = new_data
        new_rows = combined_data

    save_data_to_csv(combined_data, CSV_FILE)
    print("Data has been updated and saved to CSV.")
    print("Newly fetched rows:")
    print(new_rows)
