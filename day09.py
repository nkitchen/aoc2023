#!/usr/bin/env python3

import fileinput
from pprint import pprint

import numpy as np

def main():
    data = []
    for line in fileinput.input():
        data.append([int(n) for n in line.split()])

    s = sum(predict(seq) for seq in data)
    print("Part 1:", s)

    r = sum(rpredict(seq) for seq in data)
    print("Part 2:", r)

def predict(seq):
    r = apredict(np.array(seq))
    return r

def apredict(x):
    if (x[1:] == x[:-1]).all():
        return x[-1]
    else:
        d = apredict(x[1:] - x[:-1])
        return x[-1] + d

def rpredict(seq):
    r = arpredict(np.array(seq))
    return r

def arpredict(x):
    if (x[1:] == x[:-1]).all():
        return x[0]
    else:
        d = arpredict(x[1:] - x[:-1])
        return x[0] - d

main()

# multitime -n 5 ; median:
# cpython: 0.523s
# pypy:    1.547s
