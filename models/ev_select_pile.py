from entities.entities_nodes import *


# EV select aggregator and charging pile
# a simple random model is used
# one can be replaced by a well-designed model, such as energy and time cost depended model
# and can be combined with the path planning depended model
def select_aggregator(list_a, a_idle_list):
    sub_result = []
    sub_idle_list = []
    # find aggregator that can accommodate ev
    for i in range(len(list_a)):
        for i1 in range(len(list_a)):
            if a_idle_list[i1] == 0:
                sub_idle_list.append(i1)
        a_num = sub_idle_list[random.randint(0, len(sub_idle_list) - 1)]
        a_k = select_pile(list_a[a_num].pile_list)

        # when aggregator cant accommodate any ev
        if a_k == -1:
            a_idle_list[a_num] = 1
            # check if all aggregator is full loaded
            for i2 in range(len(list_a)):
                if a_idle_list[i2] == 0:
                    break
                if i2 == len(list_a) - 1:
                    return None
            continue
        sub_result.append(a_num)
        sub_result.append(a_k)
        break
    return sub_result, a_idle_list


# allocate EVs to  piles
def select_pile(pile_list):
    index1 = random.randint(0, len(pile_list) - 1)
    index2 = random.randint(0, len(pile_list) - 1)
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
