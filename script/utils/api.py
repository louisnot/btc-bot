"""
api module for binance
"""
import os
import ccxt
import pandas as pd
from dotenv import load_dotenv
from utils.logging import log_order

class BinanceClient:
    """
    binance class client for api calls
    """
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BinanceClient, cls).__new__(cls)
            load_dotenv('/home/louis/btc-bot/env/.env')
            api_key = os.getenv("BINANCE_TESTNET_API_KEY")
            api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
            # Configure ccxt for Binance Futures Testnet
            cls._instance.client = ccxt.binanceusdm({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'
                },
                'urls': {
                    'api': {
                        'public': 'https://testnet.binancefuture.com/fapi/v1',
                        'private': 'https://testnet.binancefuture.com/fapi/v1'
                    }
                }
            })
            cls._instance.client.set_sandbox_mode(True)
        return cls._instance
binance_futures_testnet = BinanceClient().client
# balance = binance_futures_testnet.fetch_balance()
# print(balance)

def fetch_ohlcv(symbol='BTC/USDT', timeframe='1h', limit=50):
    """
    Fetch historical candlestick data for the given symbol.
    Returns a Pandas DataFrame with columns: [timestamp, open, high, low, close, volume].
    """
    try:
        ohlcv = binance_futures_testnet.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except ccxt.BaseError as e:
        print(f"Error fetching OHLCV data: {e}")
        return None

# Place an order on Binance Futures Testnet
def place_market_order(symbol, side, amount, position_side, stop_loss_price=None, take_profit_price=None):
    """
    Places a market order on the Binance Futures Testnet.
    side: 'BUY' or 'SELL'
    amount: how many BTC you want to buy/sell
    position: long or short
    side buy && position long --> open long position || side buy && poistion short --> open short position
    side sell && position long --> close long position || side sell && position short --> close short position
    can sl or tp if provided also None by default
    """
    try:
        order = binance_futures_testnet.create_order(
            symbol=symbol,
            type='MARKET',
            side=side,
            amount=amount,
            params={
                "positionSide" : position_side
            }
        )
        print(f"{side} {position_side} order placed for {symbol} (amount: {amount})")
        log_order(order)

        # stop_loss order if provided
        if stop_loss_price:
            stop_side = 'BUY' if position_side == 'SHORT' else 'SELL'
            print(f"Placing STOP-LOSS order for {position_side} position: {stop_side} {amount} {symbol} at {stop_loss_price}")            
            stop_order = binance_futures_testnet.create_order(
                symbol=symbol,
                type='STOP_MARKET',
                side=stop_side,
                amount=amount,
                params={
                    "positionSide": position_side,
                    "stopPrice": stop_loss_price,
                    "closePosition": True  # Close the entire position
                }
            )
            print(f"Stop-loss order placed at {stop_loss_price}")
            log_order(stop_order)

        # take-profit order if provided
        if take_profit_price:
            take_profit_side = 'BUY' if position_side == 'SHORT' else 'SELL'  # Opposite side for take-profit
            print(f"Placing TAKE-PROFIT order for {position_side} position: {take_profit_side} {amount} {symbol} at {take_profit_price}")
            take_profit_order = binance_futures_testnet.create_order(
                symbol=symbol,
                type='TAKE_PROFIT_MARKET',
                side=take_profit_side,
                amount=amount,
                params={
                    "positionSide": position_side,
                    "stopPrice": take_profit_price,
                    "closePosition": True  # Close the entire position
                }
            )
            print(f"Take-profit order placed at {take_profit_price}")
            log_order(take_profit_order)
    except ccxt.BaseError as e:
        print(f'Error placing {side} order: {e}')

def cancel_pending_orders(symbol):
    """
    Cancels all open orders for a given symbol.
    """
    try:
        orders = binance_futures_testnet.fetch_open_orders(symbol)
        for order in orders:
            binance_futures_testnet.cancel_order(order['id'], symbol)
            print(f"Canceled order: {order['id']}")
    except ccxt.BaseError as e:
        print(f"Error canceling orders for {symbol}: {e}")
