#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

import functools
import heapq
from collections import defaultdict
from collections import namedtuple

DEBUG = os.environ.get("DEBUG", "")

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    grid = [list(line.rstrip()) for line in fileinput.input()]
    M = len(grid)
    N = len(grid[0])

    assert grid[0][1] == '.'
    assert grid[M - 1][N - 2] == '.'
    start = (0, 1)
    end = (M - 1, N - 2)

    def _adj(i, j):
        if i > 0 and grid[i - 1][j] != '#' and grid[i][j] in '.^':
            yield (i - 1, j)
        if i < M - 1 and grid[i + 1][j] != '#' and grid[i][j] in '.v':
            yield (i + 1, j)
        if j > 0 and grid[i][j - 1] != '#' and grid[i][j] in '.<':
            yield (i, j - 1)
        if j < N - 1 and grid[i][j + 1] != '#' and grid[i][j] in '.>':
            yield (i, j + 1)

    # The slopes are always arranged in "gadgets" surrounding single "nexus"
    # tiles.
    # First step: Find the nexuses.
    nexuses = set()
    for i in range(M):
        for j in range(N):
            assert grid[i][j] not in '^<'

            if grid[i][j] != '.':
                continue
            if not (0 < i < M - 1):
                continue
            if not (0 < j < N - 1):
                continue
            if grid[i - 1][j] == grid[i + 1][j] == 'v':
                nexuses.add((i, j))
            elif grid[i][j- 1] == grid[i][j + 1] == '>':
                nexuses.add((i, j))
    
    # Construct an acyclic graph connecting:
    # - the start point
    # - the end point
    # - the nexus points
    # Each edge is labeled with the number of steps between the points it
    # connects.
    steps_from = defaultdict(list)
    search_starts = [start]
    while search_starts:
        u = search_starts.pop(0)

        steps = {u: 0}
        q = [u]
        while q:
            v = q.pop(0)
            for w in _adj(*v):
                if w in steps:
                    continue
                steps[w] = 1 + steps[v]
                if w in nexuses:
                    steps_from[u].append((w, steps[w]))
                    if w not in steps_from and w not in search_starts:
                        search_starts.append(w)
                elif w == end:
                    steps_from[u].append((w, steps[w]))
                else:
                    q.append(w)

    if (graph_file := os.environ.get("GRAPH")):
        with open(graph_file, "w") as f:
            def gpr(s):
                print(s, file=f)

            gpr("digraph {")
            for u in steps_from:
                i, j = u
                for v, d in steps_from[u]:
                    ii, jj = v
                    gpr(f'  x{i}_{j} -> x{ii}_{jj} [label="{d}"];')
            gpr("}")

    @functools.lru_cache(maxsize=None)
    def _max_steps_to_end_from(v):
        if v == end:
            return 0

        return max(d + _max_steps_to_end_from(w)
                   for w, d in steps_from[v])

    hike = _max_steps_to_end_from(start)
    print("Part 1:", hike)

    # Part 2: I can still use the graph between nexus points, but I need to
    # treat the edges as reversible.

    # Add the reverse edges.
    adj = steps_from.copy()
    for u in steps_from:
        for v, d in steps_from[u]:
            adj[v].append((u, d))

    # But: The longest-path problem is NP-complete in general.
    # I'm going to take a leap of faith with a greedy approach:
    # backtracking recursive search, preferring the highest-distance edge at
    # each step.

    def _longest_path(u, steps_so_far, visited):
        if u == end:
            return steps_so_far

        choices = [(d, v) for v, d in adj[u]
                   if v not in visited]
        if not choices:
            return None

        choices.sort(reverse=True)
        for d, v in choices:
            steps_so_far += d
            visited.add(v)

            p = _longest_path(v, steps_so_far, visited)
            if p is not None:
                return p

            steps_so_far -= d
            visited.remove(v)

        return None

    hike = _longest_path(start, 0, {start})
    print("Part 2:", hike)

main()

# multitime -n 5 ; median:
# cpython: 21.457s
# pypy:    13.009s
