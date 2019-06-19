"""判断趋势示例"""
import datetime

import talib as ta
import pandas as pd
from core.back_test import BackTest


class MyBackTest(BackTest):
    def sizer(self):
        pass

    def strategy(self):
        date_now = self.data["trade_date"].iloc[-1]
        sma_data_20 = ta.MA(self.data["close"], timeperiod=20, matype=0)
        sma_data_20_20 = sma_data_20.iloc[-21:]
        sma_data_20_20_point_raise_flag = sma_data_20_20.rolling(2).apply(lambda x: True if x[1] > x[0] else False)
        raise_percent = sma_data_20_20_point_raise_flag.value_counts()[True] / (len(sma_data_20_20_point_raise_flag) - 1)  # -1是因为窗口函数算出来的第一个值为None

        self.args["trend_result"].append([date_now, sma_data_20_20_point_raise_flag.value_counts()[True]])

    def after_execute(self):
        trend_result = pd.DataFrame(self.args["trend_result"], columns=["trade_date", "raise_num"])
        print(trend_result["raise_num"].value_counts())


if __name__ == "__main__":
    point_data_hs300 = pd.read_csv("./point_data_used_by_trend_hs300.csv", index_col=[0], parse_dates=[2])
    point_data_600030 = pd.read_csv("./point_data_used_by_trend_600030.csv", index_col=[0], parse_dates=[2])
    ins = MyBackTest(point_data_hs300,
                     datetime.datetime(2016, 2, 1), datetime.datetime(2019, 6, 18),
                     10000, max_period=42, plot_flag=True, trend_result=[])
    ins.start()


