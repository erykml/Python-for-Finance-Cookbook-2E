# Backtesting a trading strategy based on the Simple Moving Average
 
from datetime import datetime
import backtrader as bt
from strategy_utils import *
import pandas as pd
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier


# Create a Strategy
class MeanVariancePortfStrategy(bt.Strategy):
    params = (("n_periods", 252), )

    def __init__(self):  
        # track number of days
        self.day_counter = 0
               
    def log(self, txt):
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f"{dt}: {txt}")

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order already submitted/accepted - no action required
            return

        # report executed order
        if order.status in [order.Completed]:

            direction = "b" if order.isbuy() else "s"
            log_str = get_action_log_string(
                    asset=order.data._name,
                    dir=direction, 
                    action="e", 
                    price=order.executed.price,
                    size=order.executed.size,
                    cost=order.executed.value, 
                    commission=order.executed.comm
                )
            self.log(log_str)

        # report failed order
        elif order.status in [order.Canceled, order.Margin, 
                              order.Rejected]:
            self.log(f"Order Failed: {order.data._name}")

        # reset order -> no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(get_result_log_string(gross=trade.pnl, net=trade.pnlcomm))

    def next(self):

        self.day_counter += 1
        if self.day_counter < self.p.n_periods:
            return

        today = self.datas[0].datetime.date()
        if today.weekday() != 4: 
            return

        current_portf = {}
        for data in self.datas:
            current_portf[data._name] = self.positions[data].size * data.close[0]
        portf_df = pd.DataFrame(current_portf, index=[0])
        print(f"Current allocation as of {today}")
        print(portf_df / portf_df.sum(axis=1).squeeze())

        price_dict = {}
        for data in self.datas:
            price_dict[data._name] = data.close.get(0, self.p.n_periods+1)

        prices_df = pd.DataFrame(price_dict)

        mu = mean_historical_return(prices_df)
        S = CovarianceShrinkage(prices_df).ledoit_wolf()

        ef = EfficientFrontier(mu, S)
        weights = ef.min_volatility()
        print(f"Optimal allocation identified on {today}")
        print(pd.DataFrame(ef.clean_weights(), index=[0]))

        for allocation in list(ef.clean_weights().items()):
            self.order_target_percent(data=allocation[0],
                                      target=allocation[1])

    def start(self):
        print(f"Initial Portfolio Value: {self.broker.get_value():.2f}")

    def stop(self):
        print(f"Final Portfolio Value: {self.broker.get_value():.2f}")

# download data
TICKERS = ["FB", "AMZN", "AAPL", "NFLX", "GOOG"]
data_list = []

for ticker in TICKERS:
    data = bt.feeds.YahooFinanceData(
        dataname=ticker,
        fromdate=datetime(2020, 1, 1),
        todate=datetime(2021, 12, 31)
    )
    data_list.append(data)

class FractionalTradesCommission(bt.CommissionInfo):
    def getsize(self, price, cash):
        """Returns the fractional size"""
        return self.p.leverage * (cash / price)

cerebro = bt.Cerebro(stdstats = False)

cerebro.addstrategy(MeanVariancePortfStrategy)

for ind, ticker in enumerate(TICKERS):
    cerebro.adddata(data_list[ind], name=ticker)

cerebro.broker.setcash(10000.0)
cerebro.broker.addcommissioninfo(FractionalTradesCommission(commission=0))
cerebro.addobserver(MyBuySell)
cerebro.addobserver(bt.observers.Value)

# run backtest
cerebro.run()
