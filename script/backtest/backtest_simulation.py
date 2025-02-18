import vectorbt as vbt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import os
from multiprocessing import cpu_count, Pool

FREQUENCY='1h'

def fetch_historical_data(symbol='BTC-USD'):
    """
    Fetch historical OHLCV data using vectorbt's Yahoo Finance integration.
    """
    if FREQUENCY=='1d':
        data = vbt.YFData.download(symbol, start='2022-02-01', end='2025-02-02', interval=FREQUENCY).get('Close')
    elif FREQUENCY=='1h':
        data = vbt.YFData.download(symbol, start='2023-06-02', end='2025-02-02', interval=FREQUENCY).get('Close')
    else:
        return None
    print("date range: ", data.index.min()," to " , data.index.max())
    return data

def generate_signals(
    data,
    short_window=5,
    long_window=15,
    rsi_window=14,
    rsi_buy_threshold=30,
    rsi_sell_threshold=70,
    short_type='SMA',
    long_type='SMA'):
    """
    Generate trading signals based on moving average crossover and an RSI filter.
    
    For a BUY signal:
      - The short-term MA is above the long-term MA (indicating upward momentum)
      - AND RSI is below the buy threshold (e.g., 30), suggesting the asset may be oversold.
    
    For a SELL signal:
      - The short-term MA is below the long-term MA (indicating downward momentum)
      - AND RSI is above the sell threshold (e.g., 70), suggesting the asset may be overbought.
    """
    if short_type == 'EMA':
        ma_short = data.ewm(span=short_window, adjust=False).mean()
    else:
        ma_short = data.rolling(short_window).mean()
    if long_type == 'EMA':
        ma_long = data.ewm(span=long_window, adjust=False).mean()
    else:
        ma_long = data.rolling(long_window).mean()
    # Calculate RSI
    rsi = vbt.RSI.run(data, window=rsi_window).rsi
    # Generate entries and exits using MA crossover, MACD, and RSI filters
    entries = (ma_short > ma_long) & (rsi < rsi_buy_threshold)
    exits   = (ma_short < ma_long) & (rsi > rsi_sell_threshold)
    return entries, exits

def run_backtest(args):
    """
    Run a backtest using vectorbt.
    """
    data, params = args
    short_window, long_window, rsi_window, rsi_buy_threshold, rsi_sell_threshold, short_type, long_type = params # macd_window, macd_short, macd_long,
    # Generate signals
    entries, exits = generate_signals(
        data,
        short_window=short_window,
        long_window=long_window,
        # signal_window=macd_window,
        # macd_short_window=macd_short,
        # macd_long_window=macd_long,
        rsi_window=rsi_window,
        rsi_buy_threshold=rsi_buy_threshold,
        rsi_sell_threshold=rsi_sell_threshold,
        short_type=short_type,
        long_type=long_type
    )

    # Simulate the strategy
    portfolio = vbt.Portfolio.from_signals(
        data,
        entries=entries,
        exits=exits,
        size=1.0,  # Trade 1 unit of the asset per signal
        fees=0.001,  # 0.1% trading fee
        freq='1h'  # Daily frequency
    )
    print(f"current cross:{short_window} {long_window} {rsi_window} {rsi_buy_threshold} {rsi_sell_threshold} {short_type} {long_type}")


    # Analyze performance
    stats = portfolio.stats()
    # print(stats)

    return {
            'short_window': short_window,
            'long_window': long_window,
            'rsi_window': rsi_window,
            'rsi_buy_threshold': rsi_buy_threshold,
            'rsi_sell_threshold': rsi_sell_threshold,
            'short_type': short_type,
            'long_type' : long_type,
            'total_return': stats.get('Total Return [%]', None),
            'win_rate_ratio' : stats.get('Win Rate [%]', None),
            'profit_factor' : stats.get('Profit Factor', None),
            'sharpe_ratio': stats.get('Sharpe Ratio', None),
            'calmar_ratio': stats.get('Calmar Ratio', None),
            'total_trades': stats.get('Total Trades', None),
            'avg_win_trade_duration' : stats.get('Avg Winning Trade Duration', None),
            'avg_win_trade': stats.get('Avg Winning Trade [%]', None),
            'avg_lose_trade': stats.get('Avg Losing Trade [%]', None),
            'sortino_ratio': stats.get('Sortino Ratio', None),
            'omega_ratio': stats.get('Omega Ratio', None)
        }

    # Plot the equity curve
    # portfolio.value().vbt.plot(title='Equity Curve')
    # portfolio.plots().show()

