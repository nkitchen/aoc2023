#!/usr/bin/env python3

import fileinput
import re
from collections import defaultdict, namedtuple
from pprint import pprint

MapRange = namedtuple('MapRange', 'dest_start src_start len')

class ProdMap():
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.ranges = []

    def lookup_dest(self, src):
        for r in self.ranges:
            i = src - r.src_start
            if 0 <= i < r.len:
                return r.dest_start + i
        return src

    def lookup_dest_ranges(self, src_range):
        ds = []

        for r in self.ranges:
            a = r.src_start
            b = r.src_start + r.len
            if src_range.start < a:
                if src_range.stop <= a:
                    # All before this range in the map
                    ds.append(src_range)
                    src_range = None
                    break

                ds.append(range(src_range.start, a))
                src_range = range(a, src_range.stop)

            if src_range.start < b:
                c = src_range.start - a + r.dest_start
                if src_range.stop <= b:
                    # All within this range in the map
                    d = c + len(src_range)
                    ds.append(range(c, d))
                    src_range = None
                    break
                else:
                    d = b - a + r.dest_start
                    ds.append(range(c, d))
                    src_range = range(b, src_range.stop)

        if src_range is not None:
            ds.append(src_range)

        return ds

full_input = "".join(line for line in fileinput.input())

prod_map_by_src = {}

for section in full_input.split("\n\n"):
    i = section.index(":")
    if section[:i] == "seeds":
        seeds = [int(x) for x in section[i + 1:].split()]
    else:
        m = re.search(r"(\w+)-to-(\w+) map", section)
        assert m
        src = m.group(1)
        dest = m.group(2)
        pmap = ProdMap(src, dest)
        for line in section[i + 2:].split("\n"):
            if not line:
                continue
            dest_start, src_start, ln = map(int, line.split())
            rg = MapRange(dest_start, src_start, ln)
            pmap.ranges.append(rg)
        pmap.ranges.sort(key=lambda r: r.src_start)
        prod_map_by_src[src] = pmap

def rec_lookup(seed):
    src_category = "seed"
    x = seed
    while (pmap := prod_map_by_src.get(src_category)):
        x = pmap.lookup_dest(x)
        src_category = pmap.dest
    return x

print("Part 1:", min(rec_lookup(seed) for seed in seeds))

def rec_lookup_ranges(seed_ranges):
    src_category = "seed"
    rs = seed_ranges
    while (pmap := prod_map_by_src.get(src_category)):
        ds = []
        for r in rs:
            ds.extend(pmap.lookup_dest_ranges(r))
        rs = ds
        src_category = pmap.dest
    return rs

seed_ranges = []
for i in range(0, len(seeds), 2):
    seed_ranges.append(range(seeds[i], seeds[i] + seeds[i + 1]))
    seed_ranges.sort(key=lambda r: r.start)

soil_ranges = rec_lookup_ranges(seed_ranges)
loc = min(r.start for r in soil_ranges)
print("Part 2:", loc)

# multitime -n 5 ; median:
# cpython: 0.045s
# pypy:    0.105s
