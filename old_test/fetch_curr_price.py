import os
from dotenv import load_dotenv
import ccxt

# Load API keys from .env file
load_dotenv(dotenv_path="env/.env")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Initialize Binance API client
binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
})

# Fetch current BTC/USDT price
try:
    ticker = binance.fetch_ticker('BTC/USDT')
    print(f"Current BTC/USDT price: {ticker['last']}")
except Exception as e:
    print(f"Error fetching ticker: {e}")
