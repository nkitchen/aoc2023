#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

DEBUG = os.environ.get("DEBUG")

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    grid = [list(line.rstrip()) for line in fileinput.input()]

    roll_north(grid)

    print("Part 1:", total_load(grid))

    roll_north(grid)
    roll_west(grid)
    roll_south(grid)
    roll_east(grid)

    sig_to_time = {signature(grid): 1}
    time_to_load = {1: total_load(grid)}

    t = 1
    period = None
    while True:
        roll_north(grid)
        roll_west(grid)
        roll_south(grid)
        roll_east(grid)
        t += 1

        s = signature(grid)
        time_to_load[t] = total_load(grid)

        if s in sig_to_time:
            period = t - sig_to_time[s]
            break
        else:
            sig_to_time[s] = t

    all_cycles = 1000000000
    k = (all_cycles - t) // period
    dt = all_cycles - (t + k * period)
    t += dt - period
    print("Part 2:", time_to_load[t])

def roll_north(grid):
    m = len(grid)
    n = len(grid[0])
    for j in range(n):
        start = 0
        while start < m:
            rock = None
            for i in range(start, m):
                if grid[i][j] == 'O':
                    rock = i
                    break

            if rock is None:
                break
            start = rock + 1
            while rock > 0 and grid[rock - 1][j] == '.':
                rock -= 1
                grid[rock][j] = 'O'
                grid[rock + 1][j] = '.'

def roll_south(grid):
    grid.reverse()
    roll_north(grid)
    grid.reverse()

def roll_west(grid):
    m = len(grid)
    n = len(grid[0])
    for i in range(m):
        start = 0
        while start < n:
            rock = None
            for j in range(start, n):
                if grid[i][j] == 'O':
                    rock = j
                    break

            if rock is None:
                break
            start = rock + 1
            while rock > 0 and grid[i][rock - 1] == '.':
                rock -= 1
                grid[i][rock] = 'O'
                grid[i][rock + 1] = '.'

def roll_east(grid):
    m = len(grid)
    n = len(grid[0])
    for i in range(m):
        start = n - 1
        while start >= 0:
            rock = None
            for j in range(start, -1, -1):
                if grid[i][j] == 'O':
                    rock = j
                    break

            if rock is None:
                break
            start = rock - 1
            while rock < n - 1 and grid[i][rock + 1] == '.':
                rock += 1
                grid[i][rock] = 'O'
                grid[i][rock - 1] = '.'

def signature(grid):
    m = len(grid)
    n = len(grid[0])
    sig = 0
    for i in range(m):
        for j in range(n):
            sig <<= 1
            if grid[i][j] == 'O':
                sig += 1
    return sig

def total_load(grid):
    m = len(grid)
    n = len(grid[0])
    load = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 'O':
                load += m - i

    return load

def show(grid):
    for row in grid:
        print(''.join(row))
    print()

main()

# multitime -n 5 ; median:
# cpython: 2.135s
# pypy:    0.579s
