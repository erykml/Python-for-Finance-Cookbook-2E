# Backtesting a trading strategy based on Bollinger Bands

# import libraries
import backtrader as bt
import datetime
import pandas as pd
from strategy_utils import *

# create a Strategy
class BollingerBandStrategy(bt.Strategy):
    params = (("period", 20),
              ("devfactor", 2.0),)

    def __init__(self):
        # keep track of prices
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open

        # keep track of pending orders
        self.order = None

        # add Bollinger Bands indicator and track the buy/sell signals
        self.b_band = bt.ind.BollingerBands(self.datas[0], 
                                            period=self.p.period, 
                                            devfactor=self.p.devfactor)
        self.buy_signal = bt.ind.CrossOver(self.datas[0], 
                                           self.b_band.lines.bot,
                                           plotname="buy_signal")
        self.sell_signal = bt.ind.CrossOver(self.datas[0], 
                                            self.b_band.lines.top,
                                            plotname="sell_signal")

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
            self.log("Order Failed")

        # reset order -> no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(get_result_log_string(gross=trade.pnl, net=trade.pnlcomm))

    def next_open(self):
        if not self.position:
            if self.buy_signal > 0:
                # calculate the max number of shares ("all-in")
                size = int(self.broker.getcash() / self.datas[0].open)
                # buy order
                log_str = get_action_log_string("b", "c", 
                                                price=self.data_close[0], 
                                                size=size,
                                                cash=self.broker.getcash(),
                                                open=self.data_open[0],
                                                close=self.data_close[0])
                self.log(log_str)
                self.order = self.buy(size=size)
        else:
            if self.sell_signal < 0:
                # sell order
                log_str = get_action_log_string("s", "c", self.data_close[0], 
                                                self.position.size)
                self.log(log_str)
                self.order = self.sell(size=self.position.size)

    def start(self):
        print(f"Initial Portfolio Value: {self.broker.get_value():.2f}")

    def stop(self):
        print(f"Final Portfolio Value: {self.broker.get_value():.2f}")

data = bt.feeds.YahooFinanceData(dataname="MSFT",
                                 fromdate=datetime.datetime(2021, 1, 1),
                                 todate=datetime.datetime(2021, 12, 31))

# Create a cerebro entity
cerebro = bt.Cerebro(stdstats = False, cheat_on_open=True)

# set up the backtest
cerebro.addstrategy(BollingerBandStrategy)
cerebro.adddata(data)
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)
cerebro.addobserver(MyBuySell)
cerebro.addobserver(bt.observers.Value)
cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="time_return")

backtest_result = cerebro.run()

cerebro.plot(iplot=True, volume=False)
