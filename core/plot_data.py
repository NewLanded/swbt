import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import pandas as pd


def plot_data(point_data, bs_data):
    """
    绘图
    :param point_data: 回测数据, DataFrame, 至少包含日期与开盘价, 收盘价, 最高价, 最低价, 以日期升序排序
            trade_date open high low close
        1   2016-01-01 10   11    9   10.5
        2   2016-01-02 10   11    9   10.5
        3   2016-01-03 10   11    9   10.5
    :param bs_data: 买卖数据及结果
            "trade_date", "bs_flag", "price", "trans_amount", "cash", "amount", "property"
        1   2016-01-01
        2   2016-01-02
        3   2016-01-03
    :return:
    """

    """
    首先要创建各个子图的坐标轴，
    传入一个四元列表参数：[x,y,width,height]，用来表示这个子图坐标轴原点的x坐标、y坐标，以及宽和高。
    值得注意的是，这四个值的取值范围都是[0,1]，我们约定整个大图的左下端为原点(0,0)，右上端为(1,1)。
    那么x,y的取值就表示该子图坐标原点的横坐标值和纵坐标值占大图整个长宽的比例。而width和height则表示子图的宽和高占整个大图的宽和高的比例。
    如果不传入参数则表示选取默认坐标轴，即大图的坐标轴。
    """
    fig = plt.figure(figsize=(12, 9))

    ax1 = plt.axes([0.1, 0.2, 0.8, 0.5])

    b_date_bs_data = bs_data[bs_data["bs_flag"] == "B"]
    b_date_point_data = point_data[point_data["trade_date"].isin(b_date_bs_data["trade_date"])]

    s_date_bs_data = bs_data[bs_data["bs_flag"] == "S"]
    s_date_point_data = point_data[point_data["trade_date"].isin(s_date_bs_data["trade_date"])]

    ax1.plot(point_data["trade_date"], point_data["close"], ls="-", lw=1, color='g')
    ax1.plot(b_date_point_data["trade_date"], b_date_point_data["close"], "o", color='r', markersize=3)
    ax1.plot(s_date_point_data["trade_date"], s_date_point_data["close"], "o", color='b', markersize=3)
    ax1.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95), ncol=3, title="color meaning", shadow=True, fancybox=True, labels=['close point', 'buy', "sell"])

    ax2 = plt.axes([0.1, 0.75, 0.8, 0.2], sharex=ax1)
    ax2.plot(bs_data["trade_date"], bs_data["property"], ls="-", lw=1)
    ax2.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95), ncol=3, title="color meaning", shadow=True, fancybox=True, labels=['property'])

    ax1.grid(axis="y")
    ax2.grid(axis="y")

    plt.show()


if __name__ == "__main__":
    point_data = pd.read_csv("../examples/point_data_000001.csv", index_col=[0], parse_dates=[2])
    bs_data = pd.read_csv("../examples/bs_data.csv", index_col=[0], parse_dates=[1])
    plot_data(point_data, bs_data)
