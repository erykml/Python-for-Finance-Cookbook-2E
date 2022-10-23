def print_portfolio_summary(perf, weights, assets, name):
    """
    Helper function for printing the performance summary of a portfolio.

    Args:
        perf (pd.Series): Series containing the perf metrics
        weights (np.array): An array containing the portfolio weights
        assets (list): list of the asset names
        name (str): the name of the portfolio
    """
    print(f"{name} portfolio ----")
    print("Performance")
    for index, value in perf.items():
        print(f"{index}: {100 * value:.2f}% ", end="", flush=True)
    print("\nWeights")
    for x, y in zip(assets, weights):
        print(f"{x}: {100*y:.2f}% ", end="", flush=True)