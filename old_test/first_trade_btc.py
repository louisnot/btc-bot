import ccxt
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="env/.env")

API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")

# Set testnet=True for Binance Futures
binance_futures_testnet = ccxt.binanceusdm({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {
        'defaultType': 'future'  # Use futures endpoints
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binancefuture.com/fapi/v1',
            'private': 'https://testnet.binancefuture.com/fapi/v1'
        }
    }
})
binance_futures_testnet.set_sandbox_mode(True)
test = binance_futures_testnet.fetch_balance()
print(test)

# Example: Place a market order for BTC/USDT on Testnet
symbol = 'BTC/USDT'
order = binance_futures_testnet.create_order(
    symbol=symbol,
    type='MARKET',
    side='BUY',
    amount=0.01  # Example amount
)

print(order)


# order = binance_futures_testnet.create_order(symbol=symbol, type='market', side='sell', amount='0.01')
print(order)
