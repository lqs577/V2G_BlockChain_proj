import random
import math
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
import seaborn as sns


# ……………………# Initialize parameter


# ……………………#

class Grid:
    def __init__(self):
        self.p_req = 0  # power requirement
        self.w_req = 0  # requested highest bidding price of aggregator
        self.w_ch = []  # charging price
        self.w_dc = []  # discharging price
        self.p_ch = 0  # sum of charging power in grid
        self.p_dc = 0  # sum of discharging power in grid
        self.bid_list = []
        self.all_trans = []

        # ………………parameters#
        self.w1 = 0
        self.w2 = 0
        self.w3 = 0
        self.alpha = 0
        self.beta = 0
        # ……………………………#

    # bid information scoring function
    def score(self, bid_info):
        s = self.w1 * bid_info[1] + self.w2 * bid_info[2] - self.w3 * bid_info[3]
        bid_info.append(s)
        self.bid_list.append(bid_info)

    # choose aggregator in turn
    def choose(self):
        sorted(self.bid_list, key=lambda x: x[4], reverse=True)
        choosed_list = []
        i = 0
        while self.p_req > 0 and i < len(self.bid_list):
            ack_bid = []
            if self.p_req > self.bid_list[i][1]:
                ack_bid.append(self.bid_list[i][0])
                ack_bid.append(self.bid_list[i][1])
                self.p_req -= self.bid_list[i][1]
            else:
                ack_bid.append(self.bid_list[i][0])
                ack_bid.append(self.p_req)
                self.p_req = 0
            choosed_list.append(ack_bid)
            i += 1
        return choosed_list

    def f_w_req(self):
        revenue = self.alpha * (self.p_req * self.p_req) + self.beta
        self.w_req = 1.1

    def put(self, p_req, w_ch, w_dc):
        self.p_req = p_req
        self.w_ch = w_ch
        self.w_dc = w_dc

    def put_para(self, w1, w2, w3, alpha, beta):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.alpha = alpha
        self.beta = beta


class Aggregator:
    def __init__(self):
        self.i_a = 0  # aggregator number
        self.p_prov = 0  # power can provided
        self.w_ch = []  # charging price
        self.w_dc = []  # discharging price
        self.p_ch = 0  # sum of charging power
        self.p_dc = 0  # sum of discharging power
        self.pile_list = []  # 0-value means idle,i_v value means i_v is charging
        self.ch_power = 0  # charging power of pile list
        self.dc_power = 0  # discharging power of pile list
        self.reg_permission = 0  # received permission of frequency regulation from grid
        self.r_a = 0  # credit score
        self.w_bid = 0  # bidding price
        self.p_accept = 0  # power can accept
        self.bid_list = []
        self.w_low = 0
        self.w_loss = 0
        self.trans = []  # aggregator transactions queue

        # …………#parameters
        self.w1 = 0
        self.w2 = 0
        self.w3 = 0
        self.beta = 0
        # ………………

    def initial_pile_list(self):
        for i in range(1500):
            self.pile_list.append(0)

    def update_pile_list(self, ev, k):
        self.pile_list[k] = ev

    # ………………the first-level auction#
    # caculate charging power that can be increased
    def f_p_accept(self):
        for i in range(len(self.pile_list)):
            if self.pile_list[i] != 0:
                self.pile_list[i].f_q_accept()

                if self.pile_list[i].q_accept > 0:
                    self.p_accept += self.ch_power
                    self.pile_list[i].trans.append([self.pile_list[i].i_v, self.i_a])

    # regulate up the frequency
    def up_regulation(self, p):
        list1 = []
        for i in range(len(self.pile_list)):
            sublist = []
            if self.pile_list[i] != 0:
                if self.pile_list[i].q_accept > 0:
                    sublist.append(i)
                    sublist.append(self.pile_list[i].q_accept)
                    list1.append(sublist)
        sorted(list1, key=lambda x: x[1], reverse=True)
        i = 0
        while p > 0 and i < len(list1):
            self.pile_list[list1[i][0]].start_charge()
            i += 1
            p -= self.ch_power

    # caculate the power that can be provided for grid by aggregator
    def f_p_prov(self):
        for i in range(len(self.pile_list)):
            if self.pile_list[i] != 0:
                self.pile_list[i].f_q_prov()
                if self.pile_list[i].q_prov > 0:
                    self.p_prov += self.dc_power

    # set bidding price
    def set_bid_price(self, w_low, w_loss, w_req):
        if w_req > w_low + w_loss:
            self.w_bid = self.beta * (w_req - w_low - w_loss) + w_low + w_loss
        else:
            self.w_bid = 0

    # pack the bidding information
    def pack_bid_info(self):
        if self.w_bid != 0 and self.p_prov > 0:
            bid_info = []
            bid_info.append(self.i_a)
            bid_info.append(self.p_prov)
            bid_info.append(self.r_a)
            bid_info.append(self.w_bid)
            return bid_info
        else:
            return None

    # ………………………………………………#

    # ………………the second-level auction#
    # score bidding information from EVs
    def score(self, bid_info):
        s = self.w1 * bid_info[1] + self.w2 * bid_info[2] - self.w3 * bid_info[3]
        bid_info.append(s)
        self.bid_list.append(bid_info)

    # choose EV that participating in FM in turn
    def choose(self):
        sorted(self.bid_list, key=lambda x: x[4], reverse=True)
        choosed_list = []
        i = 0
        while self.p_prov > 0 and i < len(self.bid_list):
            ack_bid = []
            if self.p_prov > 0:
                ack_bid.append(self.bid_list[i][0])
                self.p_prov -= self.dc_power
            choosed_list.append(ack_bid)
            i += 1
        return choosed_list

    # ………………the second-level auction#

    # caculate the sum of charging power and discharging power
    def p_sum(self):
        self.p_ch = 0
        self.p_dc = 0
        for i in range(len(self.pile_list)):
            if self.pile_list[i] != 0:
                if self.pile_list[i].state == -1:
                    self.p_dc += self.dc_power
                elif self.pile_list[i].state == 1:
                    self.p_ch += self.ch_power

    def initialize(self):
        self.f_p_prov()
        self.f_p_accept()

    def put(self, i_a, w_ch, w_dc, r_a):
        self.i_a = i_a
        self.w_ch = w_ch
        self.w_dc = w_dc
        self.r_a = r_a

    def put_para(self, w1, w2, w3, beta):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.beta = beta


