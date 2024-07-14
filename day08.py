#!/usr/bin/env python3

import fileinput
import itertools
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

    nn = set()
    for n in succs:
        if n.endswith('A'):
            nn.add(n)

    steps = 0
    for inst in itertools.cycle(insts):
        nn = set(succs[n][inst_index[inst]] for n in nn)
        steps += 1
        if all(n.endswith('Z') for n in nn):
            break

    print("Part 2:", steps)

main()

# multitime -n 5 ; median:
# cpython: 0.051s
# pypy:    0.099s
