"""在有巨大回撤之后, 20日均线趋于平缓的时候, 买入"""
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
        slope_30 = ta.LINEARREG_SLOPE(sma_data, timeperiod=self.parameter["slope"])

        # if slope_30.iloc[-2] < 0 and slope_30.iloc[-1] > 0:
        if (self.data["close"].iloc[-1] - max(self.data["close"].iloc[-40:])) / max(self.data["close"].iloc[-40:]) < -0.2 and self.data["close"].iloc[-1] > self.data["close"].iloc[-2]:
            self.bs_flag = "B"
        elif slope_30.iloc[-2] > 0 and slope_30.iloc[-1] < 0:
            self.bs_flag = "S"
        else:
            pass


if __name__ == "__main__":
    point_data = pd.read_csv("./point_data_000001.csv", index_col=[0], parse_dates=[2])
    basic_data = pd.read_csv("./basic_data_000001.csv", index_col=[0], parse_dates=[2])
    ins = MyBackTest(point_data,
                     datetime.datetime(2016, 5, 1), datetime.datetime(2019, 1, 31),
                     10000, max_period=30,
                     parameter_map={"sma": [20], "slope": [13, 14]}, plot_flag=True,
                     commission=0.0022)
    gain_loss = ins.start()
    print(gain_loss)
