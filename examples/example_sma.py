"""简单移动平均线示例, 五日线上穿十日线则买入, 五日线下穿十日线则卖出"""
import datetime

import talib as ta
import pandas as pd
from core.back_test import BackTest


class MyBackTest(BackTest):
    def sizer(self):
        if self.bs_flag == "B":
            self.trans_amount = (self.cash // (self.price + self.commission)) // 2
        elif self.bs_flag == "S":
            self.trans_amount = self.amount

    def strategy(self):
        sma_data_5 = ta.MA(self.data["close"], timeperiod=self.parameter["sma_5"], matype=0)
        sma_data_10 = ta.MA(self.data["close"], timeperiod=self.parameter["sma_10"], matype=0)

        if sma_data_5.iloc[-2] <= sma_data_10.iloc[-2] and sma_data_5.iloc[-1] > sma_data_10.iloc[-1]:
            self.bs_flag = "B"
        elif sma_data_5.iloc[-2] >= sma_data_10.iloc[-2] and sma_data_5.iloc[-1] < sma_data_10.iloc[-1]:
            self.bs_flag = "S"
        else:
            pass

        self._add_manual_plot_data({"trade_date": self.data["trade_date"].iloc[-1], "sma_data_5": sma_data_5.iloc[-1], "sma_data_10": sma_data_10.iloc[-1]})  # 将 sma_data_5 和 sma_data_10 画图


if __name__ == "__main__":
    point_data = pd.read_csv("./point_data_000001.csv", index_col=[0], parse_dates=[2])
    basic_data = pd.read_csv("./basic_data_000001.csv", index_col=[0], parse_dates=[2])
    ins = MyBackTest(point_data,
                     datetime.datetime(2016, 5, 1), datetime.datetime(2019, 1, 31),
                     10000, max_period=11,
                     parameter_map={"sma_5": [5, 7], "sma_10": [10, 14]}, plot_flag=True,
                     commission=0.0022)
    gain_loss = ins.start()
    print(gain_loss)

