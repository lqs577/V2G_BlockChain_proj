from operator import itemgetter

from models.power_requirenment import calculate_p_req
from utils.data_process import *
from models.ev_distribution import *
from models.ev_select_pile import *
from models.auction import *
from models.ev_soc import *
from parameters import *


def initialization():
    # initialize grid node
    grid = Grid()
    # grid.p_req = p_req
    grid.put_para(0.3, 0.7, 0, 0, 0)
    grid.f_w_req()
    aggregator_list = []
    ev_list = []

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
    print("complete initializing aggregator")

    # initialize EVs node
    ev_stop_num = ev_distribution(0)
    a_idle_list = []
    for m in range(len(aggregator_list)):
        a_idle_list.append(0)
    for j in range(ev_num):
        temp = EV()
        temp.i_v = j
        temp.soc_min = 0.6
        temp.soc_max = 0.9
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

        # bundle the EVs and charging piles of aggregators

        # if EV is in stopping state
        if random.random() < ev_stop_num / ev_num:
            select_result, a_idle_list = select_aggregator(aggregator_list, a_idle_list)
            # if is there idle charging piles
            if select_result is not None:
                aggregator_list[select_result[0]].pile_list[select_result[1]] = ev_list[j]
                ev_list[j].i_a = select_result[0]
                ev_list[j].i_a_p = select_result[1]
                # add transaction application
                if random.random() < y1[0]:
                    ev_list[j].trans.append([j, select_result[0], 0, random.randint(0, 47)])
                # grid.all_trans.append([j, select_result[0]])
                # set stopping states
                ev_list[j].soc = initial_soc()
                if ev_list[j].soc == 0.9:
                    ev_list[j].state = 0
                else:
                    ev_list[j].state = 1
            else:
                ev_list[j].i_a = -1
                ev_list[j].i_a_p = -1
                ev_list[j].run()
        else:
            ev_list[j].i_a = -1
            ev_list[j].i_a_p = -1
            ev_list[j].run()

    # initial random soc pool
    initial_soc_pool()

    print("complete initializing EV")

    return grid, aggregator_list, ev_list, a_idle_list


if __name__ == '__main__':
    # initialize entities nodes
    grid, aggregator_list, ev_list, a_idle_list = initialization()

    p_req_list = calculate_p_req()
    # p_req_list += p_req_list
    p_result1 = []
    p_result2 = []
    p_result3 = []
    p_result4 = []
    p_result5 = []
    load_list1 = []
    load_list2 = []
    load_list3 = []
    load_list4 = []
    load_list5 = []
    ev_result_list = []
    # y1 += y1
    # y2 += y2

    for i in range(0, 24):
        grid.p_req = p_req_list[i]
        temp1 = auction(grid, aggregator_list, ev_list, i)
        ev_result_list.append(temp1[1])
        ev_list = temp1[1]
        aggregator_list = temp1[2]
        grid = temp1[3]
        load_list5.append(temp1[0])
        # for each there minutes update system states
        depart_prob = y2[i] / 20
        arr_prob = y1[i] / 20

        # change ev attributes in each 3 min depend on the models
        for j in range(0, 20):
            print('t= ' + str(i + 3 * j / 60))
            for ev in ev_list:
                if ev.state != -2:
                    ev.soc, ev.state = soc_change(ev.soc, ev.state, 3, ev.d_fr_flag)
                    # if this ev leave charging station
                    if random.random() < depart_prob:
                        a_idle_list[ev.i_a] = 0
                        aggregator_list[ev.i_a].pile_list[ev.i_a_p] = 0
                        ev.i_a_p = -1
                        ev.i_a = -1
                        # grid.all_trans += ev.trans
                else:
                    if random.random() < arr_prob:
                        select_result, a_idle_list = select_aggregator(aggregator_list, a_idle_list)
                        # if is there idle charging piles
                        if select_result is not None:
                            aggregator_list[select_result[0]].pile_list[select_result[1]] = ev
                            ev.i_a = select_result[0]
                            ev.i_a_p = select_result[1]
                            # add transaction application
                            ev.trans.append([ev.i_v, select_result[0], 0, i + 3 * j / 60])
                            # set stopping states
                            ev.soc = arr_soc()
                            ev.start_charge()

                        else:
                            ev_list[j].i_a = -1
                            ev_list[j].i_a_p = -1
                            ev_list[j].run()
        for ev in ev_list:
            ev.d_fr_flag = 0

    ch_sum_list = []
    dc_sum_list = []
    for i in range(24):
        ch_sum = 0
        dc_sum = 0
        for item in ev_result_list[i]:
            if item.state == 1:
                ch_sum += 1
            elif item.state == -1:
                dc_sum += 1
        ch_sum_list.append(ch_sum * 7)
        dc_sum_list.append(dc_sum * 7)

    all_trans = []
    for ev in ev_list:
        all_trans += ev.trans
    for aggregator in aggregator_list:
        all_trans += aggregator.trans
    all_trans += grid.trans
    all_trans = sorted(all_trans, key=itemgetter(3))
    count = []
    for i in range(48):
        count.append(0)
    for item in all_trans:
        count[int(item[3])] += 1
    print(count[11:35])
    print(len(all_trans))
    # paint2(ch_sum_list, dc_sum_list)
    # paint1(load_list1, load_list2, load_list3, load_list4, load_list5)
