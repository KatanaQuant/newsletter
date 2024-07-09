import requests
import pandas as pd


def fetch_btcusdt_daily_data():
    # Binance API endpoint for historical candlestick data
    url = "https://api.binance.com/api/v3/klines"

    # Parameters: symbol, interval (1 day), and limit (max 1000 data points per request)
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1d',
        'limit': 1000
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Extract only the required columns from the data
    extracted_data = [[item[0], item[1], item[2],
                       item[3], item[4], item[5]] for item in data]

    # Convert the extracted data to a pandas DataFrame
    df = pd.DataFrame(
        extracted_data, columns=['Open time', 'open', 'high', 'low', 'close', 'volume'])

    # Convert timestamps to readable dates
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')

    # Rename 'Open time' to 'Timestamp' for clarity
    df.rename(columns={'Open time': 'timestamp'}, inplace=True)

    # Save to CSV
    df.to_csv('BTCUSDT_daily_data.csv', index=False)

    print("Data fetched and saved to BTCUSDT_daily_data.csv")


fetch_btcusdt_daily_data()
