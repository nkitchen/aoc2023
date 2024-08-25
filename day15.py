#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import operator
import re
from collections import namedtuple
from functools import reduce

DEBUG = os.environ.get("DEBUG")

def dprint(*args):
    if DEBUG:
        print(*args)

Lens = namedtuple('Lens', 'label focal_length')

def main():
    for line in fileinput.input():
        steps = line.strip().split(',')
        s = sum(aoc_hash(step) for step in steps)
        print("Part 1:", s)

        boxes = [{} for i in range(256)]
        for step in steps:
            label, op, n = re.match(r"([a-z]+)([-=])(\d*)", step).groups()
            box = boxes[aoc_hash(label)]
            if op == '-':
                box.pop(label, None)
            else:
                assert op == '='
                box[label] = Lens(label, int(n))

        total_power = 0
        for i, box in enumerate(boxes):
            for j, lens in enumerate(box.values()):
                power = (1 + i) * (1 + j) * lens.focal_length
                total_power += power
        print("Part 2:", total_power)

def aoc_hash(s):
    h = 0
    for c in s:
        h += ord(c)
        h *= 17
        h %= 256
    return h

main()

# multitime -n 5 ; median:
# cpython: 0.054s
# pypy:    0.097s
