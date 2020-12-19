# ------------------------#
# Models used in this experiment platform
# including trading model,
# EV stopping and move distribution model,
# EV choosing charging station and charging piles model,
# EV SOC and charging model

from entities_nodes import *
from parameters import *


# EV stopping and moving model, a similar gamma distribution model is adopted
def ev_distribution(num, t):
    # how much evs will stop
    y1 = [0, 0.001, 0.002, 0.002, 0.002, 0.003, 0.003, 0.004, 0.006, 0.009, 0.02, 0.03, 0.06, 0.10, 0.03, 0.06, 0.10,
          0.15, 0.20, 0.15, 0.08, 0.04, 0.02, 0.01]
    y2 = [0, 0.001, 0.002, 0.002, 0.01, 0.02, 0.05, 0.09, 0.14, 0.20, 0.12, 0.04, 0.03, 0.06, 0.08, 0.03, 0.02,
          0.015, 0.01, 0.005, 0.003, 0.002, 0.001, 0.0005]
    sum1 = 0
    for i in range(len(y1)):
        sum1 += y1[i]
    for i in range(len(y1)):
        y1[i] = (y1[i] / sum1)
    sum1 = 0
    for i in range(len(y2)):
        sum1 += y2[i]
    for i in range(len(y2)):
        y2[i] = (y2[i] / sum1)
    num -= num * 0.05
    num1 = 0.9 * num
    stop_num_list = []
    for i in range(24):
        num1 += y1[i] * num * 0.9
        num1 -= y2[i] * num * 0.9
        stop_num_list.append(int(num1 + 0.1 * num))
    return stop_num_list[t]


# allocate EVs to  aggregators
def select_aggregator(list_v, list_a):
    result = []
    a_idle_list = []
    for i in range(len(list_a)):
        a_idle_list.append(0)
    for i in range(len(list_v)):
        sub_result = []
        sub_idle_list = []
        # find aggregator that can accommodate ev
        for i1 in range(len(list_a)):
            if a_idle_list[i1] == 0:
                sub_idle_list.append(i1)
        a_num = sub_idle_list[random.randint(0, len(sub_idle_list) - 1)]
        a_k = select_pile(list_a[a_num].pile_list)

        # when aggregator cant accommodate any ev
        if a_k == -1:
            i -= 1
            a_idle_list[a_num] = 1
            # check if all aggregator is full load
            for i2 in range(len(list_a)):
                if a_idle_list[i2] == 0:
                    break
                if i2 == len(list_v) - 1 and a_idle_list[i2] == 1:
                    return result
            continue
        sub_result.append(a_num)
        sub_result.append(a_k)
        result.append(sub_result)
    return result


# allocate EVs to  piles
def select_pile(pile_list):
    index1 = random.randint(0, 1499)
    index2 = random.randint(0, 1499)
    if pile_list[index1] == 0:
        return index1
    elif pile_list[index2] == 0:
        return index2
    idle = []
    for i in range(len(pile_list)):
        if pile_list[i] == 0:
            idle.append(i)
    if len(idle) - 1 >= 0:
        return idle[random.randint(0, len(idle) - 1)]
    else:
        return -1


# initialization before auction
def initialization(ev_num, aggregator_num):
    # initialize grid node
    grid = Grid()
    # grid.p_req = p_req
    grid.put_para(0.3, 0.7, 0, 0, 0)
    grid.f_w_req()
    aggregator_list = []
    ev_list = []
    ev_stop_num = ev_distribution(ev_num, t)

    # initialize aggregators node
    for j in range(aggregator_num):
        temp = Aggregator()
        temp.i_a = j
        temp.ch_power = 7
        temp.dc_power = 7
        temp.r_a = 0
        temp.w_low = 0.2223
        temp.w_loss = 0.002
        temp.put_para(0.3, 0.7, 0, beta1)
        temp.initial_pile_list()
        aggregator_list.append(temp)
    print(str(t) + " :complete initializing aggregator")

    # initialize EVs node
    idle_count = 0
    charging_count = 0
    for j in range(ev_stop_num):
        temp = EV()
        temp.i_v = j
        temp.soc_min = 0.6
        temp.soc_max = 0.9
        x = random.random()
        if x < 0.2:
            temp.state = 1
            temp.soc = random.randint(2, 9) / 10
            charging_count += 1
        else:
            temp.state = 0
            temp.soc = temp.soc_max
            idle_count += 1
        temp.w_loss = 0.002
        temp.b = 40
        temp.r_v = 0
        x1 = random.random()
        if x1 < 7 / 24:
            temp.w_ch = random.randint(22, 55) / 100
        elif 7 / 24 < x1 < 21 / 24:
            temp.w_ch = random.randint(55, 77) / 100
        else:
            temp.w_ch = random.randint(77, 100) / 100
        temp.beta = beta2
        ev_list.append(temp)
    print(str(t) + " :complete initializing EV, idle count= " + str(idle_count) + " ,charging count = " + str(
        charging_count))
    # bundle the EVs and charging piles of aggregators
    select_result = select_aggregator(ev_list, aggregator_list)
    0

    for j in range(ev_stop_num):
        aggregator_list[select_result[j][0]].pile_list[select_result[j][1]] = ev_list[j]
        ev_list[j].i_a = select_result[j][0]
