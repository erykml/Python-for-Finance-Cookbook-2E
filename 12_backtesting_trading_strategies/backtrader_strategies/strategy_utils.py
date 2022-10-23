import backtrader as bt

class MyBuySell(bt.observers.BuySell):
    """
    Custom color definitions of the buy/sell indicators.
    """
    plotlines = dict(
        buy=dict(marker="^", markersize=8.0, color="green", fillstyle="full"),
        sell=dict(marker="v", markersize=8.0, color="red", fillstyle="full")
    )

def get_action_log_string(dir, action, price, size, asset=None, cost=None, 
                          commission=None, cash=None, open=None, close=None):
    """
    Helper function for logging. Creates a string indicating a 
    created/executed buy/sell order.

    Args:
        dir (str): The direction of the position, can be a value in ["b", "s"]
        action (str): The action, can be a value in ["e", "c"]
        price (float): The price
        size (float, optional): The size. Defaults to None.
        asset (str): name of the asset
        cost (float, optional): The cost. Defaults to None.
        commission (float, optional): The comission. Defaults to None.
        cash (float, optional): The cash amount. Defaults to None.
        open (float, optional): The open price. Defaults to None.
        close (float, optional): The close price. Defaults to None.

    Returns:
        str: The string used for logging
    """
    dir_dict = {
        "b": "BUY",
        "s": "SELL",
    }

    action_dict = {
        "e": "EXECUTED",
        "c": "CREATED"
    }

    str = (
        f"{dir_dict[dir]} {action_dict[action]} - "
        f"Price: {price:.2f}, Size: {size:.2f}"
    )
    
    if asset is not None:
        str = str + f", Asset: {asset}"


    if action == "e":
        if cost is not None:
            str = str + f", Cost: {cost:.2f}"
        if commission is not None:
            str = str + f", Commission: {commission:.2f}"
    elif action == "c":
        if cash is not None:
            str = str + f", Cash: {cash:.2f}"
        if open is not None:
            str = str + f", Open: {open:.2f}"
        if close is not None:
            str = str + f", Close: {close:.2f}"

    
    return str

def get_result_log_string(gross, net):
    """
    Helper function for logging. Creates a string indicating the summary of
    an operation.

    Args:
        gross (float): the gross outcome
        net (float): the net outcome

    Returns:
        str: The string used for logging
    """
    str = f"OPERATION RESULT - Gross: {gross:.2f}, Net: {net:.2f}"
    return str
