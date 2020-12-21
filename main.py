from models.auction import *
from data_process import *

if __name__ == '__main__':
    p_req_list = calculate_p_req()
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
    # for i in range(0, 24):
    #     temp1 = auction(p_req_list[i], i, 0.2, 0.5)
    #     load_list1.append(temp1[0])
    # for i in range(0, 24):
    #     temp1 = auction(p_req_list[i], i, 0.35, 0.5)
    #     load_list2.append(temp1[0])
    # for i in range(0, 24):
    #     temp1 = auction(p_req_list[i], i, 0.5, 0.5)
    #     load_list3.append(temp1[0])
    # for i in range(0, 24):
    #     temp1 = auction(p_req_list[i], i, 0.65, 0.5)
    #     load_list4.append(temp1[0])
    for i in range(0, 24):
        temp1 = auction(p_req_list[i], i, 0.8, 0.5)
        ev_result_list.append(temp1[1])
        load_list5.append(temp1[0])

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

    paint2(ch_sum_list, dc_sum_list)
    # paint1(load_list1, load_list2, load_list3, load_list4, load_list5)
