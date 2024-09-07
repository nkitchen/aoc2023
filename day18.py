#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import bisect
import itertools
import re
from collections import defaultdict

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args):
    if DEBUG:
        print(*args)

dir_del = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1),
}

# Single-quadrant/outside corners
NW_OUTSIDE = 1
NE_OUTSIDE = 2
SW_OUTSIDE = 4
SE_OUTSIDE = 8
# Inside corners
NW_INSIDE = 16
NE_INSIDE = 32
SW_INSIDE = 64
SE_INSIDE = 128

digit_dir = {
    '0': 'R',
    '1': 'D',
    '2': 'L',
    '3': 'U',
}

def main():
    plan = []
    for line in fileinput.input():
        if (m := re.search(r"([UDLR]) +(\d+) +[(]#([0-9a-f]+)[)]", line)):
            dir, n, color = m.groups()
            plan.append((dir, int(n), color))

    grid = defaultdict(lambda: '.')
    grid[(0, 0)] = '#'
    r, c = (0, 0)
    for dir, n, color in plan:
        dr, dc = dir_del[dir]
        for k in range(1, n + 1):
            r += dr
            c += dc
            grid[(r, c)] = '#'

    ravg = sum(rc[0] for rc in grid) // len(grid)
    cavg = sum(rc[1] for rc in grid) // len(grid)
    # Is the average of the edge locations inside the trench?
    # For the example and for my input, it is.
    # Verified here: There is an odd number of edges on each side of the
    # average location.
    nl = nr = 0
    for r, c in grid:
        if r == ravg:
            if c < cavg:
                nl += 1
            else:
                nr += 1
    assert nl % 2 == 1
    assert nr % 2 == 1

    def _adj(r, c):
        yield (r - 1, c)
        yield (r + 1, c)
        yield (r, c - 1)
        yield (r, c + 1)

    q = [(ravg, cavg)]
    while q:
        r, c = q.pop()
        for rr, cc in _adj(r, c):
            if grid[(rr, cc)] != '#':
                grid[(rr, cc)] = '#'
                q.append((rr, cc))

    print("Part 1:", len(grid))

    # Generate corner points (r, c).
    r, c = (0, 0)
    corners = [(r, c)]
    #for dir, n, color in plan:
    for _, _, code in plan:
        n = int(code[:5], 16)
        dir = digit_dir[code[5]]
        dr, dc = dir_del[dir]
        dr *= n
        dc *= n
        r += dr
        c += dc
        corners.append((r, c))
    assert corners[0] == corners[-1]
    corners.pop()

    if (plot_file := os.environ.get('PLOT')):
        with open(plot_file, 'w') as f:
            for r, c in corners:
                print(r, c, file=f)

    corners.sort()

    # Step through the rectangular strips of the enclosed space.
    area = 0
    r_top = None
    cs_top = None
    for _, rcs in itertools.groupby(corners, lambda rc: rc[0]):
        rcs = list(rcs)
        assert len(rcs) % 2 == 0

        cs = [c for (r, c) in rcs]

        if r_top is None:
            r_top = rcs[0][0]
            cs_top = cs
            continue

        r = rcs[0][0]
        # Count only the cells above the current row.
        # The cells in the current row will be counted as the strips narrow or
        # widen, or they will contribute to the strips in the next iteration.
        h = r - r_top
        for c1, c2 in batched(cs_top, 2):
            w = c2 - c1 + 1
            area += h * w

        dprint(f"{area=}")
        dprint(f"{r_top=}")
        dprint(f"{cs_top=}")
        dprint(f"{r=}")
        dprint(f"{cs=}")
        dprint()

        # Each pair makes a line segment.
        # At least one end of the segment aligns with the edge of a current strip
        # (because all the strips are rectangular).
        # Does it widen or narrow an existing strip?
        # Or does it join two strips?
        for c1, c2 in batched(cs, 2):
            if (i := find(cs_top, c1)) >= 0:
                if i % 2 == 0:
                    c_top2 = cs_top[i + 1]
                    if c2 < c_top2:
                        # Case A
                        # *-----*
                        # |.....|
                        # *--*..|
                        #    :..:
                        area += c2 - c1 # Area that is not in the narrowed strip
                        cs_top[i] = c2
                    else:
                        assert c2 == c_top2
                        # Case B
                        # *--*
                        # |..|
                        # *--*
                        area += c2 - c1 + 1
                        del cs_top[i : i + 2]
                else:
                    if i == len(cs_top) - 1 or c2 < cs_top[i + 1]:
                        # Case C
                        # *--*
                        # |..|
                        # |..*--*
                        # :.....:
                        # Added cells will be counted with the widened strip.
                        cs_top[i] = c2
                    else:
                        assert c2 == cs_top[i + 1]
                        # Case D
                        # *--*  *--*
                        # |..|  |..|
                        # |..*--*..|
                        # :........:
                        cs_top.pop(i)
                        cs_top.pop(i)
            elif (i := find(cs_top, c2)) >= 0:
                if i % 2 == 0:
                    if i > 0:
                        assert cs_top[i - 1] < c1
                        # or else it would have been caught by Case D.

                    # Case E:
                    #    *--*
                    #    |..|
                    # *--*..|
                    # :.....:
                    cs_top[i] = c1
                else:
                    c_top1 = cs_top[i - 1]
                    assert c_top1 < c1
                    # or else it would have been caught by Case D.

                    # Case F:
                    # *-----*
                    # |.....|
                    # |..*--*
                    # :..:
                    area += c2 - c1
                    cs_top[i] = c1
            else:
                i = bisect.bisect(cs_top, c1)
                if i < len(cs_top):
                    assert c2 < cs_top[i]

                if i % 2 == 1:
                    # Case G:
                    # A strip is being split into two.
                    # *--------*
                    # |........|
                    # |..*--*..|
                    # :..:  :..:
                    area += c2 - c1 - 1
                    cs_top[i:i] = [c1, c2]
                else:
                    # Case H:
                    # New strip
                    cs_top[i:i] = [c1, c2]

        r_top = r

    if cs_top:
        breakpoint()
    assert not cs_top

    print("Part 2:", area)

def batched(p, n):
    b = []
    try:
        for x in p:
            b.append(x)
            if len(b) == n:
                yield b
                b = []
    except StopIteration:
        if b:
            yield b

def find(s, x):
    try:
        return s.index(x)
    except ValueError:
        return -1

main()

# multitime -n 5 ; median:
# cpython: 0.139s
# pypy:    0.206s
