#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

import functools
import itertools
import heapq
import string
from collections import defaultdict
from collections import namedtuple

DEBUG = os.environ.get("DEBUG", "")

def dprint(*args):
    if DEBUG:
        print(*args)

Point = namedtuple('Point', 'x y z')

def main():
    bricks = []
    for line in fileinput.input():
        line = line.rstrip()
        b = []
        for part in line.split('~'):
            xyz = [int(w) for w in part.split(',')]
            b.append(Point(*xyz))
        assert len(b) == 2
        assert b[0].x <= b[1].x
        assert b[0].y <= b[1].y
        assert b[0].z <= b[1].z
        bricks.append(b)

    # 0 <= x, y <= 9

    bricks.sort(key=lambda b: b[0].z)

    def _brick_xy(b):
       for x in range(b[0].x, b[1].x + 1):
           for y in range(b[0].y, b[1].y + 1):
               yield (x, y)

    bricks_by_xy = defaultdict(list)
    for bi, b in enumerate(bricks):
        for xy in _brick_xy(b):
           bricks_by_xy[xy].append(bi)

    def _open_cubes_below(bi):
        for xy in _brick_xy(bricks[bi]):
            dzs = []
            for bj in bricks_by_xy[xy]:
                if (dz := bricks[bi][0].z - bricks[bj][1].z) > 0:
                    dzs.append(dz)
            if dzs:
                yield min(dzs)
            else:
                # Distance to ground
                yield bricks[bi][0].z

    for bi in range(len(bricks)):
        # How high is this brick above something else?
        dz = min(_open_cubes_below(bi))
        if dz > 1:
            p, q = bricks[bi]
            bricks[bi] = [Point(p.x, p.y, p.z - dz + 1),
                          Point(q.x, q.y, q.z - dz + 1)]

    # All the bricks have fallen.

    if "check" in DEBUG:
        # The bricks are still in the same order.
        for xy in bricks_by_xy:
            for i, bi in enumerate(bricks_by_xy[xy]):
                for j in range(i + 1, len(bricks_by_xy[xy])):
                    bj = bricks_by_xy[xy][j]
                    assert bricks[bi][1].z < bricks[bj][0].z

    supporters = defaultdict(set)
    for bi in range(len(bricks)):
        bi0z = bricks[bi][0].z
        for xy in _brick_xy(bricks[bi]):
            supp = None
            for bj in bricks_by_xy[xy]:
                if bricks[bj][1].z + 1 == bi0z:
                    supp = bj
                    break
            if supp is not None:
                supporters[bi].add(supp)

    if "check" in DEBUG:
        # Every brick rests on at least one other (or the ground).
        for b in range(len(bricks)):
            if not supporters[bi]:
                assert bricks[bi][0].z == 1

    lone_supporters = set()
    for bi in supporters:
        if len(supporters[bi]) == 1:
            lone_supporters |= supporters[bi]

    disintegrable = len(bricks) - len(lone_supporters)
    print("Part 1:", disintegrable)

    code = dict(zip(range(len(bricks)),
                    (''.join(args) for args in
                     itertools.product(string.ascii_uppercase, repeat=2))))

    # The critical bricks of brick bi are the bricks in its transitive support
    # such that, if any one of them were disintegrated, it would fall.
    critical = {}
    def _find_critical(bi):
        if bi in critical:
            return critical[bi]

        if supporters[bi]:
            crit = functools.reduce(set.intersection,
                                    (_find_critical(bj) for bj in supporters[bi]))
            if len(supporters[bi]) == 1:
                crit = crit.union(supporters[bi])
        else:
            crit = set()

        critical[bi] = crit
        return crit

    t = 0
    for bi in range(len(bricks)):
        crit = _find_critical(bi)
        if "crit" in DEBUG:
            print(f"Crit of {bi} {code[bi]}: {crit}", [code[bj] for bj in crit])
        t += len(crit)
    print("Part 2:", t)

    if "draw" in DEBUG:

        grid = {}
        for bi, b in enumerate(bricks):
            for z in range(b[0].z, b[1].z + 1):
                for x, y in _brick_xy(b):
                    grid[(x, y, z)] = bi

        zmax = max(z for x, y, z in grid)
        
        def printc(*args):
            print(*args, end="")

        printc("    ")
        for y in range(10):
            printc(f"{y=} ")
            printc("  " * 9)
        print()

        printc("    ")
        for y in range(10):
            for x in range(10):
                printc(f"{x:>2}")
            printc("  ")
        print()

        for z in range(zmax, 0, -1):
            printc(f"{z:>4}")
            for y in range(10):
                for x in range(10):
                    if (bi := grid.get((x, y, z))) is not None:
                        printc(code[bi])
                    else:
                        printc("..")
                printc("  ")
            print()

main()

# multitime -n 5 ; median:
# cpython: 0.112s
# pypy:    0.257s
