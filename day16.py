#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

DEBUG = os.environ.get("DEBUG")

def dprint(*args):
    if DEBUG:
        print(*args)

NONE = 0
NORTH = 1
SOUTH = 2
EAST = 4
WEST = 8

dir_del = {
    NORTH: (-1, 0),
    SOUTH: (1, 0),
    EAST: (0, 1),
    WEST: (0, -1),
}

out_dirs = {
    (NORTH, '/'): (EAST, NONE),
    (NORTH, '\\'): (WEST, NONE),
    (NORTH, '-'): (WEST, EAST),
    (SOUTH, '/'): (WEST, NONE),
    (SOUTH, '\\'): (EAST, NONE),
    (SOUTH, '-'): (WEST, EAST),
    (WEST, '/'): (SOUTH, NONE),
    (WEST, '\\'): (NORTH, NONE),
    (WEST, '|'): (NORTH, SOUTH),
    (EAST, '/'): (NORTH, NONE),
    (EAST, '\\'): (SOUTH, NONE),
    (EAST, '|'): (NORTH, SOUTH),
}

def main():
    grid = [list(line.rstrip()) for line in fileinput.input()]
    m = len(grid)
    n = len(grid[0])

    def _energized_tiles(i_start, j_start, dir_start):
        beam = {}
        q = [(i_start, j_start, dir_start)]
        while q:
            i, j, dir = q[0]
            q = q[1:]

            if (b := beam.get((i, j), NONE)) & dir:
                continue

            beam[(i, j)] = b | dir

            ddir1, ddir2 = out_dirs.get((dir, grid[i][j]), (dir, NONE))

            assert ddir1 != NONE
            di, dj = dir_del[ddir1]
            ii = i + di
            jj = j + dj
            if (0 <= ii < m) and (0 <= jj < n):
                q.append((ii, jj, ddir1))

            if ddir2 != NONE:
                di, dj = dir_del[ddir2]
                ii = i + di
                jj = j + dj
                if (0 <= ii < m) and (0 <= jj < n):
                    q.append((ii, jj, ddir2))
        return len(beam)

    print("Part 1:", _energized_tiles(0, 0, EAST))

    def _starts():
        for j in range(n):
            yield (0, j, SOUTH)
            yield (m - 1, j, NORTH)

        for i in range(m):
            yield(i, 0, EAST)
            yield(i, n - 1, WEST)

    m = max(_energized_tiles(*start) for start in _starts())
    print("Part 2:", m)
        
main()

# multitime -n 5 ; median:
# cpython: 3.783s
# pypy:    1.258s
