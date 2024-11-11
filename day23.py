#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

import copy
import functools
import heapq
from collections import defaultdict
from collections import namedtuple

import cpmpy as cp

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
    adj = copy.deepcopy(steps_from)
    for u in steps_from:
        for v, d in steps_from[u]:
            adj[v].append((u, d))

    # The longest-path problem is NP-complete in general.
    # My attempts at a brute-force (backtracking) search were too slow
    # (how did others do it in under 60 seconds?)
    # so I'll use the big hammer: a constraint solver.

    # true if the point is visited by the path
    visited = {}
    for v in steps_from:
        visited[v] = cp.boolvar(name=f"vis{v}")
    visited[end] = cp.boolvar(name=f"vis{end}")

    # 1 if the edge is used, 0 if not
    edge = {}
    for u in steps_from:
        for v, _ in steps_from[u]:
            edge[(u, v)] = cp.intvar(0, 1, name=f"e{u}_{v}")
            edge[(v, u)] = cp.intvar(0, 1, name=f"e{v}_{u}")

    model = cp.Model()

    # Use each edge in at most one direction.
    for u in steps_from:
        for v, _ in steps_from[u]:
            model += (edge[(u, v)] + edge[(v, u)] <= 1)

    # Simple path: one edge in -> one edge out
    for u in adj:
        ingress = [edge[(v, u)] for v, _ in adj[u]]
        egress = [edge[(u, v)] for v, _ in adj[u]]

        if u == start:
            assert len(egress) == 1
            model += (egress[0] == 1)
        elif u == end:
            assert len(ingress) == 1
            model += (ingress[0] == 1)
        else:
            model += (sum(ingress) <= 1)
            model += (sum(ingress) == sum(egress))

    # The constraints so far are sufficient to get a simple path from start to
    # end.  But they allow for disconnected cycles of edges that add to the
    # objective function.  To prevent the cycles, I need additional constraints
    # defining hop counts.

    MAX_HOPS = len(edge) // 2
    hops = {}
    for v in adj:
        hops[v] = cp.intvar(0, MAX_HOPS, name=f"hops{v}")

    for v in adj:
        ingress = [edge[(u, v)] for u, _ in adj[v]]
        if len(ingress) == 0:
            model += (hops[v] == 0)
        else:
            model += (sum(ingress) == 0).implies(hops[v] == 0)

        for u, _ in adj[v]:
            model += (edge[(u, v)] == 1).implies(hops[v] == 1 + hops[u])

    obj = 0
    for u in adj:
        for v, d in adj[u]:
            obj += d * edge[(u, v)]
    model.maximize(obj)

    dprint(model)
    if model.solve():
        hike = model.objective_value()
        print("Part 2:", hike)
    else:
        print("Not solved")

main()

# multitime -n 5 ; median:
# cpython: 0.999s
# pypy:    Didn't try
# CPMpy wants OR-Tools, which doesn't work with pypy.
# cpython runs it so fast that pypy isn't really interesting anyway.
