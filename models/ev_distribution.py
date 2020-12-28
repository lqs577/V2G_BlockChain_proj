from parameters import *

# arrive prob
y1 = [0.04, 0.02, 0.02, 0.02, 0.02, 0.02, 0.04, 0.06, 0.04, 0.04, 0.04, 0.05, 0.05, 0.10, 0.05, 0.06, 0.10,
      0.15, 0.20, 0.15, 0.10, 0.08, 0.06, 0.04]
# departure prob
y2 = [0.01, 0.01, 0.02, 0.02, 0.02, 0.03, 0.09, 0.14, 0.20, 0.12, 0.08, 0.04, 0.03, 0.08, 0.10, 0.12, 0.08,
      0.04, 0.03, 0.02, 0.02, 0.02, 0.01, 0.01]


def normalization(y1, y2):
    sum1 = 0
    for i in range(len(y1)):
        sum1 += y1[i]
    for i in range(len(y1)):
        y1[i] = (y1[i] / sum1)
    sum1 = 0
    for i in range(len(y2)):
        sum1 += y2[i]
    for i in range(len(y2)):
        y2[i] = (y2[i] / sum1)
    return y1, y2


# EV stopping and moving model, a similar gamma distribution model is adopted
def ev_distribution(t):
    # how much evs will stop
    num = ev_num
    num -= num * 0.05
    num1 = 0.9 * num
    stop_num_list = []
    for i in range(24):
        num1 += y1[i] * num * 0.9
        num1 -= y2[i] * num * 0.9
        stop_num_list.append(int(num1 + 0.1 * num))
    return stop_num_list[t]
