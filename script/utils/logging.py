"""
logging script 
"""
import logging

import csv
import os
from datetime import datetime


CUR_ENV = os.getenv('BOT_ENV', 'dev')

def setup_logger():
    """
    Set up a logger to write logs to a file.
    """
    if CUR_ENV.lower() == 'production':
        path = 'btc-bot/script/logs/trading_bot.log'
    else:
        path = 'script/logs/trading_bot.log'
    logging.basicConfig(
            filename=path,
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

def log_order(order, log_filename="orders_log.csv"):
    """
    Logs order information to a CSV file.
    :param order: A dictionary returned by ccxt.create_order().
    :param log_filename: The CSV file to store the logs.
    """
    # Define the columns you want to record
    fieldnames = ["timestamp", "order_id", "symbol", "side",
                    "price", "amount", "status"]
    # Convert timestamp to a human-readable string
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # current time

    # Gather the relevant info from the 'order' dict
    row = {
        "timestamp": current_time,
        "order_id": order.get("id", ""),        # ccxt typically has 'id' or 'orderId'
        "symbol": order.get("symbol", ""),
        "side": order.get("side", ""),
        "price": order.get("price", ""),        # might be None for MARKET orders
        "amount": order.get("amount", ""),      # how many contracts or coins
        "status": order.get("status", "")
    }
    if CUR_ENV.lower() == 'production':
        log_filename = 'btc-bot/script/logs/orders_log.csv'
    else:
        log_filename = 'script/logs/orders_log.csv'
    file_exists = os.path.isfile(log_filename)

    # Append to CSV
    with open(log_filename, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # If this is a brand-new file, write the header first
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
        print(row)

if __name__ == "__main__":
    test_current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(test_current_time)
