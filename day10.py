#!/usr/bin/env python3

import fileinput
from pprint import pprint

from collections import defaultdict

def main():
    grid = list(filter(None, (line.strip() for line in fileinput.input())))

    def _find_start():
        for i, _ in enumerate(grid):
            for j, _ in enumerate(grid[i]):
                if grid[i][j] == 'S':
                    return (i, j)
        return None
    start = _find_start()

    dp = {
        'S': [(-1, 0), (1, 0), (0, -1), (0, 1)],
        '|': [(-1, 0), (1, 0)],
        '-': [(0, -1), (0, 1)],
        'L': [(-1, 0), (0, 1)],
        'J': [(-1, 0), (0, -1)],
        '7': [(1, 0), (0, -1)],
        'F': [(1, 0), (0, 1)],
        '.': [],
    }

    def _adj(i, j):
        c = grid[i][j]
        if c == 'S':
            for di, dj in dp[c]:
                ii = i + di
                jj = j + dj
                if (0 <= ii < len(grid) and
                    0 <= jj < len(grid[i]) and
                    (i, j) in list(_adj(ii, jj))):
                    yield (ii, jj)
        else:
            for di, dj in dp[c]:
                ii = i + di
                jj = j + dj
                if 0 <= ii < len(grid) and 0 <= jj < len(grid[i]):
                    yield (ii, jj)

    dist = {start: 0}
    queue = [start]
    while queue:
        p = queue[0]
        queue = queue[1:]

        i, j = p
        for pp in _adj(i, j):
            if pp in dist:
                continue
            d = dist[p] + 1
            dist[pp] = d
            queue.append(pp)

    m = max(dist.values())

    print("Part 1:", m)

    ### Part 2

    loop = set(dist)

    # Identify connected non-loop regions: union-find.

    rep = {}
    def _lookup_rep(p):
        r = rep.get(p)
        if r != p:
            rep[p] = r = _lookup_rep(r)
        return r

    def _join(p1, p2):
        r1 = _lookup_rep(p1)
        r2 = _lookup_rep(p2)
        if r1 != r2:
            r1, r2 = (min(r1, r2), max(r1, r2))
            rep[r2] = r1

    for i, _ in enumerate(grid):
        for j, _ in enumerate(grid[i]):
            p = (i, j)
            if p not in loop:
                rep[p] = p

    def _non_loop_adj(p):
        i, j = p
        for ii in (i - 1, i + 1):
            if 0 <= ii < len(grid) and (pp := (ii, j)) not in loop:
                yield pp
        for jj in (j - 1, j + 1):
            if 0 <= jj < len(grid[i]) and (pp := (i, jj)) not in loop:
                yield pp

    for p in rep:
        for pp in _non_loop_adj(p):
            _join(p, pp)

    # Collapse rep pointers for all of them.
    for p in rep:
        _lookup_rep(p)

    regions = defaultdict(list)
    for p in rep:
        r = _lookup_rep(p)
        regions[r].append(p)

    # For each region, count the number of loop pipes we need to cross in
    # order to reach the edge of the grid.  If it's even, the region is outside
    # the loop.

    trans = {
        ('.', '-'): ('.', 1),
        ('.', 'L'): ('L', 0),
        ('.', 'J'): ('J', 0),
        ('.', '7'): ('7', 0),
        ('.', 'F'): ('F', 0),

        ('L', '|'): ('L', 0),
        ('L', '7'): ('.', 1),
        ('L', 'F'): ('.', 0),

        ('J', '|'): ('J', 0),
        ('J', '7'): ('.', 0),
        ('J', 'F'): ('.', 1),

        ('7', '|'): ('7', 0),
        ('7', 'L'): ('.', 1),
        ('7', 'J'): ('.', 0),

        ('F', '|'): ('F', 0),
        ('F', 'L'): ('.', 0),
        ('F', 'J'): ('.', 1),
    }

    enclosed = 0
    for r in regions:
        i, j = r
        rg = range(0, i)
        # Avoid needing to determine the shape at the start.
        if any(grid[ii][j] == 'S' for ii in rg):
            rg = range(i + 1, len(grid))

        k = 0
        state = '.'
        for ii in rg:
            if (ii, j) not in loop:
                continue
            state, dk = trans[(state, grid[ii][j])]
            k += dk

        if k % 2 != 0:
            enclosed += len(regions[r])

    print("Part 2:", enclosed)

main()

# multitime -n 5 ; median:
# cpython: 0.110s
# pypy:    0.264s
