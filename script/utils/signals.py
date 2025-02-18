"""
signals module to detect when to buy or sell
"""
import pandas as pd
import vectorbt as vbt


def generate_signals(df, short_window=8, long_window=14, rsi_window=14, rsi_buy_threshold=35, rsi_sell_threshold=60):
    """
    Adds two columns to the DataFrame: short MA and long MA.
    Returns the DataFrame with the new columns and a signal ('BUY', 'SELL', or None).
    """
    if df is None or df.empty:
        return df, None
    df['MA_short'] = df['close'].rolling(window=short_window).mean() # short MA reacts faster to price change
    df['MA_long'] = df['close'].rolling(window=long_window).mean() #  long MA reacts slower and representer broader trend

    rsi_series = vbt.RSI.run(df['close'], window=rsi_window).rsi
    df['RSI'] = rsi_series

    # We only generate a signal on the last row
    latest_short = df['MA_short'].iloc[-1]
    latest_long = df['MA_long'].iloc[-1]
    latest_rsi = df['RSI'].iloc[-1]

    # Check for NaN
    if pd.isna(latest_short) or pd.isna(latest_long) or pd.isna(latest_rsi):
        return df, None

    # crossover logic
    # (We also check the previous candles to confirm a crossover event)
    prev_short = df['MA_short'].iloc[-2]
    prev_long = df['MA_long'].iloc[-2]

    # Moving Average Crossover
    buy_condition  = (prev_short < prev_long) and (latest_short > latest_long)
    sell_condition = (prev_short > prev_long) and (latest_short < latest_long)

    # RSI Filters
    # BUY if RSI < rsi_buy_threshold
    # SELL if RSI > rsi_sell_threshold
    rsi_buy_filter  = latest_rsi < rsi_buy_threshold
    rsi_sell_filter = latest_rsi > rsi_sell_threshold
    # Buy signal if short MA crosses above long MA
    if buy_condition and rsi_buy_filter:
        return df, 'BUY'
    # Sell signal if short MA crosses below long MA
    if sell_condition and rsi_sell_filter:
        return df, 'SELL'
    return df, None
