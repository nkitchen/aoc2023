#!/usr/bin/env python3

import fileinput
import re
from collections import defaultdict

schematic = list(line.rstrip() for line in fileinput.input())


def adj(i, mat):
    j1 = max(0, mat.start() - 1)
    j2 = min(len(mat.string), mat.end() + 1)
    if i > 0:
        yield (i - 1, j1, j2)
    if 0 < (jl := mat.start()):
        yield (i, jl - 1, jl)
    if (jr := mat.end()) < len(mat.string):
        yield (i, jr, jr + 1)
    if i < len(schematic) - 1:
        yield (i + 1, j1, j2)

part_nums = {}

star_parts = defaultdict(list)

sym_re = re.compile(r"[^.0-9]")
for i, row in enumerate(schematic):
    for mat in re.finditer(r"\d+", row):
        j = mat.start()
        n = int(mat.group())
        for ii, j1, j2 in adj(i, mat):
            for m in sym_re.finditer(schematic[ii], j1, j2):
                part_nums[(i, j)] = n
                if m.group() == "*":
                    star_i = ii
                    star_j = m.start()
                    star_parts[(star_i, star_j)].append(n)

s = sum(part_nums.values())
print(s)

ratio_sum = 0
for parts in star_parts.values():
    if len(parts) == 2:
        ratio_sum += parts[0] * parts[1]
print(ratio_sum)

# multitime -n 5 ; median:
# cpython: 0.038s
# pypy:    0.119s
