from entities.entities_nodes import *


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
