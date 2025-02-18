"""
methods for risk management

position size and sl tp
"""
def calculate_stop_loss_take_profit(entry_price, stop_loss_pct=7, take_profit_pct=5, position_side='LONG'):
    """
    Calculate stop-loss and take-profit prices based on a percentage of the entry price
    """
    position_side = position_side.upper()
    if position_side == 'LONG':
        stop_loss_price = entry_price * (1 - stop_loss_pct / 100) if stop_loss_pct else None
        take_profit_price = entry_price * (1 + take_profit_pct / 100) if take_profit_pct else None
    elif position_side == 'SHORT':
        stop_loss_price = entry_price * (1 + stop_loss_pct / 100) if stop_loss_pct else None
        take_profit_price = entry_price * (1 - take_profit_pct / 100) if take_profit_pct else None
    else:
        raise ValueError("Invalid position_side: must be 'LONG' or 'SHORT' ")
    return stop_loss_price, take_profit_price

def calculate_position_size(account_balance, risk_percentage, entry_price, stop_loss_price):
    """
    Calculate the position size based on account balance and risk tolerance set
    """
    risk_amount = account_balance * (risk_percentage / 100)
    position_size = risk_amount / abs(entry_price - stop_loss_price)
    return position_size
