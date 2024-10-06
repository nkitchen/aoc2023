#!/usr/bin/env python3

import os
import sys
from pprint import pprint

import heapq
import numpy.linalg
from collections import defaultdict

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    inp = open(sys.argv[1])
    part1_steps = int(sys.argv[2])
    part2_steps = int(sys.argv[3])

    grid = [line.rstrip() for line in inp]
    M = len(grid)
    N = len(grid[0])
    assert M == N
    assert M % 2 == 1

    start = next(((i, j) for j in range(N)
                         for i in range(M)
                         if grid[i][j] == 'S'))

    def _reachable_plots_bounded(target_steps):
        def _adj(i, j):
            if i > 0:
                yield (i - 1, j)
            if i < M - 1:
                yield (i + 1, j)
            if j > 0:
                yield (i, j - 1)
            if j < N - 1:
                yield (i, j + 1)

        step_dist = {}
        queue = [(start, 0)]
        while queue:
            loc, d = queue.pop(0)
            if d > target_steps:
                break
            if d >= step_dist.get(loc, 1000000):
                continue
            step_dist[loc] = d

            i, j = loc
            for ii, jj in _adj(i, j):
                if grid[ii][jj] in ".S":
                    queue.append(((ii, jj), d + 1))

        reachable = 0
        for (i, j), d in step_dist.items():
            if d <= target_steps and d % 2 == 0:
                reachable += 1

        return reachable

    print("Part 1:", _reachable_plots_bounded(part1_steps))

    # As BFS expands, eventually we get to a point where every plot has distance M=N greater
    # than the corresponding plots in the adjacent slices closer to the center.
    # After that point, the total number of plots within a given distance is a quadratic
    # function of the distance, for a given modulus of M.
    # (Actually, it has to be modulo M * 2, because M is odd, and the parity of the dist also
    # has to match the target.)
    # If we solve for the quadratic, we can use it with the much larger distance of part 2.
    #
    # We need to make sure that we've reached the point of regularity.
    # We'll call the maximum distance of any point whose distance is not +M from its
    # counterpart the "maximum irregular radius".

    P = part2_steps % (M * 2)

    def _adj(i, j):
        yield (i - 1, j)
        yield (i + 1, j)
        yield (i, j - 1)
        yield (i, j + 1)

    step_dist = {}

    def _regular(i, j):
        u = i // M
        v = j // N
        if u == 0 and v == 0:
            return False
        elif abs(u) > abs(v):
            if u < 0 and ((dd := step_dist.get((i + 2 * M, j))) is None or d != dd + 2 * M):
                return False
            elif u > 0 and ((dd := step_dist.get((i - 2 * M, j))) is None or d != dd + 2 * M):
                return False
        else:
            if v < 0 and ((dd := step_dist.get((i, j + 2 * N))) is None or d != dd + 2 * N):
                return False
            elif v > 0 and ((dd := step_dist.get((i, j - 2 * N))) is None or d != dd + 2 * N):
                return False
        return True

    max_irreg_dist = 0
    queue = [(0, start)]
    while queue:
        d, loc = heapq.heappop(queue)
        if d >= step_dist.get(loc, 10**10):
            continue
        step_dist[loc] = d
        
        i, j = loc
        if not _regular(i, j):
            if d > max_irreg_dist:
                max_irreg_dist = d
                dprint(f"{i=} {j=} {max_irreg_dist=}")

        for ii, jj in _adj(i, j):
            if grid[ii % M][jj % N] in ".S":
                heapq.heappush(queue, (d + 1, (ii, jj)))

        if d > max_irreg_dist + 2 * M and d % (2 * M) == (P + 1) % (2 * M):
            break

    # Interlude: Visualize the distances.
    if (dist_file := os.environ.get("DISTFILE")):
        with open(dist_file, "w") as f:
            def _p(*args, **kwargs):
                print(*args, **kwargs, file=f)

            w = len(str(max(step_dist.values())))
            umin = min(i // M for i, j in step_dist)
            umax = max(i // M for i, j in step_dist)
            vmin = min(j // N for i, j in step_dist)
            vmax = max(j // N for i, j in step_dist)

            for u in range(umin, umax + 1):
                for i in range(M):
                    for v in range(vmin, vmax + 1):
                        for j in range(N):
                            ii = u * M + i
                            jj = v * N + j
                            d = step_dist.get((ii, jj))
                            ind = " "
                            if d is not None:
                                s = f"{d:>{w}}"
                                if abs(u) > abs(v):
                                    if u < 0 and d == step_dist.get((ii + M, jj), d) + M:
                                        ind = "v"
                                    elif u > 0 and d == step_dist.get((ii - M, jj), d) + M:
                                        ind = "^"
                                else:
                                    if v < 0 and d == step_dist.get((ii, jj + N), d) + N:
                                        ind = ">"
                                    elif v > 0 and d == step_dist.get((ii, jj - N), d) + N:
                                        ind = "<"
                            else:
                                s = grid[i][j] * w
                                if s[0] == "S":
                                    s = "." * w

                            _p(s, ind, " ", sep="", end="")
                        _p("   ", end="")
                    _p()
                _p()

    def _plots_within_dist(d_max):
        n = 0
        for d in step_dist.values():
            if  d <= d_max and d % 2 == part2_steps % 2:
                n += 1
        return n

    # First data point: first distance with the right parity outside the radius of irregularity
    d1 = max(d for d in step_dist.values()
             if d % (2 * M) == P)
    a1 = _plots_within_dist(d1)
    dprint(f"{d1=} {a1=}")

    # Keep expanding to collect enough data for the other data points.
    while queue:
        d, loc = heapq.heappop(queue)
        if d >= step_dist.get(loc, 10**10):
            continue
        step_dist[loc] = d
        
        i, j = loc
        if not _regular(i, j):
            if d > max_irreg_dist:
                max_irreg_dist = d
                dprint(f"{i=} {j=} {max_irreg_dist=}")

        for ii, jj in _adj(i, j):
            if grid[ii % M][jj % N] in ".S":
                heapq.heappush(queue, (d + 1, (ii, jj)))

        if d > d1 + 4 * M:
            break
        
    # Second data point
    d2 = d1 + 2 * M
    a2 = _plots_within_dist(d2)
    dprint(f"{d2=} {a2=}")

    # Third data point
    d3 = d2 + 2 * M
    a3 = _plots_within_dist(d3)
    dprint(f"{d3=} {a3=}")

    dmat = numpy.array([[d1**2, d1, 1],
                     [d2**2, d2, 1],
                     [d3**2, d3, 1]])
    avec = numpy.array([a1, a2, a3])
    coeffs = numpy.linalg.solve(dmat, avec)
    d = part2_steps
    a = coeffs[0] * d**2 + coeffs[1] * d + coeffs[2]
    print("Part 2:", a)
        
main()

# multitime -n 5 ; median:
# cpython: 21.457s
# pypy:    13.009s
