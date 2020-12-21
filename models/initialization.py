from entities.entities_nodes import *
from models.ev_distribution import *
from models.ev_select_pile import *


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

    for j in range(ev_stop_num):
        aggregator_list[select_result[j][0]].pile_list[select_result[j][1]] = ev_list[j]
        ev_list[j].i_a = select_result[j][0]
