import numpy as np


def to_tups(a):
    return [tuple(x) for x in a]


def to_np(ts):
    return np.array(ts)
