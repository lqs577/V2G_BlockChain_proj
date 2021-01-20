import math
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
from functools import reduce

import xlrd
from scipy.interpolate import make_interp_spline
import seaborn as sns
import pandas
import matplotlib


def paint1():
    workbook1 = xlrd.open_workbook('../sc1std19.xlsx')
    sheet1 = workbook1.sheet_by_index(0)
    data = []
    for i in range(1, 366):
        row_data = []
        for j in range(1, 25):
            row_data.append(sheet1.cell_value(i, j) * 983.99e8)
        data.append(row_data)
    # x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 21, 22, 23]
    # y1 = list1
    # y2 = list2
    # y3 = list3
    # y4 = list4
    # y5 = list5

    # data[300] += data[300]
    # data[300] = data[300][12:36]
    # for i in range(0, 24):
    #     y1[i] += data[300][i]
    # y2[i] += data[300][i]
    # y3[i] += data[300][i]
    # y4[i] += data[300][i]
    # y5[i] += data[300][i]

    x = np.arange(0, 24, 1)
    plt.title('Original load Curve of grid', fontsize='13')
    plt.xlabel("Time/h", fontsize='13')
    plt.ylabel("Load/KW", fontsize='13')

    plt.plot(data[300], c='burlywood', linewidth='2')
    # plt.plot(x, y1, c='darkgreen', label='beta=0.2', linewidth='1')
    # plt.plot(x, y2, c='lightgreen', label='beta=0.35', linewidth='1')
    # plt.plot(x, y3, c='limegreen', label='beta=0.5', linewidth='1')
    # plt.plot(x, y4, c='g', label='beta=0.65', linewidth='1')
    # plt.plot(x, y5, c='darkgreen', label='beta=0.8', linewidth='1')
    plt.xticks([0, 6, 12, 18, 24], ["0:00", "6:00", "12:00", "18:00", "0:00"])
    plt.grid(axis='y')  # 添加网格
    # sns.despine()
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    # plt.legend(fontsize="12")
    plt.savefig("original_load_curve.jpg")
    plt.show()


def paint2(list1, list2, list3):
    a = np.array(list1)
    b = np.array(list2)
    c = np.array(list3)
    # 应要求关闭横坐标

    plt.figure(figsize=(14, 9))

    plt.xlabel("Time", fontsize='12')
    plt.ylabel("Power/kw", fontsize='12')
    plt.xticks(range(0, 24))
    plt.yticks()
    plt.title('Charging and Discharging power of EVs')
    x = list(range(len(c)))
    y = list(range(len(a)))
    for i in range(len(x)):
        # y[i] = y[i] * 1.3
        x[i] = x[i] - 0.5

    rect_a = plt.bar(y, a, color='aquamarine', width=0.4)
    rect_b = plt.bar(y, -b, color='palegoldenrod', width=0.4)

    rect_c = plt.bar(x, c, color='burlywood', width=0.4)
    # ncol 同一行显示2个图例,bbox_to_anchor 控制具体的位置 0代表底部，0.5代表中部，frameon去除边框
    plt.legend((rect_c, rect_a, rect_b,), ("Original charging power", "Charging power", "Discharging power"),
               loc='upper center', fontsize="9")

    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "24:00"])
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.gca().yaxis.get_major_formatter().set_powerlimits((0, 2))
    plt.grid(axis='y')  # 添加网格
    # sns.despine()
    plt.tick_params(labelsize=10)  # 刻度字体大小13
    plt.savefig("ch_dc_numbers.jpg")
    plt.show()
    return 0


def paint3(list1):
    y1 = list1
    x = np.arange(0, 24, 1)
    xnew = np.linspace(x.min(), x.max(), 300)
    y_smooth1 = make_interp_spline(x, y1)(xnew)
    plt.title('a) Without V2G', fontsize='13')
    plt.xlabel("Time", fontsize='13')
    plt.ylabel("Transactions number/k", fontsize='13')

    plt.plot(list1, c='b', label='original curve', linewidth='1')
    plt.plot(x, y1, c='darkgreen', label='beta=0.2', linewidth='1')

    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["12:00", "", "18:00", "", "0:00", "", "6:00", "", "12:00"])
    plt.grid(axis='y')  # 添加网格
    sns.despine()
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.legend(fontsize="12")
    plt.savefig("load_curve2.jpg")
    plt.show()


def paint4(list1, list2, title, filename):
    length = len(list1)
    length2 = len(list2)
    x = np.arange(0, length, 1)
    x2 = np.arange(0, length2, 1)
    # x2 *= int(max(length, length2) / length2)
    x2 *= 10

    y1 = list1
    y2 = list2
    x_new = np.linspace(x.min(), x.max(), 300)
    # x2_new = np.linspace(x2.min(), x2.max(), 300)
    y_smooth1 = make_interp_spline(x, y1)(x_new)
    # y_smooth2 = make_interp_spline(x2, y2)(x2_new)

    plt.title(title, fontsize='14')
    plt.xlabel("Time (h)", fontsize='14')
    plt.ylabel("Rate (numbers/min)", fontsize='14')

    plt.plot(x_new, y_smooth1, c='burlywood', label='Instantaneous rate', linewidth='2')
    plt.plot(x2, y2, c='green', label='Average rate', linewidth='2', marker="o", markersize=3)

    plt.xticks([0, int(length / 8), int(length / 4), int(3 * length / 8), int(2 * length / 4), int(5 * length / 8),
                int(3 * length / 4), int(7 * length / 8), length],
               ["0:00", '', "6:00", '', "12:00", '', "18:00", '', "0:00"])
    plt.grid(axis='y')  # 添加网格
    # sns.despine()
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.legend(fontsize="13")
    plt.savefig(filename)
    plt.show()


