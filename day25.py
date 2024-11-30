#!/usr/bin/env python3

import fileinput
import os
import sys
from pprint import pprint

from collections import defaultdict
import random

import networkx as nx

DEBUG = os.environ.get("DEBUG", "")

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    graph = nx.Graph()

    for line in fileinput.input():
        u, vs = line.split(':')
        for v in vs.split():
            graph.add_edge(u, v)

    _ = """
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
    """

    nodes = list(graph)

    while True:
        u, v = random.sample(nodes, 2)
        cutset = nx.minimum_edge_cut(graph, u, v)
        dprint(f"Cut: {len(cutset)}")
        if len(cutset) == 3:
            break

    for u, v in cutset:
        graph.remove_edge(u, v)

    comp_sizes = [len(comp) for comp in nx.connected_components(graph)]
    assert len(comp_sizes) == 2
    p = comp_sizes[0] * comp_sizes[1]
    print("Part 1:", p)
    
main()

# multitime -n 5 ; median:
# cpython: 0.487s
# pypy:    0.885s
