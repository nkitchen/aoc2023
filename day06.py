#!/usr/bin/env python3

import fileinput
import math
import re
from pprint import pprint

# t_c: time to charge
# T: total race time
# R: record distance to beat
#
# t_c * (T - t_c) > R
#
# -t_c^2 + T*t_c - R > 0
# t_c^2 - T*t_c + R > 0
#
# (T +/- sqrt(T^2 - 4*R)) / 2
#
# t_c in (ceil( (T - sqrt(T^2 - 4*R))/2),
#         floor((T + sqrt(T^2 - 4*R))/2)) (exclusive)

def main():
    for line in fileinput.input():
        if not line:
            continue
        i = line.index(":")
        values = [int(x) for x in line[i+1:].split()]
        if line[:i] == "Time":
            times = values
        if line[:i] == "Distance":
            records = values

    print("Part 1:", win_ways(times, records))

    jtime = int("".join(str(T) for T in times))
    jrecord = int("".join(str(R) for R in records))

    print("Part 2:", win_ways([jtime], [jrecord]))

def win_ways(times, records):
    ways = []
    for T, R in zip(times, records):
        disc = T ** 2 - 4 * R
        a = math.floor((T - math.sqrt(disc)) / 2) + 1
        b = math.ceil((T + math.sqrt(disc)) / 2) - 1
        ways.append(len(range(int(a), int(b + 1))))

    return math.prod(ways)

main()

# multitime -n 5 ; median:
# cpython: 0.049s
# pypy:    0.091s
