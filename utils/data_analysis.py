import json
from utils.data_process import *
from utils.transaction_manager import *

with open("../without_V2G_data.json", 'r') as f:
    without_V2G_data = json.load(f)
    print("complete without_V2G_data load")

with open("../original_trans_data.json", 'r') as f:
    ori_trans_data = json.load(f)
    print("complete original_trans_data load")

with open("../trans_aggregation_data.json", 'r') as f:
    trans_agg_data = json.load(f)
    print("complete trans_aggregation_data load")

with open("../duo_priority_queue_data.json", 'r') as f:
    duo_pri_data = json.load(f)
    print("complete duo_priority_queue_data load")

with open("../trans_accumulation_data.json", 'r') as f:
    trans_acc_data = json.load(f)
    print("complete trans_acc_data load")

with open("../trans_subchain_data.json", 'r') as f:
    trans_subchain_data = json.load(f)
    print("complete trans_subchain_data load")


def store_json(trans_list, filename):
    with open(filename, 'w') as file_obj:
        json.dump(trans_list, file_obj)


def get_trans_acc_data(all_trans1):
    print("------trans accumulation:")
    all_trans2 = trans_accumulation(all_trans1, 3)
    # store_json(all_trans2, "../trans_accumulation_data.json")
    print("trans number after trans accumulation" + str(len(all_trans2)))
    print("response time is:" + str(response_time(all_trans2)))
    print("---------------")
    print('     ')
    return all_trans2


def get_duo_pri_data(all_trans1):
    # --------duo priority queue
    print("------duo priority queue")
    all_trans3 = duo_prior_queue(all_trans1)
    # store_json(all_trans3, "../duo_priority_queue_data.json")
    print("trans number after duo priority queue" + str(len(all_trans3)))
    print("response time is:" + str(response_time(all_trans3)))
    print("------------------")
    print('     ')
    # ---------duo priority queue----#
    return all_trans3


def get_sub_chain_data(all_trans1):
    # --------trans sub chain
    print("------trans sub chain:")
    sub_chain_number = 3
    all_trans4 = sub_chain(all_trans1, sub_chain_number)
    for item in all_trans4:
        print(len(item))
    # store_json(all_trans4, "../trans_subchain_data.json")
    print("trans number after trans subchain" + str(len(all_trans1)))
    res_time = 0
    for trans_list in all_trans4:
        res_time += response_time(trans_list)
    print("response time is:" + str(res_time / sub_chain_number))
    print("---------------")
    print('     ')
    # ---------trans sub chain---#
    return all_trans4


def get_sub_list(trans_queue):
    trans_list = []
    flag = 12
    index = 0
    start = -1
    end = -1
    for trans in trans_queue:
        if trans[3] == flag and start == -1:
            start = index
        elif (trans[3] >= flag + 1 and end == -1) or index == len(trans_queue) - 1:
            end = index
            trans_list.append((end - start) / 60)
            start = -1
            end = -1
            flag = trans[3]
        index += 1
    result_list = trans_list[12:24] + trans_list[0:12]
    return result_list


def get_sub_list1(trans_queue):
    trans_list = []
    flag = 12
    index = 0
    start = -1
    end = -1
    sp_flag = 0
    counter = 0
    for trans in trans_queue:
        if trans[3] >= flag and start == -1:
            start = index
        elif (trans[3] >= flag + 0.5 and end == -1) or index == len(trans_queue) - 1:
            end = index
            trans_list.append((end - start) / 30)
            counter += 1
            if trans[3] >= 24 and sp_flag == 0:
                sp_flag = counter
            # print(end - start)
            start = index
            end = -1
            flag = trans[3]
        index += 1
    result_list = trans_list[sp_flag:len(trans_queue)] + trans_list[0:sp_flag]
    return result_list


def get_sub_list2(trans_queue):
    trans_list = []
    flag = 12
    index = 0
    start = -1
    end = -1
    sp_flag = 0
    counter = 0
    for trans in trans_queue:
        if trans[3] >= flag and start == -1:
            start = index
        elif (trans[3] != flag and end == -1) or index == len(trans_queue) - 1:
            end = index
            trans_list.append((end - start) / 3)
            counter += 1
            if trans[3] >= 24 and sp_flag == 0:
                sp_flag = counter
            # print(end - start)
            start = index
            end = -1
            flag = trans[3]
        index += 1
    result_list = trans_list[sp_flag:len(trans_queue)] + trans_list[0:sp_flag]
    return result_list


def paint_all(sign):
    if sign == 1:
        list1 = get_sub_list2(without_V2G_data)
        list2 = get_sub_list1(without_V2G_data)
        paint4(list1, list2, '(a) Free charging mode', '1.jpg')
    elif sign == 2:
        list1 = get_sub_list2(ori_trans_data)
        list2 = get_sub_list1(ori_trans_data)
        paint4(list1, list2, '(b) Without optimization', '2.jpg')
    elif sign == 3:
        list1 = get_sub_list2(trans_agg_data)
        list2 = get_sub_list1(trans_agg_data)
        paint4(list1, list2, '(C) Transaction aggregation', '3.jpg')
    elif sign == 4:
        list1 = get_sub_list2(duo_pri_data)
        list2 = get_sub_list1(duo_pri_data)
        paint4(list1, list2, '(d) Multi-priority transaction queues', '4.jpg')
    elif sign == 5:
        list1 = get_sub_list2(trans_acc_data)
        list2 = get_sub_list1(trans_acc_data)
        paint4(list1, list2, '(e) Transaction accumulation', '5.jpg')
    elif sign == 6:
        list1 = []
        list2 = []
        for item in trans_subchain_data:
            list1.append(get_sub_list2(item))
            list2.append(get_sub_list1(item))
        paint5(list1, list2)


if __name__ == '__main__':
    data1 = get_duo_pri_data(trans_agg_data)
    data2 = get_trans_acc_data(data1)
    data3 = get_sub_chain_data(data2)
    # paint_all(4)
    # paint_all(5)
    # paint_all(6)

    # print(len(without_V2G_data))
    # print(response_time(without_V2G_data))
