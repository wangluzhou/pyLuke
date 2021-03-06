# encoding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


def alpha_factor(data, i, cycle):
    pass


def onbar(data, i, cycle):
    """计算上一个周期收益率排名，取前3的品种，按照排名权重分配"""
    opt_w = np.zeros(len(data.columns))
    rank = (data.iloc[i - cycle:i, :]).sum().rank(ascending=False, method='max')
    for k in range(len(rank)):
        if rank[k] == 1:
            opt_w[k] = 0.2
        elif rank[k] == 2:
            opt_w[k] = 0.2
        elif rank[k] == 3:
            opt_w[k] = 0.2
        elif rank[k] == 4:
            opt_w[k] = 0.2
        elif rank[k] == 5:
            opt_w[k] = 0.2
    rank = rank.to_frame(name=data.index[i - 1]).T
    return opt_w, rank


def init_data():
    """初始化数据"""
    data = pd.read_excel(u"index_ret.xlsx", sheetname=0)
    data.set_index(["date"], inplace=True)
    # data = data.drop(["054D.CS"], axis=1)
    data = data.drop(["000832.SH"], axis=1)
    money = data.ix[:, ["885009.WI"]]
    data = data.drop(["885009.WI"], axis=1)  # 去除货币基金
    data = data[(data.index > datetime(2009, 1, 1)) & (data.index < datetime(2017, 12, 31))]
    base = pd.read_excel(u"index_ret.xlsx", sheetname=1)
    base.set_index(["date"], inplace=True)
    beta_factor = pd.read_excel(u"beta_factor.xlsx", sheetname=0)
    beta_factor.set_index(["date"], inplace=True)

    return data, base, beta_factor, money


def main():
    data, base, beta_factor, money = init_data()
    rank_df = pd.DataFrame(columns=data.columns)
    consider_beta = False
    # 初始化组合收益率df
    cycle_begin = 23
    cycle_end = 24  # 不包含
    ret = pd.DataFrame(columns=[i for i in range(cycle_begin, cycle_end)], index=data.index)
    # -----------------
    for cycle in range(cycle_begin, cycle_end):
        for i in range(cycle):
            ret.ix[i, cycle] = base.iloc[i, 0]
            opt_w = []
        for i in range(cycle, len(data)):
            if i % cycle == 0:
                opt_w, rank = onbar(data, i, cycle)
                rank_df = rank_df.append(rank)
            ret.ix[i, cycle] = np.dot(opt_w, data.ix[i, :].values)
            if consider_beta:
                if beta_factor.iloc[i, 0] > 0.8:
                    ret.ix[i, cycle] = ret.ix[i, cycle]
                elif 0.6 < beta_factor.iloc[i, 0] <= 0.8:
                    ret.ix[i, cycle] = ret.ix[i, cycle] * 0.8 + money.iloc[i, 0] * 0.2
                elif 0.4 < beta_factor.iloc[i, 0] <= 0.6:
                    ret.ix[i, cycle] = ret.ix[i, cycle] * 0.6 + money.iloc[i, 0] * 0.4
                elif 0.2 < beta_factor.iloc[i, 0] <= 0.4:
                    ret.ix[i, cycle] = ret.ix[i, cycle] * 0.4 + money.iloc[i, 0] * 0.6
                elif 0.0 <= beta_factor.iloc[i, 0] <= 0.2:
                    ret.ix[i, cycle] = ret.ix[i, cycle] * 0.2 + money.iloc[i, 0] * 0.8
                else:
                    raise BaseException

    ret = ret.join(base)
    # ret.to_excel("ret_retranking_cba.xlsx")
    # 将ret转换为净值曲线
    ret = ret.astype(float)  # 必须加上这句话，否则就无法使用exp函数，原因暂时未知
    value = (np.exp(ret).cumprod())  # 净值df
    # value.to_excel("value_retranking.xlsx")
    print (ret.mean() - 0.03 / 250) / ret.std() * np.sqrt(250.0)
    print u"return per year:", (value.iloc[-1, 0] - value.iloc[0, 0]) / value.iloc[0, 0] / (len(value) / 250.0)
    print u"base return per year:", (value.iloc[-1, 1] - value.iloc[0, 1]) / value.iloc[0, 1] / (len(value) / 250.0)
    value.plot()
    plt.show()
    # rank_df.to_excel("rank.xlsx")


if __name__ == "__main__":
    main()
