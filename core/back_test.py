import copy

import pandas as pd

from core.plot_data import plot_data


class BackTest:
    """
    回测核心类, 继承该类以定制策略, 覆盖 sizer 及 strategy
    """

    def __init__(self, data, start_date, end_date, init_funding, max_period=0, commission=0.0022, plot_flag=False, parameter_map=None, **kwargs):
        """
        初始化类
        :param data: 回测数据, DataFrame, 至少包含日期与开盘价, 收盘价, 最高价, 最低价, 以日期升序排序
            trade_date open high low close
        1   2016-01-01 10   11    9   10.5
        2   2016-01-02 10   11    9   10.5
        3   2016-01-03 10   11    9   10.5
        :param start_date: 回测开始时间 datetime.datetime
        :param end_date: 回测结束时间 datetime.datetime
        :param init_funding: 初始资金
        :param max_period: 数据区间, 计算过程中, 至少需要多少天的数据, 比如原始数据从1号开始, 至少需要5天的数据计算平均值, 那么真正的计算过程会从6号开始
        :param commission: 手续费, 这个目前不太准, 只是一个大约的数值, 并不紧急
        :param plot_flag: 是否画图
        :param parameter_map: 测试不同参数效果的参数列表
            {
                "parameter_1": [1, 2],
                "parameter_2": [3, 4]
            }
            运行时会组合为
            [1, 3], [1, 4], [2, 3], [2, 4] 四种条件进行测试, 数据放在self.parameter.parameter_1 和 self.parameter.parameter_2 里
        :param kwargs: 其他参数, 会放在self.args中供全局调用
        """
        self.data_all = data[(start_date <= data["trade_date"]) & (data["trade_date"] <= end_date)]
        self.start_date = start_date
        self.end_date = end_date
        self.cash = init_funding  # 可用资金
        self.max_period = max_period
        self.commission = commission
        self.plot_flag = plot_flag
        self.parameter_map = parameter_map
        self.args = kwargs

        self.amount = 0  # 持仓数量
        self.bs_flag = None  # 交易标志, 买: B, 卖: S
        self.price = 0  # 交易价格
        self.trans_amount = 0  # 交易数量

        self.parameter = {}
        self.result = []  # 存储每日的交易持仓等信息, [日期, 买卖标志, 交易价格, 交易数量, 现金, 持仓数量, 资产]
        self.manual_plot_data = {}  # 自定义画图的数据

    def sizer(self):
        """
        获取单次交易买卖数量, 默认使用全部可用金钱或全部可用券
        self.price 默认为当日收盘价, 可使用 self.data中的数据自定义
        :return:
        """
        if self.bs_flag == "B":
            self.trans_amount = self.cash // (self.price + self.commission)
        elif self.bs_flag == "S":
            self.trans_amount = self.amount

    def strategy(self):
        """
        交易策略, 需设置 self.bs_flag 为 B 或 S, 若无买卖信号则无需设置
        :return:
        """
        pass

    def _add_manual_plot_data(self, plot_data_dict):
        """
        将需要画图的数据, 以key, value的形式写在plot_data_dict中 (plot_data_dict至少需要包含一个trade_date)
        :param plot_data_dict:  {
            trade_date: datetime.datetime(2016, 1, 1),
            my_point: 10,
            ...
        }
        :return:
        """
        self.manual_plot_data[plot_data_dict["trade_date"]] = {}
        for k, v in plot_data_dict.items():
            self.manual_plot_data[plot_data_dict["trade_date"]][k] = v

    def plot(self):
        """作图, 使用self.result作为数据源"""
        trade_date_list = list(self.manual_plot_data)
        trade_date_list.sort()
        if trade_date_list:
            manual_plot_data = {}
            key_list = list(self.manual_plot_data[trade_date_list[0]])
            for date in trade_date_list:
                for key in key_list:
                    manual_plot_data.setdefault(key, []).append(self.manual_plot_data.get(date, {}).get(key, None))
            manual_plot_data = pd.DataFrame(manual_plot_data)
        else:
            manual_plot_data = pd.DataFrame()

        plot_data(self.data_all, self.result, manual_plot_data)

    def _bs(self):
        """
        计算买卖数据
        :return:
        """
        if self.bs_flag == "B":
            self.amount = self.amount + self.trans_amount if self.amount else self.trans_amount
            self.cash = self.cash - self.trans_amount * (self.price + self.commission)
        elif self.bs_flag == "S":
            self.amount = self.amount - self.trans_amount
            self.cash = self.cash + self.trans_amount * (self.price + self.commission)

    def _execute(self):
        """
        执行买卖
        :return:
        """
        for date_now in list(self.data_all["trade_date"])[self.max_period:]:
            self.data = self.data_all[self.data_all["trade_date"] <= date_now]
            self.price = self.data.iloc[-1]["close"]

            self.strategy()
            if self.bs_flag:
                self.sizer()
                self._bs()

            self.result.append([date_now, self.bs_flag, self.price, self.trans_amount, self.cash, self.amount, self.cash + self.amount * self.data.iloc[-1]["close"]])
            self.trans_amount = None
            self.bs_flag = None

        if self.plot_flag is True:
            self.result = pd.DataFrame(self.result, columns=["trade_date", "bs_flag", "price", "trans_amount", "cash", "amount", "property"])
            # self.result.to_csv("./bs_data.csv")
            self.plot()

        return self.cash + self.amount * self.data.iloc[-1]["close"]

    def _iter_list(self, parameter_map_value_list, parameter_all_list, parameter_now_list):
        """
        [[1, 2], [3, 4]] --> [1, 3], [1, 4], [2, 3], [2, 4]
        :param parameter_map_value_list: [[1, 2], [3, 4]]
        :param parameter_all_list: 空列表, 运行后的结果会放在此处
        :param parameter_now_list: 空列表
        """
        data_list, parameter_map_value_list = parameter_map_value_list[0], parameter_map_value_list[1:]
        if parameter_map_value_list:
            for parameter in data_list:
                parameter_now_list.append(parameter)
                self._iter_list(parameter_map_value_list, parameter_all_list, parameter_now_list)
                parameter_now_list.pop()
        else:
            for parameter in data_list:
                parameter_now_list_copy = copy.deepcopy(parameter_now_list)
                parameter_now_list_copy.append(parameter)
                parameter_all_list.append(parameter_now_list_copy)

    def start(self):
        """
        开始运行
        :return:
        """
        if self.parameter_map:
            keys_list = list(self.parameter_map)
            parameter_map_value_list = [self.parameter_map[key] for key in keys_list]
            parameter_all_list = []
            self._iter_list(parameter_map_value_list, parameter_all_list, [])

            result = {}
            parameter_str = ""
            for parameter_list in parameter_all_list:
                for key, value in zip(keys_list, parameter_list):
                    self.parameter[key] = value
                    parameter_str += str(key) + ":" + str(value) + ","
                gain_loss = self._execute()
                result[parameter_str] = gain_loss
                parameter_str = ""

        else:
            gain_loss = self._execute()
            result = {None: gain_loss}
        return result
