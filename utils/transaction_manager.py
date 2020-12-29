# ------------ #
# This transaction manager includes four optimization tools,
# transaction aggregation, Multi-priority transaction queues, Transaction accumulation and Transaction subchain

# aggregate transactions which issued in the EV arrive->leave period
def trans_aggregation(trans_queue):
