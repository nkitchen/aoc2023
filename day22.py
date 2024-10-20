#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

import functools
from collections import defaultdict
from collections import namedtuple

DEBUG = int(os.environ.get("DEBUG", "0"))

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
                yield from dzs
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

    lone_supporters = set()
    for bi in supporters:
        if len(supporters[bi]) == 1:
            lone_supporters |= supporters[bi]

    disintegrable = len(bricks) - len(lone_supporters)
    print("Part 1:", disintegrable)

    # The critical bricks of brick bi are the bricks in its transitive support
    # such that, if any one of them were disintegrated, it would fall.
    critical = {}
    def _find_critical(bi):
        if bi in critical:
            return critical[bi]

        if supporters[bi]:
            crit = functools.reduce(set.intersection,
                                    (_find_critical(bj) for bj in supporters[bi]))
        else:
            crit = set()

        if len(supporters[bi]) == 1:
            crit |= supporters[bi]

        critical[bi] = crit
        return crit

    t = 0
    for bi in range(len(bricks)):
        crit = _find_critical(bi)
        dprint(f"Crit of {bi}: {crit}")
        t += len(crit)

    print("Part 2:", t)
        
main()

# multitime -n 5 ; median:
# cpython: 21.457s
# pypy:    13.009s
