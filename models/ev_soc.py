# describe evs soc state and changes

import random
from models.ev_distribution import *
import math
import numpy as np

random_pool = [0.0]


# initial ev soc state
# ev full charge in five hours
def initial_soc():
    if random.random() < y1[23]:
        soc = random.randint(1, 9) / 10
    elif random.random() < y1[22]:
        soc = random.randint(3, 9) / 10
    elif random.random() < y1[21]:
        soc = random.randint(5, 9) / 10
    elif random.random() < y1[20]:
        soc = random.randint(7, 9) / 10
    else:
        soc = 0.9
    return soc


# normal distribution
def normal_distribution(t):
    # map (0.1,0.9) to (-3,3)
    t = ((t * 10) - 5) * 0.75
    miu = 0
    sigma = 1
    y = (1 / (sigma * math.sqrt(2 * math.pi))) * np.exp(-((t - miu) ** 2 / 2 * sigma ** 2))
    return y
    # mu, sigma = 0.5, 1
    # sampleNo = 1000
    # np.random.seed(0)
    # s = np.random.normal(mu, sigma, sampleNo)


def initial_soc_pool():
    for i in range(1, 10):
        soc1 = normal_distribution(i / 10)
        for j in range(1, int(soc1 * 1000)):
            random_pool.append(i / 10)
    random_pool[0] = len(random_pool)


# ev soc state when arrive
def arr_soc():
    index = random.randint(1, int(random_pool[0]) - 1)
    return random_pool[index]


# ev soc changes in minutes
# each minutes charge 0.003 soc
def soc_change(ev, t, fr_flag, t1):
    if ev.state == 0:
        ev.soc = ev.soc
    elif ev.state == 1:
        # ev.soc += 0.003 * t
        ev.soc += (random.randint(2, 4) / 1000) * t
        if ev.soc >= 0.9 and fr_flag == 0:
            ev.soc = 0.9
            ev.state = 0
            ev.trans.append([ev.i_v, ev.i_a, 0, t1])
        elif ev.soc >= 1.0:
            ev.soc = 1.0
            ev.state = 0
            # if fr_flag != 1:
            #     ev.trans.append([ev.i_v, ev.i_a, 0, t1])
            if fr_flag == 1:
                fr_flag = 0
    elif ev.state == -1:
        ev.soc -= (random.randint(2, 4) / 1000) * t
        if ev.soc <= 0.6:
            ev.soc = 0.6
            ev.state = 0

    return ev.soc, ev.state, fr_flag


if __name__ == '__main__':
    initial_soc_pool()
    for i in range(1, 100):
        print(arr_soc())
