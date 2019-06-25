import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import pandas as pd


def plot_data(point_data, bs_data, manual_plot_data):
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
    sns.set()
    sns.set_palette(sns.color_palette('dark'))

    fig = plt.figure(figsize=(12, 9))

    ax1 = plt.axes([0.1, 0.2, 0.8, 0.5])

    b_date_bs_data = bs_data[bs_data["bs_flag"] == "B"]
    b_date_point_data = point_data[point_data["trade_date"].isin(b_date_bs_data["trade_date"])]

    s_date_bs_data = bs_data[bs_data["bs_flag"] == "S"]
    s_date_point_data = point_data[point_data["trade_date"].isin(s_date_bs_data["trade_date"])]

    ax1.plot(point_data["trade_date"], point_data["close"], ls="-", lw=1, color='y')
    ax1.plot(b_date_point_data["trade_date"], b_date_point_data["close"], "o", color='r', markersize=3)
    ax1.plot(s_date_point_data["trade_date"], s_date_point_data["close"], "o", color='g', markersize=3)
    labels = ['close point', 'buy', "sell"]

    if not manual_plot_data.empty:
        manual_plot_data_columns = list(manual_plot_data.columns)
        manual_plot_data_columns.remove("trade_date")
        for manual_plot_data_column in manual_plot_data_columns:
            ax1.plot(manual_plot_data["trade_date"], manual_plot_data[manual_plot_data_column], ls="-", lw=1)
            labels.append(manual_plot_data_column)

    ax1.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95), ncol=3, title="color meaning", shadow=True, fancybox=True, labels=labels)

    ax2 = plt.axes([0.1, 0.75, 0.8, 0.2], sharex=ax1)
    ax2.plot(bs_data["trade_date"], bs_data["property"], ls="-", lw=1)
    ax2.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95), ncol=3, title="color meaning", shadow=True, fancybox=True, labels=['property'])

    ax1.grid(axis="y")
    ax2.grid(axis="y")

    plt.show()


def plot_data_2(ts_code, point_data, point_data_part):
    """记录matplotlib使用过程中x轴刻度设置出的一些问题的解决方法
    1. x轴刻度为日期且不连续
    2. 设置刻度间隔
    """
    sns.set()
    sns.set_palette(sns.color_palette('dark'))

    point_data_part['xticks_int_index'] = [i for i in range(len(point_data_part["trade_date"]))]
    xticks_index_map = point_data_part["trade_date"].apply(lambda x: x.strftime("%Y-%m-%d"))

    def format_date(x, pos=None):
        if x < 0 or x > len(xticks_index_map) - 1:
            return ''
        return xticks_index_map.iloc[int(x)]

    fig = plt.figure(figsize=(16, 9))

    ax1 = plt.axes([0, 0, 0.7, 1])
    ax1.plot(point_data["trade_date"], point_data["close"], ls="-", lw=1, color='k')
    labels = ['close point']
    ax1.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95), ncol=3, title=ts_code, shadow=True, fancybox=True, labels=labels)
    ax1.grid(axis="y")

    ax2 = plt.axes([0.7, 0.3, 0.3, 0.7])
    ax2.plot(point_data_part["xticks_int_index"], point_data_part["close"], ls="-", lw=1, color='k')
    ax2.plot(point_data_part["xticks_int_index"], point_data_part["sma_data_5"], ls="-", lw=1, color='r')
    ax2.plot(point_data_part["xticks_int_index"], point_data_part["sma_data_10"], ls="-", lw=1, color='g')
    labels = ['close point', 'sma_5', "sma_10"]
    ax2.legend(loc="upper left", bbox_to_anchor=(0.05, 0.95), ncol=1, title=ts_code, shadow=True, fancybox=True, labels=labels, fontsize='small')
    ax2.grid(axis="y")

    import matplotlib.ticker as ticker
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))  # 来强制指定每隔5个刻度，设定一个主刻度
    # 原始数据中日期是不连续的, 反应到x轴的刻度上, x轴会默认补全所有日期, 所以有的日期就会没数据, 这个方法可以去掉没有数据的日期
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.xticks(rotation=90)

    ax3 = plt.axes([0.7, 0.05, 0.3, 0.1], sharex=ax2)
    ax3.bar(point_data_part["xticks_int_index"], point_data_part["vol"], width=1)
    # ax3.bar(point_data_part["trade_date"], point_data_part["vol"], width=np.timedelta64(24, 'h'))  # 如果横坐标是时间的话, width=np.timedelta64(24, 'h') 要使用这种形式
    ax3.grid(axis="y")
    plt.xticks(rotation=90)

    plt.show()


if __name__ == "__main__":
    point_data = pd.read_csv("../examples/point_data_000001.csv", index_col=[0], parse_dates=[2])
    bs_data = pd.read_csv("../examples/bs_data.csv", index_col=[0], parse_dates=[1])
    plot_data(point_data, bs_data, pd.DataFrame())
