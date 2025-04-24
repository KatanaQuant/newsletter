import pandas as pd
import requests
import json
import time


def fetch_historical_funding_rates(symbol, start_time, end_time):
    print('fetching historical funding rates for', symbol, start_time, end_time)

    url = 'https://api.bybit.com/v5/market/funding/history'
    params = {
        'symbol': symbol,
        'category': 'inverse',
        'startTime': start_time,
        'endTime': end_time,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_message = response.json().get('ret_msg', 'Unknown error')
        except (json.JSONDecodeError, AttributeError):
            error_message = str(e)
        raise Exception(f"API request failed: {error_message}")


def fetch_all_funding_rates(symbol, start_time):
    all_funding_rates = []
    current_time = int(time.time()) * 1000  # Current time in milliseconds
    end_time = start_time + (66 * 24 * 60 * 60 * 1000)  # 66 days in milliseconds

    while start_time < current_time:
        if end_time > current_time:
            end_time = current_time

        funding_rates = fetch_historical_funding_rates(symbol, start_time, end_time)
        if 'result' in funding_rates and 'list' in funding_rates['result']:
            rates = funding_rates['result']['list']

            all_funding_rates.extend(rates)
            start_time = end_time
            end_time = start_time + (66 * 24 * 60 * 60 * 1000)
        else:
            print("could not find funding rates in response")

    return all_funding_rates


symbol = "BTCUSDT"
start_time = int(time.mktime(time.strptime('2011-01-01', '%Y-%m-%d'))) * 1000  # Convert to milliseconds


all_funding_rates = fetch_all_funding_rates(symbol, start_time)
print(json.dumps(all_funding_rates, indent=4))
print(f"Fetched {len(all_funding_rates)} funding rates")


df = pd.DataFrame(all_funding_rates)
df['time_close'] = pd.to_datetime(pd.to_numeric(df['fundingRateTimestamp']), unit='ms')
if not pd.api.types.is_datetime64_any_dtype(df['time_close']):
    df['time_close'] = pd.to_datetime(df['time_close'])
df.set_index('time_close', inplace=True)
df.sort_values(by='time_close', inplace=True)
df.to_csv('BTC_funding_rates.csv')
