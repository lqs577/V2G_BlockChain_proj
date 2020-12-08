import xlrd
import xlwt
import math
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
from functools import reduce
from scipy.interpolate import make_interp_spline
import seaborn as sns
import pandas
import matplotlib


def calculate_p_req():
    workbook1 = xlrd.open_workbook('./sc1std19.xlsx')
    sheet1 = workbook1.sheet_by_index(0)
    data = []
    for i in range(1, 366):
        row_data = []
        for j in range(1, 25):
            row_data.append(sheet1.cell_value(i, j) * 983.99e8)
        data.append(row_data)
    p_low = 1.05e7
    p_high = 1.15e7
    p_req_list = []
    for item in data[300]:
        if item > p_high:
            p_req_list.append(item - p_high)
        elif item < p_low:
            p_req_list.append(item - p_low)
        else:
            p_req_list.append(0)
    print("p_req_list= " + str(p_req_list))
    print("complete calculating p_req")
    return p_req_list


def paint1(list1, list2, list3, list4, list5):
    workbook1 = xlrd.open_workbook('./sc1std19.xlsx')
    sheet1 = workbook1.sheet_by_index(0)
    data = []
    for i in range(1, 366):
        row_data = []
        for j in range(1, 25):
            row_data.append(sheet1.cell_value(i, j) * 983.99e8)
        data.append(row_data)
    # x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 10, 21, 22, 23]
    y1 = list1
    y2 = list2
    y3 = list3
    y4 = list4
    y5 = list5
    for i in range(0, 24):
        y1[i] += data[300][i]
        y2[i] += data[300][i]
        y3[i] += data[300][i]
        y4[i] += data[300][i]
        y5[i] += data[300][i]

    x = np.arange(0, 24, 1)
    plt.title('Load Curve of grid', fontsize='13')
    plt.xlabel("Time", fontsize='13')
    plt.ylabel("Load/KW", fontsize='13')
    plt.plot(data[300], c='b', label='original curve', linewidth='1')
    plt.plot(x, y1, c='bisque', label='beta=0.2', linewidth='1')
    plt.plot(x, y2, c='lightgreen', label='beta=0.35', linewidth='1')
    plt.plot(x, y3, c='limegreen', label='beta=0.5', linewidth='1')
    plt.plot(x, y4, c='g', label='beta=0.65', linewidth='1')
    plt.plot(x, y5, c='darkgreen', label='beta=0.8', linewidth='1')
    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "0:00"])
    plt.grid(axis='y')  # 添加网格
    sns.despine()
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.legend(fontsize="12")
    plt.savefig("load_curve1.jpg")
    plt.show()


def paint2(list1, list2):
    a = np.array(list1)
    b = np.array(list2)
    # 应要求关闭横坐标
    plt.xlabel("Time", fontsize='12')
    plt.ylabel("Power/kw", fontsize='12')
    plt.xticks(range(0, 24))
    plt.yticks()
    plt.title('Sum of Charging and Discharging power of EV')
    rect_a = plt.bar(range(len(a)), a, color='aquamarine', width=0.4)
    rect_b = plt.bar(range(len(b)), -b, color='palegoldenrod', width=0.4)
    # ncol 同一行显示2个图例,bbox_to_anchor 控制具体的位置 0代表底部，0.5代表中部，frameon去除边框
    plt.legend((rect_a, rect_b,), ("Charging power", "Discharging power"),
               loc='upper right', fontsize="9")

    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "0:00"])
    plt.tick_params(labelsize=12)  # 刻度字体大小13
    plt.gca().yaxis.get_major_formatter().set_powerlimits((0, 2))
    plt.grid(axis='y')  # 添加网格
    sns.despine()
    plt.tick_params(labelsize=10)  # 刻度字体大小13
    plt.savefig("ch_dc_numbers.jpg")
    plt.show()
    return 0


def gamma(n, alpha, beta):
    result = []
    for i in n:
        m = math.pow(i, alpha - 1) * math.pow(beta, alpha) * math.exp(-1 * beta * i)
        if alpha > 1:
            accum = 1
            for j in range(1, alpha):
                accum *= j
            result.append(m / accum)
        else:
            result.append(m)
    return result


if __name__ == '__main__':
    x = np.arange(0, 24, 1)
    # paint2([1111, 2], [222222, 34])
    xnew = np.linspace(x.min(), x.max(), 300)
    # # y2 = st.gamma.pdf(x, 2, scale=2)  # "α=2,β=2"
    # # y3 = st.gamma.pdf(x-4, 3, scale=2)  # "α=3,β=2"
    # # y4 = st.gamma.pdf(x, 5, scale=1)  # "α=5,β=1"
    # # y5 = st.gamma.pdf(x, 9, scale=0.5)  # "α=9,β=0.5"
    y1 = [0, 0.001, 0.002, 0.002, 0.002, 0.003, 0.004, 0.0052, 0.0063, 0.009, 0.02, 0.04, 0.06, 0.08, 0.03, 0.06, 0.10,
          0.15, 0.20, 0.15, 0.08, 0.04, 0.02, 0.01]
    y2 = [0, 0.001, 0.002, 0.002, 0.01, 0.02, 0.05, 0.09, 0.14, 0.20, 0.12, 0.04, 0.03, 0.06, 0.08, 0.03, 0.02,
          0.015, 0.01, 0.005, 0.003, 0.002, 0.001, 0.0005]
    sum1 = 0
    for i in y1:
        sum1 += i
    for i in y1:
        i = (i / sum1)
    sum1 = 0
    for i in y2:
        sum1 += i
    for i in y2:
        i = (i / sum1)
    y_smooth1 = make_interp_spline(x, y1)(xnew)
    y_smooth2 = make_interp_spline(x, y2)(xnew)

    fig = plt.figure(figsize=(7.5, 4.5))
    plt.title('Departure and Arrival Time Analysis', fontsize='14')
    plt.xlabel("Time", fontsize='14')
    plt.ylabel("Density", fontsize='14')
    plt.plot(xnew, y_smooth1, c="darkgoldenrod", linewidth='2', label="Arrival time")
    plt.plot(xnew, y_smooth2, color="gold", linewidth='2', label="Departure time")
    # x轴
    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "0:00"])
    plt.tick_params(labelsize=12)  # 刻度字体大小13

    plt.legend(fontsize="14")
    plt.grid(axis='y')  # 添加网格
    plt.ylim((0, 0.35))
    sns.despine()
    plt.savefig("temporal_distribution.jpg")
    plt.show()
