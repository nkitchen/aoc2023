#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

from collections import defaultdict


DEBUG = os.environ.get("DEBUG", "")

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    adj = defaultdict(set)

    for line in fileinput.input():
        u, vs = line.split(':')
        for v in vs.split():
            adj[u].add(v)
            adj[v].add(u)

    if (graph_file := os.environ.get("GRAPH")):
        with open(graph_file, "w") as f:
            def gpr(s):
                print(s, file=f)

            gpr("graph {")
            for u in adj:
                for v in adj[u]:
                    if u < v:
                        gpr(f"  {u} -- {v};")
            gpr("}")

    # Observed structure: It looks like any edge that we're *not* supposed to cut
    # is part of a triangle: If the edge is (u, v), then there is a w such that
    # (u, w) and (v, w) are also in the graph.

    # But some edges aren't in triangles, and also aren't in the min cut.
    # Try: Use the triangle edges to find connected components.

    triangle_edges = set()
    for u in adj:
        for v in adj[u]:
            if u > v:
                continue

            s = (adj[u] - {v}) & (adj[v] - {u})
            for w in s:
                triangle_edges.add((u, v))
                triangle_edges.add(tuple(sorted([v, w])))
                triangle_edges.add(tuple(sorted([u, w])))

    rep = {}
    def _lookup_rep(v):
        r = rep.get(v, v)
        if r != v:
            rep[v] = r = _lookup_rep(r)
        return r

    def _join(v1, v2):
        r1 = _lookup_rep(v1)
        r2 = _lookup_rep(v2)
        if r1 != r2:
            r1, r2 = (min(r1, r2), max(r1, r2))
            rep[r2] = r1

    for u, v in triangle_edges:
        _join(u, v)

    comps = defaultdict(set)
    for u in adj:
        r = _lookup_rep(u)
        comps[r].add(u)

    print(len(comps))
    for c in comps.values():
        print(len(c))

main()

# multitime -n 5 ; median:
# cpython: 0.999s
# pypy:    Didn't try
