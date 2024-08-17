#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

DEBUG = os.environ.get("DEBUG")

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    grids = [[]]
    for line in fileinput.input():
        line = line.strip()
        if line:
            grids[-1].append(line)
        else:
            grids.append([])

    if not grids[-1]:
        grids.pop()

    s = 0
    for grid in grids:
        s += reflection_summary(grid)

    print("Part 1:", s)

    s = 0
    for grid in grids:
        s += reflection_summary_fixed(grid)

    print("Part 2:", s)

flip = {'.': '#', '#': '.'}

def reflection_summary_fixed(grid):
    s_smudged = reflection_summary(grid)
    m = len(grid)
    n = len(grid[0])
    grid_fixed = [list(row) for row in grid]
    for i in range(m):
        for j in range(n):
            grid_fixed[i][j] = flip[grid_fixed[i][j]]
            s_fixed = reflection_summary(grid_fixed, exclude=s_smudged)
            dprint(f"Fix [{i}][{j}]:", s_fixed)
            if s_fixed is not None:
                return s_fixed

            grid_fixed[i][j] = flip[grid_fixed[i][j]]

    return None

def reflection_summary(grid, exclude=None):
    m = len(grid)
    n = len(grid[0])

    row_sigs = []
    for i in range(m):
        sig = 0
        for j in range(n):
            if grid[i][j] == '#':
                sig += 1 << j
        row_sigs.append(sig)

    col_sigs = []
    for j in range(n):
        sig = 0
        for i in range(m):
            if grid[i][j] == '#':
                sig += 1 << i
        col_sigs.append(sig)

    def _before_reflection(sigs, exclude=None):
        for k1 in range(1, len(sigs)):
            k2 = len(sigs) - k1
            if k1 <= k2:
                kk = k1
                sigs1 = sigs[:k1]
                sigs2 = sigs[k1 : k1 + kk]
            else:
                kk = k2
                sigs1 = sigs[k1 - kk : k1]
                sigs2 = sigs[k1 : k1 + kk]
            if sigs1 == list(reversed(sigs2)) and k1 != exclude:
                return k1
        return None

    exclude_rows = None
    if exclude is not None and exclude % 100 == 0:
        exclude_rows = exclude // 100

    if (k := _before_reflection(col_sigs, exclude=exclude)) is not None:
        return k
    elif (k := _before_reflection(row_sigs, exclude=exclude_rows)) is not None:
        return 100 * k
    else:
        return None

main()

# multitime -n 5 ; median:
# cpython: 0.410s
# pypy:    0.222s
