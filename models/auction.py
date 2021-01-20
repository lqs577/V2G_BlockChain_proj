import gc
import random

import parameters


def auction(grid, aggregator_list, ev_list, t):
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
        # there are some discharging evs from last time period
        grid.p_req -= p_dc_before
        grid.bid_list.clear()
        for k in range(len(aggregator_list)):
            aggregator_list[k].f_p_prov()
            aggregator_list[k].set_bid_price(aggregator_list[k].w_low, aggregator_list[k].w_loss, grid.w_req)
            bid_info1 = aggregator_list[k].pack_bid_info()
            # score bid_info and put it into bid_listq
            grid.score(bid_info1)
        # choose aggregator in turn
        choose_result = grid.choose()
        for k in range(len(choose_result)):
            r1 = choose_result[k][0]
            r2 = choose_result[k][1]
            # get the regulation permission
            aggregator_list[r1].reg_permission = 1
            grid.trans.append([-1, r1, 2, t + random.randint(0, 20) / 10])
            aggregator_list[r1].p_prov = r2
        # ……………………………………………………………………#

        # ……………………………………the second level auction#
        for k in range(len(aggregator_list)):
            aggregator_list[k].bid_list.clear()
            if aggregator_list[k].reg_permission == 1:
                for j in range(len(aggregator_list[k].pile_list)):
                    if aggregator_list[k].pile_list[j] != 0:
                        temp = aggregator_list[k].pile_list[j]
                        temp.f_q_prov()
                        temp.set_bid_price(aggregator_list[k].w_bid)
                        ev_bid_info = temp.pack_bid_info()
                        if ev_bid_info is not None:
                            aggregator_list[k].score(ev_bid_info)
                ev_choose_result = aggregator_list[k].choose()
                for m in range(len(ev_choose_result)):
                    # ev_list[ev_choose_result[m][0]].reg_permission = 1
                    if random.random() < 0.8:
                        aggregator_list[k].trans.append(
                            [k, ev_choose_result[m][0], 1, t + 0.5 + random.randint(0, 80) * 5 / 100])
                        ev_list[ev_choose_result[m][0]].start_discharge()
            aggregator_list[k].reg_permission = 0
    # ……………………………………………………………………#

    if grid.p_req < 0:
        p_accept_sum = 0
        for k in range(len(aggregator_list)):
            aggregator_list[k].f_p_accept(t)
            p_accept_sum += aggregator_list[k].p_accept
            grid.p_req += aggregator_list[k].f_d_q()
        for k in range(len(aggregator_list)):
            aggregator_list[k].up_regulation(abs(grid.p_req) * (aggregator_list[k].p_accept / p_accept_sum), t)

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

    ch_sum = 0
    dc_sum = 0
    for j in range(len(ev_list)):
        if ev_list[j].state == -1:
            dc_sum += 1
        if ev_list[j].state == 1:
            ch_sum += 1

    if p_dc_after > 0:
        p_result = -p_dc_after
    else:
        p_result = p_ch_after
    result_list = [p_result, ev_list, aggregator_list, grid, ch_sum, dc_sum]
    return result_list