class EV:
    def __init__(self):
        self.i_v = 0
        self.i_a = 0  # the aggregator number
        self.i_a_p = 0  # the charging pile number
        self.soc = 0
        self.soc_min = 0
        self.soc_max = 0
        self.b = 0
        self.w_loss = 0
        self.r_v = 0
        self.state = 0  # -1 value->discharging, 0 value->idle, 1-value->charging, -2 ->not in charging station
        self.w_ch = 0  # charging price(last past 30 min)
        self.q_prov = 0
        self.w_bid = 0
        self.w_r = 0  # expected revenue in frequency regulation
        self.reg_permission = 0
        self.q_accept = 0  # electricity amount can accept
        self.trans = []  # EV transactions

        # ………………parameter#
        self.beta = 0
        # …………………………#

    def f_q_accept(self):
        if self.state == 0 and self.soc < 1:
            self.q_accept = (1 - self.soc) * self.b
        else:
            self.q_accept = 0

    # ……………………………………the second level auction#
    def f_q_prov(self):
        if self.state == 0 and self.soc > self.soc_min:
            self.q_prov = (self.soc - self.soc_min) * self.b
        else:
            self.q_prov = 0

    def set_bid_price(self, w_req):
        if w_req > self.w_ch + self.w_loss:
            self.w_bid = self.beta * (w_req - (self.w_ch + self.w_loss)) + (self.w_ch + self.w_loss)
        else:
            self.w_bid = 0

    def pack_bid_info(self):
        if self.q_prov > 0 and self.w_bid != 0:
            bid_info = []
            bid_info.append(self.i_v)
            bid_info.append(self.q_prov)
            bid_info.append(self.r_v)
            bid_info.append(self.w_bid)
            return bid_info
        else:
            return None

    # …………………………………………………………#

    # change ev state #
    def start_discharge(self):
        self.state = -1

    def start_charge(self):
        self.state = 1

    def start_idle(self):
        self.state = 0

    def run(self):
        self.state = -2

    # -- change ev state --#

    def initialize(self):
        self.f_q_prov()
        self.f_q_accept()

    def put(self, i_v, i_a, soc_min, soc_max, b, w_loss, r_v, soc, state, w_ch, w_r):
        self.i_v = i_v
        self.i_a = i_a
        self.soc = soc
        self.soc_min = soc_min
        self.soc_max = soc_max
        self.b = b
        self.w_loss = w_loss
        self.r_v = r_v
        self.state = state
        self.w_ch = w_ch
        self.w_r = w_r


if __name__ == '__main__':
    # stopping ev numbers
    y11 = [0, 0.001, 0.002, 0.002, 0.002, 0.003, 0.003, 0.004, 0.006, 0.009, 0.02, 0.03, 0.06, 0.10, 0.03, 0.06, 0.10,
           0.15, 0.20, 0.15, 0.08, 0.04, 0.02, 0.01]
    y22 = [0, 0.001, 0.002, 0.002, 0.01, 0.02, 0.05, 0.09, 0.14, 0.20, 0.12, 0.04, 0.03, 0.06, 0.08, 0.03, 0.02,
           0.015, 0.01, 0.005, 0.003, 0.002, 0.001, 0.0005]
    sum11 = 0
    for i1 in range(len(y11)):
        sum11 += y11[i1]
    for i1 in range(len(y11)):
        y11[i1] = (y11[i1] / sum11)
    sum11 = 0
    for i1 in range(len(y22)):
        sum11 += y22[i1]
    for i1 in range(len(y22)):
        y22[i1] = (y22[i1] / sum11)

    num = 360000
    num -= num * 0.05
    num1 = 0.9 * num
    stop_num_list = []
    for i1 in range(24):
        num1 += y11[i1] * num * 0.9
        num1 -= y22[i1] * num * 0.9
        stop_num_list.append(num1 + 0.1 * num)
    # ………………
    x = np.arange(0, 24, 1)
    xnew = np.linspace(x.min(), x.max(), 300)
    y_smooth1 = make_interp_spline(x, stop_num_list)(xnew)

    fig = plt.figure(figsize=(8, 4.5))
    plt.title('Analysis of Parking EV Numbers  ', fontsize='14')
    plt.xlabel("Time", fontsize='14')
    plt.ylabel("EV numbers", fontsize='14')
    plt.plot(xnew, y_smooth1, c="darkgoldenrod", linewidth='2')
    # x轴
    plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24], ["0:00", "", "6:00", "", "12:00", "", "18:00", "", "0:00"])
    plt.tick_params(labelsize=12)  # 刻度字体大小13

    # plt.legend(fontsize="10")
    plt.grid(axis='y')  # 添加网格
    sns.despine()
    plt.savefig("EV_numbers.jpg")
    plt.show()