def paint5(list1, list2):
    length_list = []
    y_list = []
    for item in list1:
        length_list.append(len(item))
        y_list.append(item)
    for item in list2:
        length_list.append(len(item))
        y_list.append(item)

    length = max(length_list)
    print(length)
    x_list = []
    for length1 in length_list:
        x1 = np.arange(0, length1, 1)
        x_list.append(x1)

    for x_item in x_list:
        x_item *= int(length / len(x_item))

    x_new_list = []
    for i in range(0, int(len(x_list) / 2)):
        x_new = np.linspace(x_list[i].min(), x_list[i].max(), 300)
        x_new_list.append(x_new)

    y_smooth_list = []
    for i in range(0, int(len(y_list) / 2)):
        y_smooth = make_interp_spline(x_list[i], y_list[i])(x_new_list[i])
        y_smooth_list.append(y_smooth)

    plt.title('(f) Transaction subchain', fontsize='14')
    plt.xlabel("Time (h)", fontsize='14')
    plt.ylabel("Rate (numbers/min)", fontsize='14')

    color_list = ['burlywood', 'crimson', 'skyblue', 'darkseagreen', 'firebrick', 'mediumorchid']
    for i in range(0, int(len(x_list) / 2)):
        plt.plot(x_new_list[i], y_smooth_list[i], c=color_list[i], label='Subchain ' + str(i), linewidth='2')
        # temp = i + len(x_new_list)
        # if i == 0:
        #     plt.plot(x_list[temp], y_list[temp], c=color_list[temp], label='Average rate' + str(i), linewidth='2',
        #              marker="o",
        #              markersize=3)
        # else:
        #     plt.plot(x_list[temp], y_list[temp], c=color_list[temp], linewidth='2',
        #              marker="o",
        #              markersize=3)

    plt.xticks([0, int(length / 8), int(length / 4), int(3 * length / 8), int(2 * length / 4), int(5 * length / 8),
                int(3 * length / 4), int(7 * length / 8), length],
               ["0:00", '', "6:00", '', "12:00", '', "18:00", '', "0:00"])
    plt.grid(axis='y')  # 添加网格
    # sns.despine()
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.legend(fontsize="13")
    plt.savefig("6.jpg")
    plt.show()


def gamma(list1, bins):
    x = np.arange(0, 24, 1)
    y = st.gamma.pdf(x, 5, scale=1)
    y1 = st.gamma.pdf(x, 3, scale=2)

    plt.title('EV arrival and departure distribution', fontsize='13')
    plt.xlabel("Time", fontsize='13')
    plt.ylabel("Density/proportion", fontsize='13')

    plt.plot(x, y, c='darkgoldenrod', label='Arrival', linewidth='1')
    plt.plot(x, y1, c='gold', label='Departure', linewidth='1')

    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "0:00"])
    plt.grid(axis='y')  # 添加网格
    sns.despine()
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.legend(fontsize="12")
    plt.savefig("EV_arr_depart.jpg")
    plt.show()


if __name__ == '__main__':
    paint1()
    # x = np.arange(0, 24, 1)
    # # paint2([1111, 2], [222222, 34])
    # xnew = np.linspace(x.min(), x.max(), 300)
    # # # y2 = st.gamma.pdf(x, 2, scale=2)  # "α=2,β=2"
    # # # y3 = st.gamma.pdf(x-4, 3, scale=2)  # "α=3,β=2"
    # # # y4 = st.gamma.pdf(x, 5, scale=1)  # "α=5,β=1"
    # # # y5 = st.gamma.pdf(x, 9, scale=0.5)  # "α=9,β=0.5"
    # y1 = [0, 0.001, 0.002, 0.002, 0.002, 0.003, 0.004, 0.0052, 0.0063, 0.009, 0.02, 0.04, 0.06, 0.08, 0.03, 0.06, 0.10,
    #       0.15, 0.20, 0.15, 0.08, 0.04, 0.02, 0.01]
    # y2 = [0, 0.001, 0.002, 0.002, 0.01, 0.02, 0.05, 0.09, 0.14, 0.20, 0.12, 0.04, 0.03, 0.06, 0.08, 0.03, 0.02,
    #       0.015, 0.01, 0.005, 0.003, 0.002, 0.001, 0.0005]
    # sum1 = 0
    # for i in y1:
    #     sum1 += i
    # for i in y1:

    #     i = (i / sum1)
    # sum1 = 0
    # for i in y2:
    #     sum1 += i
    # for i in y2:
    #     i = (i / sum1)
    # y_smooth1 = make_interp_spline(x, y1)(xnew)
    # y_smooth2 = make_interp_spline(x, y2)(xnew)
    #
    # fig = plt.figure(figsize=(7.5, 4.5))
    # plt.title('Departure and Arrival Time Analysis', fontsize='14')
    # plt.xlabel("Time", fontsize='14')
    # plt.ylabel("Density", fontsize='14')
    # plt.plot(xnew, y_smooth1, c="darkgoldenrod", linewidth='2', label="Arrival time")
    # plt.plot(xnew, y_smooth2, color="gold", linewidth='2', label="Departure time")
    # # x轴
    # plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "0:00"])
    # plt.tick_params(labelsize=12)  # 刻度字体大小13
    #
    # plt.legend(fontsize="14")
    # plt.grid(axis='y')  # 添加网格
    # plt.ylim((0, 0.35))
    # sns.despine()
    # plt.savefig("temporal_distribution.jpg")
    # plt.show()
