#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import itertools

def main():
    grid = list(filter(None, (line.strip() for line in fileinput.input())))

    galaxies = set()
    x_pre_exp = set()
    y_pre_exp = set()
    for y, _ in enumerate(grid):
        for x, _ in enumerate(grid[y]):
            if grid[y][x] == '#':
                galaxies.add((x, y))
                x_pre_exp.add(x)
                y_pre_exp.add(y)

    def _dist_sum(expansion_factor):
        def _expansion(coords):
            exp = {}
            prev = -1
            prev_exp = -1
            for c in sorted(coords):
                dc = c - prev
                gap = dc - 1
                prev_exp = exp[c] = prev_exp + gap * expansion_factor + 1
                prev = c
            return exp

        exp_x = _expansion(x_pre_exp)
        exp_y = _expansion(y_pre_exp)

        galaxies_post_exp = set(
            (exp_x[x], exp_y[y]) for x, y in galaxies
        )

        s = 0
        for g1, g2 in itertools.combinations(galaxies_post_exp, 2):
            x1, y1 = g1
            x2, y2 = g2
            s += (d := abs(x1 - x2) + abs(y1 - y2))

        return s

    print("Part 1:", _dist_sum(2))
    print("Part 2:", _dist_sum(10 ** 6))

main()

# multitime -n 5 ; median:
# cpython: 0.089s
# pypy:    0.084s
