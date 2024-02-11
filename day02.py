#!/usr/bin/env python3

import fileinput
import re

impossible_re = re.compile(r"""(?x) (?: 1[3-9] | [2-9]\d )[ ]red |
                                    (?: 1[4-9] | [2-9]\d )[ ]green |
                                    (?: 1[5-9] | [2-9]\d )[ ]blue""")

possible_sum = 0

input_lines = list(fileinput.input())

for line in input_lines:
    fields = line.split(":", 1)
    if impossible_re.search(fields[1]):
        continue

    game_id = int(fields[0].split()[1])
    possible_sum += game_id

print(possible_sum)

red_re = re.compile(r"(\d+) red")
green_re = re.compile(r"(\d+) green")
blue_re = re.compile(r"(\d+) blue")

def min_set(line):
    r = max(int(s) for s in red_re.findall(line))
    g = max(int(s) for s in green_re.findall(line))
    b = max(int(s) for s in blue_re.findall(line))
    return r, g, b

power_sum = 0
for line in input_lines:
    r, g, b = min_set(line)
    power_sum += r * g * b

print(power_sum)

# multitime -n 5 ; median:
# cpython: 0.037s
# pypy:    0.074s
