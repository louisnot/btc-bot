import pandas as pd
import matplotlib.pyplot as plt
import vectorbt as vbt

def plot_bitcoin_data():
    data = vbt.YFData.download(
        'BTC-USD', 
        start='2024-01-01',
        end='2025-01-01',
        interval='1d'
    )
    
    # Get the 'Close' price series and convert it into a DataFrame
    close_series = data.get('Close')
    df = pd.DataFrame({'close': close_series})
    
    # Calculate Moving Averages
    df['MA_short'] = df['close'].rolling(window=4).mean()
    df['MA_long']  = df['close'].rolling(window=15).mean()
    
    # Calculate RSI using vectorbt's built-in RSI indicator
    rsi_series = vbt.RSI.run(df['close'], window=14).rsi
    df['RSI'] = rsi_series

    # Check that our DataFrame has data
    if df.empty:
        print("No data available. Please check your date range and interval.")
        return

    # Create the figure and two subplots: one for price and MAs, one for RSI
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(14, 10), sharex=True)

    # Top subplot: Price and Moving Averages
    ax1.plot(df.index, df['close'], label='BTC-USD Close', color='blue', linewidth=1)
    ax1.plot(df.index, df['MA_short'], label=f'MA Short (4h)', color='red', linewidth=1)
    ax1.plot(df.index, df['MA_long'], label=f'MA Long (15h)', color='green', linewidth=1)
    ax1.set_title('BTC-USD Hourly Price with Moving Averages')
    ax1.set_ylabel('Price (USD)')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Bottom subplot: RSI
    ax2.plot(df.index, df['RSI'], label=f'RSI (14h)', color='orange', linewidth=1)
    ax2.axhline(30, linestyle='--', color='gray', label='Oversold (30)')
    ax2.axhline(70, linestyle='--', color='gray', label='Overbought (70)')
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_ylabel('RSI Value')
    ax2.set_xlabel('Date')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left')
    ax2.grid(True)

    # Adjust layout and display the plot
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    plot_bitcoin_data()
