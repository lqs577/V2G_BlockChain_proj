# ------------ #
# This transaction manager includes four optimization tools,
# transaction aggregation, Multi-priority transaction queues, Transaction accumulation and Transaction subchain

from queue import Queue


# aggregate transactions which issued in the EV arrive->leave period
def trans_aggregation(ev_list, aggregator_list):
    for ev in ev_list:
        for time in ev.time_period:
            temp = []
            e_count = 0
            a_count = 0

            del_list_e = []
            del_list_a = []
            i = 0
            for trans in ev.trans:
                if time[0] <= trans[3] <= time[1]:
                    temp.append(trans)
                    e_count += 1
                    del_list_e.append(i)
                i += 1
            i = 0
            for trans in aggregator_list[time[2]].trans:
                if time[0] <= trans[3] <= time[1] and trans[1] == ev.i_v:
                    temp.append(trans)
                    a_count += 1
                    del_list_a.append(i)
                i += 1

            if e_count > a_count:
                trans = [ev.i_v, time[2], 0, time[1]]
                ev.trans.insert(del_list_e[len(del_list_e) - 1] + 1, trans)
            elif e_count < a_count:
                trans = [time[2], ev.i_v, 1, time[1]]
                aggregator_list[time[2]].trans.insert(del_list_a[len(del_list_e) - 1] + 1, trans)
            for item in reversed(del_list_e):
                del ev.trans[item]
            for item in reversed(del_list_a):
                del aggregator_list[time[2]].trans[item]


def duo_prior_queue(trans_queue):
    q1 = []
    q2 = []
    for trans in trans_queue:
        if trans[2] == 0 or trans[2] == 1:
            q1.append(trans)
        else:
            q2.append(trans)

    time_cost = 0.1
    waiting_time = 0
    time_counter = 43200
    trans_counter = 0
    trans_counter1 = 0
    result_list = []

    flag1 = 0
    flag2 = 0
    while 1:
        temp_t = time_counter / 3600
        if q1[trans_counter][3] <= temp_t and flag1 == 0:
            time_counter += time_cost
            start_time = q1[trans_counter][3] * 3600
            waiting_time += time_counter - start_time
            trans_counter += 1
            result_list.append(q1[trans_counter])
        elif q2[trans_counter1][3] <= temp_t and flag2 == 0:
            time_counter += time_cost
            start_time = q1[trans_counter1][3] * 3600
            waiting_time += time_counter - start_time
            trans_counter1 += 1
            result_list.append(q2[trans_counter1])
        else:
            time_counter += time_cost
        if trans_counter == len(q1):
            flag1 = 1
        if trans_counter1 == len(q2):
            flag2 = 1
        if flag1 == 1 and flag2 == 1:
            break
    return result_list


def trans_accumulation(trans_queue, option):
    if option == 1:
        # --method 1
        curr = 0
        del_list = []
        for trans in trans_queue:
            if trans[0] != -2:
                for i in range(curr + 1, curr + 6000):
                    if i < len(trans_queue):
                        if identify_func(trans, trans_queue[i]):
                            del_list.append(i)
                            trans_queue[i][0] = -2
                            trans_queue[i][1] = -2
                    else:
                        break
            curr += 1
        del_list.sort(reverse=True)
        for index in del_list:
            trans_queue.pop(index)
        return trans_queue

    if option == 2:
        # --method 2
        trans_list = []
        flag = 12
        index = 0
        start_flag = -1
        end_flag = -1
        for trans in trans_queue:
            if trans[3] == flag and start_flag == -1:
                start_flag = index
            elif (trans[3] == flag + 1 and end_flag == -1) or index == len(trans_queue) - 1:
                end_flag = index
                trans_list.append([start_flag, end_flag])
                start_flag = -1
                end_flag = -1
                flag += 1
            index += 1
        print(trans_list)

        del_list = []
        for item in trans_list:
            curr = 0
            for trans in trans_queue[item[0]:item[1]]:
                print(curr)
                if trans[0] != -2:
                    for i in range(curr + 1, item[1]):
                        if identify_func(trans, trans_queue[i]):
                            del_list.append(i)
                            trans_queue[i][0] = -2
                            trans_queue[i][1] = -2
                curr += 1
        del_list.sort(reverse=True)
        for index1 in reversed(del_list):
            trans_queue.pop(index1)
        return trans_queue

    if option == 3:
        # --method 3
        time_cost = 0.1
        time_counter = 43200
        trans_counter = 0
        waiting_queue = []
        result_queue = []

        while 1:
            temp_t = time_counter / 3600
            for i in range(trans_counter, len(trans_queue)):
                if trans_queue[i][3] <= temp_t:
                    trans_counter += 1
                    print(trans_counter)
                    flag = 0
                    for item in waiting_queue:
                        if identify_func(item, trans_queue[i]):
                            flag = 1
                            break
                    if flag == 0:
                        waiting_queue.append(trans_queue[i])
                else:
                    break
            if len(waiting_queue) != 0:
                result_queue.append(waiting_queue.pop(0))
                # pop_index = []
                # for j in range(1, len(waiting_queue)):
                #     if identify_func(waiting_queue[0], waiting_queue[j]):
                #         pop_index.append(j)
                # for j in reversed(pop_index):
                #     waiting_queue.pop(j)
                time_counter += time_cost
            else:
                time_counter += time_cost
            if trans_counter >= len(trans_queue):
                break
        return result_queue


def identify_func(trans1, trans2):
    if trans1[0] == trans2[0] and trans1[1] == trans2[1]:
        return 1
    elif trans1[0] == trans2[1] and trans1[1] == trans2[0]:
        return 1
    return 0


def response_time(trans_queue):
    time_cost = 0.1
    waiting_time = 0
    time_counter = 43200
    trans_counter = 0
    while 1:
        temp_t = time_counter / 3600
        if trans_queue[trans_counter][3] <= temp_t:
            time_counter += time_cost
            start_time = trans_queue[trans_counter][3] * 3600
            waiting_time += time_counter - start_time
            trans_counter += 1
        else:
            time_counter += time_cost
        if trans_counter == len(trans_queue):
            break
    return waiting_time / len(trans_queue)
