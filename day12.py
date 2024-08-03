#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import functools
import itertools

DEBUG = os.environ.get("DEBUG")

def main():
    records = []
    for line in fileinput.input():
        conditions, g = line.split()
        groups = list(map(int, g.split(",")))
        records.append((conditions, groups))

    print("Part 1:", arrangements(records))

    FOLD_FACTOR = 5
    unfolded_records = []
    for conditions, groups in records:
        ucond = "?".join(itertools.repeat(conditions, FOLD_FACTOR))
        ugroups = groups * FOLD_FACTOR
        unfolded_records.append((ucond, ugroups))

    print("Part 2:", arrangements(unfolded_records))
    
def arrangements(records):
    s = 0
    for conditions, groups in records:
        # Add an undamaged spring at the end to simplify end-of-group checking.
        conditions += "."

        @functools.lru_cache(maxsize=None)
        def _matches(cstart, gstart):
            """Returns the number of ways that the groups in groups[gstart:]
            can match the conditions in conditions[cstart:].
            """
            while cstart < len(conditions) and conditions[cstart] == ".":
                cstart += 1

            if gstart == len(groups):
                if conditions.find("#", cstart) == -1:
                    return 1
                else:
                    return 0

            group = groups[gstart]

            last_start = conditions.find("#", cstart)
            if last_start == -1:
                last_start = len(conditions)

            n = 0
            for i in range(cstart, last_start + 1):
                j = i + group
                if j > len(conditions):
                    break

                if j < len(conditions) and conditions[j] == "#":
                    continue

                if conditions.find(".", i, j) != -1:
                    continue

                n += _matches(j + 1, gstart + 1)

            if DEBUG:
                print(conditions[cstart:], groups[gstart:], ">>>", n)

            return n

        m = _matches(0, 0)
        if DEBUG:
            print(m, conditions, groups)
        s += m

    return s

main()

# multitime -n 5 ; median:
# cpython: 0.597s
# pypy:    0.843s
