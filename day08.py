#!/usr/bin/env python3

import fileinput
import itertools
import math
import re
from pprint import pprint

def main():
    succs = {}

    for line in fileinput.input():
        line = line.strip()
        if re.match( r"[RL]+$", line ):
            insts = line
            continue
        if '=' in line:
            n, l, r = re.findall( r"\w+", line )
            succs[n] = (l, r)

    inst_index = {'L': 0, 'R': 1}

    if (n := 'AAA') in succs:
        steps = 0
        for inst in itertools.cycle(insts):
            n = succs[n][inst_index[inst]]
            steps += 1
            if n == 'ZZZ':
                break

        print("Part 1:", steps)

    # Part 2:
    # My input structure: Multiple disjoint rings of nodes, each with one start
    # (A) node and one end (Z) node.

    start = set()
    for n in succs:
        if n.endswith('A'):
            start.add(n)

    z_cycle_lengths = []

    for s in start:
        t = 0
        z_times = []
        n = s
        while True:
            i = t % len(insts)
            inst = insts[i]
            n = succs[n][inst_index[inst]]
            t += 1
            if n.endswith('Z'):
                z_times.append(t)
                if len(z_times) == 2:
                    # There's no initial part of the path before entering the cycle.
                    assert(z_times[1] == 2 * z_times[0])
                    z_cycle_lengths.append(z_times[0])
                    break

    t = math.lcm(*z_cycle_lengths)
    print("Part 2:", t)

main()

# multitime -n 5 ; median:
# cpython: 0.051s
# pypy:    0.099s
