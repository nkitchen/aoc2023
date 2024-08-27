#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import heapq
import math
from collections import namedtuple, defaultdict

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args):
    if DEBUG:
        print(*args)

State = namedtuple('State', 'loc vel')

def rot_left(vel):
    return (-vel[1], vel[0])

def rot_right(vel):
    return (vel[1], -vel[0])

def main():
    grid = [list(map(int, line.rstrip())) for line in fileinput.input()]
    m = len(grid)
    n = len(grid[0])

    def _adj(i, j):
        if i > 0:
            yield (i - 1, j)
        if i < m - 1:
            yield (i + 1, j)
        if j > 0:
            yield (i, j - 1)
        if j < n - 1:
            yield (i, j + 1)

    min_loss_to_factory = {}
    q = [(0, m - 1, n - 1)]
    while q:
        loss, i, j = heapq.heappop(q)
        if (i, j) in min_loss_to_factory:
            continue
        min_loss_to_factory[(i, j)] = loss
        if DEBUG & 2:
            for iii in range(m):
                print(''.join("{:3}".format(str(min_loss_to_factory.get((iii, jjj), '-')))
                              for jjj in range(n)))
            print()

        for ii, jj in _adj(i, j):
            lloss = grid[i][j] + loss
            heapq.heappush(q, (lloss, ii, jj))

    if DEBUG > 100:
        for i in range(m):
            for j in range(n):
                if i == m - 1 and j == n - 1:
                    continue
                mm = min(grid[ii][jj] + min_loss_to_factory[(ii, jj)]
                        for ii, jj in _adj(i, j))
                try:
                    assert min_loss_to_factory[(i, j)] == mm
                except AssertionError:
                    print(i, j)
                    raise

    def moves(s):
        if s.loc == (0, 0):
            for k in range(1, 4):
                yield State(loc=(0, k), vel=(0, 1))
                yield State(loc=(k, 0), vel=(1, 0))
            return

        for vv in (rot_left(s.vel), rot_right(s.vel)):
            di, dj = vv
            for k in range(1, 4):
                ii = s.loc[0] + k * di
                jj = s.loc[1] + k * dj
                if (0 <= ii < m) and (0 <= jj < n):
                    yield State(loc=(ii, jj), vel=vv)

    pred = {}
    start = State(loc=(0, 0), vel=(0, 0))
    loss_so_far = defaultdict(lambda: math.inf)
    loss_so_far[start] = 0
    q = [(min_loss_to_factory[start.loc], start)]
    frontier = set([start])
    while q:
        e, s = heapq.heappop(q)
        if s.loc == (m - 1, n - 1):
            break

        frontier.remove(s)
        #if s.loss < visited.get(s.loc, s.loss + 1):
        #    visited[s.loc] = s.loss
        #else:
        #    continue

        #pred[s.loc] = s.pred

        if DEBUG & 4:
            for i in range(m):
                for j in range(n):
                    v = str(loss_so_far.get(State(loc=(i, j)), "."))
                    ml = min_loss_to_factory[(i, j)]
                    print(f"{grid[i][j]:>4}:{v:>2}+{ml:>2} ", end='')
                print()
            print()

        dprint("==", e, s)

        i, j = s.loc
        for ss in moves(s):
            ii, jj = ss.loc

            loss = loss_so_far[s]
            if ii == i:
                for mj in range(jj, j, -ss.vel[1]):
                    loss += grid[ii][mj]
            else:
                assert jj == j
                for mi in range(ii, i, -ss.vel[0]):
                    loss += grid[mi][jj]

            if loss < loss_so_far[ss]:
                pred[ss] = s
                loss_so_far[ss] = loss
                est_loss = loss + min_loss_to_factory[ss.loc]
                if ss not in frontier:
                    frontier.add(ss)
                    heapq.heappush(q, (est_loss, ss))
                    dprint("  > ", est_loss, ss)

            ##if loss > visited.get(dst, loss + 1):
            ##    continue
            #est_loss = loss # + min_loss_to_factory[(ii, jj)]
            #ss = State(est_loss, loss, dst, vel, run, s.loc)
            #dprint("  > ", ss)
            #heapq.heappush(q, ss)

    print("Part 1:", loss_so_far[s])

    if DEBUG & 8:
        path = [["."] * n for i in range(m)]
        while s:
            i, j = s.loc
            if s.vel == (0, 1):
                path[i][j] = '>'
            elif s.vel == (0, -1):
                path[i][j] = '<'
            elif s.vel == (1, 0):
                path[i][j] = 'v'
            elif s.vel == (-1, 0):
                path[i][j] = '^'
            else:
                path[i][j] = '#'
            s = pred.get(s)

        for i in range(m):
            print(''.join(path[i]))
        
main()

# multitime -n 5 ; median:
# cpython: 3.783s
# pypy:    1.258s