def grid_search(symbol='BTC-USD',
                short_window_range=None,
                long_window_range=None,
                macd_window_range=None,
                macd_short_window=None,
                macd_long_window=None,
                rsi_window_range=None,
                rsi_buy_threshold_range=None,
                rsi_sell_threshold_range=None,
                ma_combinations=[('SMA', 'SMA'), ('EMA', 'EMA'), ('EMA', 'SMA'), ('SMA', 'EMA')]
            ):
    """
    Perform a grid search over the specified parameter ranges.
    Returns a DataFrame of performance statistics for each parameter combination.
    """
    # Fetch historical data once
    data = fetch_historical_data(symbol)
    param_combinations = [
        (short_window, long_window, rsi_window, rsi_buy_threshold, rsi_sell_threshold, short_type, long_type) # macd_signal, macd_short, macd_long,
        for short_window in (short_window_range  if short_window_range is not None else [])
        for long_window in (long_window_range if long_window_range is not None else [])
        if long_window > short_window
        # for macd_signal in (macd_window_range if macd_window_range is not None else [])
        # for macd_short in (macd_short_window if macd_short_window is not None else [])
        # for macd_long in (macd_long_window if macd_long_window is not None else [])
        for rsi_window in (rsi_window_range if rsi_window_range is not None else [])
        for rsi_buy_threshold in (rsi_buy_threshold_range if rsi_buy_threshold_range is not None else [])
        for rsi_sell_threshold in (rsi_sell_threshold_range if rsi_sell_threshold_range is not None else [])
        for short_type, long_type in (ma_combinations if ma_combinations is not None else [])
    ]

    with Pool(cpu_count()) as pool:
        results = pool.map(run_backtest, [(data, params) for params in param_combinations])
    return pd.DataFrame(results)

def create_heatmaps(df, metrics, param1, param2, ma_methode):
    heatmaps = {}
    for metric in metrics:
        heatmap_data = df.pivot_table(index=param1, columns=param2, values=metric)
        plt.figure(figsize=(10,6))
        try:
            sns.heatmap(heatmap_data, annot=True, cmap='viridis', cbar_kws={'label': metric})
        except ValueError:
            break
        plt.title(f'Heatmap of {metric} for {param1} vs {param2} ({ma_methode[0]}-{ma_methode[1]})')
        plt.xlabel(f'xlabel: {param1}')
        plt.ylabel(f'ylabel: {param2}')
        heatmaps[metric] = plt
    return heatmaps

if __name__ == "__main__":
    # full_path="script/backtest/"
    full_path=""
    short_window = range(4, 12)
    long_window = range(14, 26)
    macd_window = None # range(8, 15)
    macd_short_window = None #range(8, 12)      
    macd_long_window = None # range(16, 23)     
    rsi_window = range(7,15) #[14]
    rsi_buy_threshold = [35, 30, 40]
    rsi_sell_threshold = [65, 60, 70]
    ma_tuples=[('SMA', 'SMA'), ('EMA', 'EMA'), ('EMA', 'SMA'), ('SMA', 'EMA')]
    tested_metrics = ['sharpe_ratio', 'calmar_ratio', 'total_trades', 'avg_win_trade', 'avg_lose_trade', 'sortino_ratio', 'omega_ratio', 'win_rate_ratio']

    print(os.getcwd())
    results_df = grid_search(
        symbol='BTC-USD',
        short_window_range=short_window,
        long_window_range=long_window,
        macd_window_range=macd_window,
        macd_short_window=macd_short_window,
        macd_long_window=macd_long_window,
        rsi_window_range=rsi_window,
        rsi_buy_threshold_range=rsi_buy_threshold,
        rsi_sell_threshold_range=rsi_sell_threshold,
        ma_combinations=ma_tuples
    )

    results_df = results_df[(results_df['total_trades'] >= 10) & (results_df['total_return'] > 0) ]
    best_params_sharp = results_df.sort_values(by=['sharpe_ratio'], ascending=[False])
    best_params_win_ration = results_df.sort_values(by=['win_rate_ratio'], ascending=[False])

    file_name = f'grid_search_result_freq_{FREQUENCY}_{datetime.datetime.now()}'
    res = best_params_sharp.to_csv(full_path+'backtest_res/' + file_name + '.csv')
    best_params_win_ration.to_csv(full_path+'backtest_res/' + file_name+'_win_ratio.csv')
    print(best_params_sharp.head(10))
    for ma_types in ma_tuples:
        filtered_results = results_df[(results_df['short_type'] == ma_types[0]) & (results_df['long_type'] == ma_types[1])]
        if filtered_results.empty:
            continue
        heatmap_window = create_heatmaps(results_df, tested_metrics, 'short_window', 'long_window', ma_types)
        # heatmap_macd_short = create_heatmaps(results_df, tested_metrics, 'macd_window', 'macd_short', ma_types)
        # heatmap_macd_long = create_heatmaps(results_df, tested_metrics, 'macd_window', 'macd_long', ma_types)
        # heatmap_macd_window = create_heatmaps(results_df, tested_metrics, 'macd_short', 'macd_long', ma_types)
        heatmap_rsi_buy = create_heatmaps(results_df, tested_metrics, 'rsi_window', 'rsi_buy_threshold', ma_types)
        heatmap_rsi_sell = create_heatmaps(results_df, tested_metrics, 'rsi_window', 'rsi_sell_threshold', ma_types)
        heatmap_rsi_buy_sell = create_heatmaps(results_df, tested_metrics, 'rsi_buy_threshold', 'rsi_sell_threshold', ma_types)
        for metric, plt in heatmap_window.items():
            plt.show()
        """
        for metric, plt in heatmap_macd_short.items():
            plt.show()
        for metric, plt in heatmap_macd_long.items():
            plt.show()
        for metric, plt in heatmap_macd_window.items():
            plt.show()
        """
 