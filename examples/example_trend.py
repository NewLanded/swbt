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
    """
    {
        "month": {  # 2-3个月的趋势
            "hs300": {
                "稳定平静": [],
                "稳定波动": [],
                "上涨平静": [],
                "上涨波动": [
                    [datetime.datetime(2016, 2, 1), datetime.datetime(2018, 1, 20)],
                    [datetime.datetime(2019, 1, 1), datetime.datetime(2019, 4, 15)]
                    ],
                "下跌平静": [],
                "下跌波动": [
                    [datetime.datetime(2018, 1, 20), datetime.datetime(2019, 1, 1)],
                    [datetime.datetime(2019, 4, 15), datetime.datetime(2016, 6, 17)]
                    ]
            },
            "600030": {
                "稳定平静": [],
                "稳定波动": [
                    [datetime.datetime(2016, 2, 1), datetime.datetime(2017, 5, 1)],
                    [datetime.datetime(2018, 10, 20), datetime.datetime(2018, 12, 20)],
                    ],
                "上涨平静": [
                    [datetime.datetime(2018, 12, 20), datetime.datetime(2019, 3, 7)]
                    ],
                "上涨波动": [
                    [datetime.datetime(2017, 5, 1), datetime.datetime(2018, 1, 24)]
                    ],
                "下跌平静": [],
                "下跌波动": [
                    [datetime.datetime(2018, 1, 24), datetime.datetime(2018, 10, 20)]
                    [datetime.datetime(2019, 3, 7), datetime.datetime(2019, 6, 17)]
                    ]
            }
        },
        "week": {  # 1-2个星期的趋势
            "hs300": {
                "稳定平静": [],
                "稳定波动": [],
                "上涨平静": [],
                "上涨波动": [],
                "下跌平静": [],
                "下跌波动": []
            },
            "600030": {
                "稳定平静": [],
                "稳定波动": [],
                "上涨平静": [],
                "上涨波动": [],
                "下跌平静": [],
                "下跌波动": []
            }
        }
    }
    """
    point_data_hs300 = pd.read_csv("./point_data_used_by_trend_hs300.csv", index_col=[0], parse_dates=[2])
    point_data_600030 = pd.read_csv("./point_data_used_by_trend_600030.csv", index_col=[0], parse_dates=[2])
    ins = MyBackTest(point_data_hs300,
                     datetime.datetime(2016, 2, 1), datetime.datetime(2019, 6, 18),
                     10000, max_period=42, plot_flag=True, trend_result=[])
    ins.start()


