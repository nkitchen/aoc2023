#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

import heapq
from collections import defaultdict
from collections import namedtuple

DEBUG = os.environ.get("DEBUG", "")

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    grid = [list(line) for line in fileinput.input()]
    M = len(grid)
    N = len(grid[0])

    def _adj(i, j):
        if i > 0 and grid[i - 1][j] != '#':
            yield (i - 1, j)
        if i < M - 1 and grid[i + 1][j] != '#':
            yield (i + 1, j)
        if j > 0 and grid[i][j - 1] != '#':
            yield (i, j - 1)
        if j < N - 1 and grid[i][j + 1] != '#':
            yield (i, j + 1)

    # Do the trails form a DAG?

    rep = {}
    def _lookup_rep(loc):
        r = rep.get(loc, loc)
        if r != loc:
            rep[loc] = r = _lookup_rep(r)
        return r

    def _join(loc1, loc2):
        r1 = _lookup_rep(loc1)
        r2 = _lookup_rep(loc2)
        if r1 != r2:
            r1, r2 = (min(r1, r2), max(r1, r2))
            rep[r2] = r1

    # Find connected regions.
    for i in range(M):
        for j in range(N):
            if grid[i][j] != '.':
                continue

            for ii, jj in _adj(i, j):
                if grid[ii][jj] == '.':
                    _join((i, j), (ii, jj))
    # Settle reps.
    for i in range(M):
        for j in range(N):
            _lookup_rep((i, j))

    # Collect connections between regions.
    slope_edges = set()
    for i in range(M):
        for j in range(N):
            if grid[i][j] == '^':
                u = _lookup_rep((i + 1, j))
                v = _lookup_rep((i - 1, j))
                slope_edges.add((u, v))
            elif grid[i][j] == 'v':
                u = _lookup_rep((i - 1, j))
                v = _lookup_rep((i + 1, j))
                slope_edges.add((u, v))
            elif grid[i][j] == '<':
                u = _lookup_rep((i, j + 1))
                v = _lookup_rep((i, j - 1))
                slope_edges.add((u, v))
            elif grid[i][j] == '>':
                u = _lookup_rep((i, j - 1))
                v = _lookup_rep((i, j + 1))
                slope_edges.add((u, v))

    # Emit graph.
    print("digraph {")
    for u, v in slope_edges:
        i, j = u
        ii, jj = v
        print(f"  x{i}_{j} -> x{ii}_{jj};")
    print("}")

main()

# multitime -n 5 ; median:
# cpython: 21.457s
# pypy:    13.009s
