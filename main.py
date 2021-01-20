import json
from operator import itemgetter

from models.power_requirenment import calculate_p_req
from utils.data_process import *
from models.ev_distribution import *
from models.ev_select_pile import *
from models.auction import *
from models.ev_soc import *
from parameters import *
from utils.transaction_manager import *


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
                ev_list[j].arr_time = 0
                # add transaction application
                # if random.random() < y1[0]:
                #     ev_list[j].trans.append([j, select_result[0], 0, 0])
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


def get_sub_list(trans_queue):
    trans_list = []
    flag = 12
    index = 0
    start = -1
    end = -1
    for trans in trans_queue:
        if trans[3] == flag and start == -1:
            start = index
        elif (trans[3] == flag + 1 and end == -1) or index == len(trans_queue) - 1:
            end = index
            trans_list.append([start, end])
            start = -1
            end = -1
            flag += 1
        index += 1
    return trans_list


def store_json(trans_list, filename):
    with open(filename, 'w') as file_obj:
        json.dump(trans_list, file_obj)


if __name__ == '__main__':
    # initialize entities nodes
    grid, aggregator_list, ev_list, a_idle_list = initialization()
    y1, y2 = normalization(y1, y2)
    p_req_list = calculate_p_req()
    p_req_list += p_req_list
    p_result1 = []
    p_result2 = []
    p_result3 = []
    p_result4 = []
    p_result5 = []
    ev_result_list = []
    load_list = []
    ch_sum_list = []
    dc_sum_list = []

    y1 += y1
    y2 += y2

    for i in range(0, 48):

        grid.p_req = p_req_list[i]
        for ev in ev_list:
            if grid.p_req < 0:
                if ev.state == -1:
                    ev.state = 0
            else:
                if ev.soc >= 0.9 and ev.state == 1:
                    ev.d_fr_flag = 0
                    ev.state = 0

        ch_sum = 0
        for j in range(len(ev_list)):
            if ev_list[j].state == 1:
                ch_sum += 1

        temp1 = auction(grid, aggregator_list, ev_list, i)

        ch_sum_list.append(temp1[4] * 7)
        dc_sum_list.append(temp1[5] * 7)

        ev_list = temp1[1]
        aggregator_list = temp1[2]
        grid = temp1[3]
        load_list.append(temp1[0])
        # for each there minutes update system states
        depart_prob = y2[i] / 20
        arr_prob = y1[i] / 20

        # change ev attributes in each 3 min depend on the models
        for j in range(0, 20):
            # print('t= ' + str(i + 3 * j / 60))
            if j % 3 == 0:
                for aggregator in aggregator_list:
                    aggregator.trans.append([aggregator.i_a, -1, 2, i + 3 * j / 60])
            for ev in ev_list:
                if ev.state != -2:
                    ev.soc, ev.state, ev.d_fr_flag = soc_change(ev, 3, ev.d_fr_flag, i + 3 * j / 60)
                    # if this ev leave charging station
                    if random.random() < depart_prob:
                        ev.leave_time = i + 3 * j / 60
                        # t_period = [ev.arr_time, ev.leave_time, ev.i_a]
                        # ev.time_period.append(t_period)
                        # ev.arr_time = -1
                        # ev.leave_time = -1

                        if ev.arr_time < 11:
                            if 12 <= ev.leave_time <= 35:
                                ev.arr_time = 12
                                t_period = [ev.arr_time, ev.leave_time, ev.i_a]
                                ev.time_period.append(t_period)
                                ev.arr_time = -1
                                ev.leave_time = -1
                            elif ev.leave_time > 35:
                                ev.arr_time = 12
                                ev.leave_time = 35
                                t_period = [ev.arr_time, ev.leave_time, ev.i_a]
                                # ev.time_period.append(t_period)
                                ev.arr_time = -1
                                ev.leave_time = -1
                        elif 12 <= ev.arr_time <= 35:
                            if 12 <= ev.leave_time <= 35:
                                t_period = [ev.arr_time, ev.leave_time, ev.i_a]
                                ev.time_period.append(t_period)
                                ev.arr_time = -1
                                ev.leave_time = -1
                            elif ev.leave_time > 35:
                                ev.leave_time = 35
                                t_period = [ev.arr_time, ev.leave_time, ev.i_a]
                                # ev.time_period.append(t_period)
                                ev.arr_time = -1
                                ev.leave_time = -1
                        elif ev.arr_time > 35:
                            ev.arr_time = -1
                            ev.leave_time = -1

                        if ev.state == 1:
                            ev.trans.append([ev.i_v, ev.i_a, 0, i + 3 * j / 60])
                        elif ev.state == -1:
                            ev.trans.append([ev.i_a, ev.i_v, 1, i + 3 * j / 60])
                        a_idle_list[ev.i_a] = 0
                        aggregator_list[ev.i_a].pile_list[ev.i_a_p] = 0
                        ev.i_a_p = -1
                        ev.i_a = -1
                        ev.state = -2
                    # elif j == 19 and i == 47:
                    #     ev.leave_time = i + 3 * j / 60
                    #     t_period = [ev.arr_time, ev.leave_time, ev.i_a]
                    #     ev.time_period.append(t_period)
                    #     ev.arr_time = -1
                    #     ev.leave_time = -1

                else:
                    if random.random() < arr_prob:
                        select_result, a_idle_list = select_aggregator(aggregator_list, a_idle_list)
                        # if is there idle charging piles
                        if select_result is not None:
                            aggregator_list[select_result[0]].pile_list[select_result[1]] = ev
                            ev.i_a = select_result[0]
                            ev.i_a_p = select_result[1]
                            # add transaction application
                            # ev.trans.append([ev.i_v, select_result[0], 0, i + 3 * j / 60])
                            # set stopping states
                            ev.soc = arr_soc()
                            ev.start_charge()
                            ev.arr_time = i + 3 * j / 60

                        else:
                            ev_list[j].i_a = -1
                            ev_list[j].i_a_p = -1
                            ev_list[j].run()
        # ch_sum_list.append(ch_sum*7)

    # ---------original trans data
    print("------original trans data:")
    all_trans1 = []
    for ev in ev_list:
        all_trans1 += ev.trans
    for aggregator in aggregator_list:
        all_trans1 += aggregator.trans
    all_trans1 += grid.trans
    all_trans1 = sorted(all_trans1, key=itemgetter(3))
    start_flag = 0
    end_flag = 0
    for i in range(len(all_trans1)):
        if all_trans1[i][3] >= 12 and start_flag == 0:
            start_flag = i
        if all_trans1[i][3] >= 36 and end_flag == 0:
            end_flag = i
            break
    all_trans1 = all_trans1[start_flag:end_flag]
    store_json(all_trans1, "original_trans_data.json")
    print("original trans number:" + str(len(all_trans1)))
    print("response time is:" + str(response_time(all_trans1)))
    print("---------------")
    print('     ')
    # ------original trans data---#

    # --------trans aggregation
    print("------trans aggregation:")
    all_trans = []
    trans_aggregation(ev_list, aggregator_list)
    for ev in ev_list:
        all_trans += ev.trans
    for aggregator in aggregator_list:
        all_trans += aggregator.trans
    all_trans += grid.trans
    all_trans = sorted(all_trans, key=itemgetter(3))
    start_flag = 0
    end_flag = 0
    for i in range(len(all_trans)):
        if all_trans[i][3] == 12 and start_flag == 0:
            start_flag = i
        if all_trans[i][3] == 36 and end_flag == 0:
            end_flag = i
            break
    all_trans = all_trans[start_flag:end_flag]
    store_json(all_trans, "trans_aggregation_data.json")
    print("trans number after trans aggregation:" + str(len(all_trans)))
    print("response time is:" + str(response_time(all_trans)))
    print("---------------")
    print('     ')
    # ---------trans aggregation---#

    # # --------duo priority queue
    # print("------duo priority queue")
    # all_trans3 = duo_prior_queue(all_trans1)
    # store_json(all_trans3, "duo_priority_queue_data.json")
    # print("trans number after duo priority queue" + str(len(all_trans3)))
    # print("response time is:" + str(response_time(all_trans3)))
    # print("------------------")
    # print('     ')
    # # ---------duo priority queue----#

    # # --------trans accumulation
    # print("------trans accumulation:")
    # with open("../original_trans_data.json", 'r') as f:
    #     all_trans1 = json.load(f)
    #     print("complete original_trans_data load")
    # all_trans2 = trans_accumulation(all_trans1, 1)
    # store_json(all_trans2, "trans_accumulation_data.json")
    # print("trans number after trans accumulation" + str(len(all_trans2)))
    # print("response time is:" + str(response_time(all_trans2)))
    # print("---------------")
    # print('     ')
    # # ---------trans accumulation---#

    # # --------trans sub chain
    # print("------trans sub chain:")
    # sub_chain_number = 4
    # all_trans4 = sub_chain(all_trans1, sub_chain_number)
    # store_json(all_trans4, "trans_subchain_data.json")
    # print("trans number after trans subchain" + str(len(all_trans1)))
    # res_time = 0
    # for trans_list in all_trans4:
    #     res_time += response_time(trans_list)
    # print("response time is:" + str(res_time / sub_chain_number))
    # print("---------------")
    # print('     ')
    # # ---------trans sub chain---#

    # with open("ch_dc_numbers.json", 'r') as f:
    #     paint_list = json.load(f)
    # # paint_list1 = ch_sum_list[24:36] + ch_sum_list[12:24]
    # # paint_list2 = dc_sum_list[24:36] + dc_sum_list[12:24]
    # paint_list3 = ch_sum_list[24:36] + ch_sum_list[12:24]
    # store_json(paint_list3, "free_ch_sum.json")
    # paint2(paint_list[0:24], paint_list[24:48], paint_list3)
    # paint1(load_list[12:36])
    # print(load_list[12:36])
