from polygon import RESTClient
import os
from dotenv import load_dotenv
import time
import csv
from datetime import datetime, timedelta

load_dotenv()

api_key = os.getenv('POLYGON_API_KEY')
if not api_key:
    raise ValueError(
        "No API key found. Please set the POLYGON_API_KEY in the .env file.")

client = RESTClient(api_key)

# Define the ticker and date range
ticker = 'ES'  # Replace with the appropriate contract symbol
start_date = '2022-09-30'
end_date = '2024-09-23'

# Define rate limit parameters
limit = 4  # Number of requests allowed per minute
interval = 60 / limit  # Interval in seconds between requests

# Function to fetch data in chunks

# ESH25, ESM25, ESU25, ESZ25,


def fetch_data_in_chunks(ticker, start_date, end_date):
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = timedelta(days=1)
    all_bars = []

    while current_date <= end_date:
        next_date = current_date + delta
        print(f"Fetching data from {current_date.strftime(
            '%Y-%m-%d')} to {next_date.strftime('%Y-%m-%d')}")
        try:
            bars = client.get_aggs(ticker=ticker, multiplier=1, timespan='day', from_=current_date.strftime(
                '%Y-%m-%d'), to=next_date.strftime('%Y-%m-%d'))
            print(f"extending bars: {bars}")
            all_bars.extend(bars)
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
        current_date = next_date
        time.sleep(interval)  # Pause to respect rate limit

    return all_bars

# Function to read existing CSV data and determine the date range


def read_existing_csv(csv_file_path):
    if not os.path.exists(csv_file_path):
        return None, None

    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        rows = list(reader)
        if not rows:
            return None, None

        first_date = datetime.strptime(rows[0][0], '%Y-%m-%d')
        last_date = datetime.strptime(rows[-1][0], '%Y-%m-%d')
        return first_date, last_date


# Fetch historical data for ES
print(f"Starting data fetch for {ticker} from {start_date} to {end_date}")
csv_file_path = f"{ticker}_data_2023_2024.csv"
first_date, last_date = read_existing_csv(csv_file_path)

# Determine the new date range to fetch
if first_date:
    if datetime.strptime(start_date, '%Y-%m-%d') < first_date:
        new_start_date = start_date
        new_end_date = (first_date - timedelta(days=1)).strftime('%Y-%m-%d')
        bars_before = fetch_data_in_chunks(
            ticker, new_start_date, new_end_date)
    else:
        bars_before = []
else:
    bars_before = fetch_data_in_chunks(ticker, start_date, end_date)

if last_date:
    if datetime.strptime(end_date, '%Y-%m-%d') > last_date:
        new_start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        new_end_date = end_date
        bars_after = fetch_data_in_chunks(ticker, new_start_date, new_end_date)
    else:
        bars_after = []
else:
    bars_after = []

bars = bars_before + bars_after
print(f"Data fetch complete. Total records fetched: {len(bars)}")

# Write data to CSV if new data is fetched
if bars:
    print(f"Writing data to {csv_file_path}")
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file is empty
        if os.stat(csv_file_path).st_size == 0:
            writer.writerow(['timestamp', 'open', 'high',
                            'low', 'close', 'volume'])
        # Write bar data
        for i, bar in enumerate(bars):
            writer.writerow([
                datetime.fromtimestamp(
                    bar.timestamp / 1000).strftime('%Y-%m-%d'),
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume
            ])
            # Preview the first 5 rows being written
            if i < 5:
                print(f"Row {i+1}: {datetime.fromtimestamp(bar.timestamp / 1000).strftime(
                    '%Y-%m-%d')}, {bar.open}, {bar.high}, {bar.low}, {bar.close}, {bar.volume}")
    print(
        f"Data writing complete. ES data for 2023-2024 has been written to {csv_file_path}")
else:
    print("No new data fetched. CSV file not updated.")
