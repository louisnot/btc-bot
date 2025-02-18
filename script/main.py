"""
main method to init progrmm
"""
import sys
from utils.api import fetch_ohlcv, place_market_order, cancel_pending_orders, binance_futures_testnet
from utils.signals import generate_signals
from utils.risk_management import calculate_stop_loss_take_profit, calculate_position_size
from utils.logging import setup_logger

# init logger
setup_logger()

def handle_signal(signal, symbol, risk_percentage=3):
    """
    signal: 'BUY' or 'SELL' from crossover strategy
    symbol: 'BTC/USDT'
    amount: how many contracts/coins to open
    risk_percentage factor default 3 (balance * ( risk_percentage / 100 )
    """
    cancel_pending_orders(symbol)
    # Calculate stop-loss and take-profit prices
    ticker = binance_futures_testnet.fetch_ticker(symbol)
    latest_price = ticker['last']
    stop_loss_price, take_profit_price = calculate_stop_loss_take_profit(latest_price)
    # Check current balance in USDT and determine position_size
    balance = binance_futures_testnet.fetch_balance()
    available_balance = balance['USDT']['free']
    position_size = calculate_position_size(available_balance, risk_percentage, latest_price, stop_loss_price)

    # Check current positions (both LONG and SHORT) on this symbol
    positions = binance_futures_testnet.fetch_positions()
    current_long_qty = 0
    current_short_qty = 0
    for pos in positions:
        if symbol in pos['symbol']:
            # positionSide might be 'LONG' or 'SHORT'
            if pos['side'].upper() == 'LONG':
                current_long_qty = float(pos['contracts']) if pos['contracts'] else 0
            elif pos['side'].upper() == 'SHORT':
                current_short_qty = float(pos['contracts']) if pos['contracts'] else 0

    # If signal == 'BUY', we want to:
    #    - close any short, then open (or add to) a long
    if signal == 'BUY':
        if current_short_qty > 0:
            # Close the short
            print("Closing SHORT position")
            place_market_order(symbol, 'BUY', current_short_qty, 'SHORT')
        # Open or add to long
        print("Opening/adding LONG position")
        place_market_order(symbol, 'BUY', position_size, 'LONG', stop_loss_price, take_profit_price)

    # If signal == 'SELL', we want to:
    #    - close any long, then open (or add to) a short
    elif signal == 'SELL':
        if current_long_qty > 0:
            # Close the long
            print("Closing LONG position")
            place_market_order(symbol, 'SELL', current_long_qty, 'LONG')
        # Open or add to short
        print("Opening/adding SHORT position")
        stop_loss_price, take_profit_price = calculate_stop_loss_take_profit(latest_price, position_side='SHORT')
        place_market_order(symbol, 'SELL', position_size, 'SHORT', stop_loss_price, take_profit_price)

def main(mode):
    """
    docstring
    """
    symbol = 'BTC/USDT'
    timeframe = '1h'
    df = fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
    if df is not None and not df.empty:
        df, signal = generate_signals(df)
        if mode == 'prod':
            if signal in ["BUY", "SELL"]:
                handle_signal(signal, symbol)
            else:
                print("No crossover signal. Doing nothing.")
        else:
            positions = binance_futures_testnet.fetch_positions()
            for pos in positions:
                print(pos)
            handle_signal('SELL', symbol)
            # place_market_order(symbol, 'BUY', 0.02, 'LONG', 100000, 200000)
            """
            place_market_order(symbol, 'SELL', 0.02, 'SHORT', 100000, 200000)
            place_market_order(symbol, 'BUY', 0.02, 'SHORT', 100000, 200000)
            place_market_order(symbol, 'SELL', 0.02, 'LONG', 100000, 200000)
            """
    else:
        print("No OHLCV data fetched.")

if __name__ == "__main__":
    MODE = 'debug'
    if len(sys.argv) > 1:
        if sys.argv[1] == '--prod':
            MODE = 'prod'
    main(MODE)
