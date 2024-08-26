#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import heapq
from collections import namedtuple

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args):
    if DEBUG:
        print(*args)

State = namedtuple('State', 'est_loss loss loc vel run pred')

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
            yield ((0, 1), (0, 1))
            yield ((1, 0), (1, 0))
            return

        if s.run < 3:
            ii = s.loc[0] + s.vel[0]
            jj = s.loc[1] + s.vel[1]
            if (0 <= ii < m) and (0 <= jj < n):
                yield s.vel, (ii, jj)

        for vv in (rot_left(s.vel), rot_right(s.vel)):
            ii = s.loc[0] + vv[0]
            jj = s.loc[1] + vv[1]
            if (0 <= ii < m) and (0 <= jj < n):
                yield vv, (ii, jj)

    visited = {}
    pred = {}
    q = [State(min_loss_to_factory[(0, 0)], 0, (0, 0), (0, 0), 0, None)]
    while q:
        s = heapq.heappop(q)
        if s.loss < visited.get(s.loc, s.loss + 1):
            visited[s.loc] = s.loss
        else:
            continue

        pred[s.loc] = s.pred

        if DEBUG & 4:
            for i in range(m):
                for j in range(n):
                    v = str(visited.get((i, j), "."))
                    ml = min_loss_to_factory[(i, j)]
                    print(f"{grid[i][j]:>4}:{v:>2}+{ml:>2} ", end='')
                print()
            print()

        dprint("==", s)

        if s.loc == (m - 1, n - 1):
            break

        for vel, dst in moves(s):
            if vel == s.vel:
                run = s.run + 1
            else:
                run = 1
            ii, jj = dst
            loss = s.loss + grid[ii][jj]
            if loss > visited.get(dst, loss + 1):
                continue
            est_loss = loss # + min_loss_to_factory[(ii, jj)]
            ss = State(est_loss, loss, dst, vel, run, s.loc)
            dprint("  > ", ss)
            heapq.heappush(q, ss)

    path = [["."] * n for i in range(m)]
    loc = (m - 1, n - 1)
    while loc:
        i, j = loc
        path[i][j] = '#'
        loc = pred.get(loc)

    if True or DEBUG & 8:
        for i in range(m):
            print(''.join(path[i]))

    print("Part 1:", s.loss)
        
main()

# multitime -n 5 ; median:
# cpython: 3.783s
# pypy:    1.258s
