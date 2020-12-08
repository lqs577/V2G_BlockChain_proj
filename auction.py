import numpy as np
from entities_nodes import *
import gc

# ——————————————  parameters#
aggregator_num = 180
ev_num = 360000


# ————————————————————#

def initialization():
    # initialize grid node
    grid = Grid()
    grid.p_req = p_req
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


def auction(grid, aggregator_list, ev_list, p_req, t, beta1, beta2):
    # caculate ch and dc power before auction
    grid.p_ch = 0
    grid.p_dc = 0
    for j in range(len(aggregator_list)):
        aggregator_list[j].p_sum()
        grid.p_ch += aggregator_list[j].p_ch
        grid.p_dc += aggregator_list[j].p_dc
    p_ch_before = grid.p_ch
    p_dc_before = grid.p_dc
    print(str(t) + " :before auction: charging power=" + str(p_ch_before) + ",discharging power=" + str(p_dc_before))

    # ………………………………………the first-level auction#
    grid.f_w_req()
    if grid.p_req > 0:
        for k in range(len(aggregator_list)):
            aggregator_list[k].f_p_prov()
            aggregator_list[k].set_bid_price(aggregator_list[k].w_low, aggregator_list[k].w_loss, grid.w_req)
            bid_info1 = aggregator_list[k].pack_bid_info()
            # score bid_info and put it into bid_list
            grid.score(bid_info1)
        # choose aggregator in turn
        choose_result = grid.choose()
        for k in range(len(choose_result)):
            r1 = choose_result[k][0]
            r2 = choose_result[k][1]
            # get the regulation permission
            aggregator_list[r1].reg_permission = 1
            aggregator_list[r1].p_prov = r2
        # ……………………………………………………………………#

        # ……………………………………the second level auction#
        for k in range(len(aggregator_list)):
            if aggregator_list[k].reg_permission == 1:
                for j in range(len(aggregator_list[k].pile_list)):
                    if aggregator_list[k].pile_list[j] != 0:
                        temp = aggregator_list[k].pile_list[j]
                        temp.f_q_prov()
                        temp.set_bid_price(aggregator_list[k].w_bid)
                        ev_bid_info = temp.pack_bid_info()
                        if ev_bid_info != None:
                            aggregator_list[k].score(ev_bid_info)
                ev_choose_result = aggregator_list[k].choose()
                for m in range(len(ev_choose_result)):
                    ev_list[ev_choose_result[m][0]].reg_permission = 1
                    ev_list[ev_choose_result[m][0]].start_discharge()
            aggregator_list[k].reg_permission = 0
    # ……………………………………………………………………#

    if grid.p_req < 0:
        p_accept_sum = 0
        for k in range(len(aggregator_list)):
            aggregator_list[k].f_p_accept()
            p_accept_sum += aggregator_list[k].p_accept
        for k in range(len(aggregator_list)):
            aggregator_list[k].up_regulation(abs(grid.p_req) * (aggregator_list[k].p_accept / p_accept_sum))

    # caculate ch and dc power after auction
    grid.p_ch = 0
    grid.p_dc = 0
    for j in range(len(aggregator_list)):
        aggregator_list[j].p_sum()
        grid.p_ch += aggregator_list[j].p_ch
        grid.p_dc += aggregator_list[j].p_dc
    p_ch_after = grid.p_ch
    p_dc_after = grid.p_dc
    print(str(t) + " :after auction: charging power=" + str(p_ch_after) + ",discharging power=" + str(p_dc_after))

    result_list = []
    result_list.append(p_ch_after - p_dc_after - p_ch_before)
    result_list.append(ev_list)
    result_list.append(aggregator_list)
    result_list.append(grid)
    del ev_list, aggregator_list
    gc.collect()
    return result_list
