"""
在有回撤之后买入, 涨到回撤前的高点左右卖出
这个策略不适合下跌行情, 在下跌行情中反应比较慢, 等到买的时候, 差不多反弹也结束了
还是会发生比较大的回撤, 但是也没啥办法
"""
import datetime

import talib as ta
import pandas as pd
from core.back_test import BackTest


class MyBackTest(BackTest):
    def sizer(self):
        if self.bs_flag == "B":
            self.trans_amount = self.cash // (self.price + self.commission)
        elif self.bs_flag == "S":
            self.trans_amount = self.amount

    def strategy(self):
        sma_data = ta.MA(self.data["close"], timeperiod=self.parameter["sma"], matype=0)
        slope = ta.LINEARREG_SLOPE(sma_data, timeperiod=self.parameter["slope"])

        if slope.iloc[-2] < 0 and slope.iloc[-1] > 0:
            self.bs_flag = "B"
            self.args["period_max_point"] = max(self.data["close"].iloc[-40:])
        elif self.amount:
            if slope.iloc[-2] > 0 and slope.iloc[-1] < 0:
                self.bs_flag = "S"
            elif (self.data["close"].iloc[-1] - self.args["period_max_point"]) / self.args["period_max_point"] > -0.02:
                if self.data["close"].iloc[-1] < self.data["close"].iloc[-2] < self.data["close"].iloc[-3] < self.data["close"].iloc[-4]:
                    self.bs_flag = "S"

        else:
            pass


if __name__ == "__main__":
    point_data = pd.read_csv("./point_data_000001.csv", index_col=[0], parse_dates=[2])
    basic_data = pd.read_csv("./basic_data_000001.csv", index_col=[0], parse_dates=[2])
    ins = MyBackTest(point_data,
                     datetime.datetime(2016, 5, 1), datetime.datetime(2019, 1, 31),
                     10000, max_period=30,
                     parameter_map={"sma": [5], "slope": [11]}, plot_flag=False,
                     commission=0.0022)
    gain_loss = ins.start()
    print(gain_loss)
