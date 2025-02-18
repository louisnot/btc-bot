import os
from dotenv import load_dotenv
import ccxt
import pandas as pd
from datetime import datetime

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Initialize Binance API client
binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

# Define a function to fetch historical data
def fetch_historical_data(symbol, timeframe, start_date):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe, start_date) # ohlcv = Open High Low Close Volume
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # Convert timestamp to readable date
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None


symbol = 'BTC/USDT'          # Trading pair
timeframe = '1h'             # Timeframe (1m, 5m, 1h, 1d, etc.)
start_date = binance.parse8601('2023-01-01T00:00:00Z')  # Fetch data from January 1, 2023

# Fetch data and display
historical_data = fetch_historical_data(symbol, timeframe, start_date)

if historical_data is not None:
    print(historical_data.head())  # Display the first few rows
    # Save to CSV for later analysis
    historical_data.to_csv('btc_usdt_historical_data.csv', index=False)
    print("Historical data saved to btc_usdt_historical_data.csv")
