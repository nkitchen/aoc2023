#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import math
from collections import defaultdict
from functools import reduce

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args, debug=1):
    if DEBUG >= debug:
        print(*args)

def main():
    outputs = {}
    conj_inputs = defaultdict(list)
    flop_states = {}

    for line in fileinput.input():
        line = line.rstrip()
        module, out_str = line.split(" -> ")
        if module[0] == "%":
            module = module[1:]
            flop_states[module] = 0
        elif module[0] == "&":
            module = module[1:]
            conj_inputs[module] = {}

        outputs[module] = out_str.split(", ")

    for src in outputs:
        for dst in outputs[src]:
            if dst in conj_inputs:
                conj_inputs[dst][src] = 0

    if (graph_file := os.environ.get("GRAPH")):
        with open(graph_file, "w") as f:
            def gprint(*args):
                print(*args, file=f)

            gprint("digraph {")
            gprint("node [shape=doublecircle];")
            for v in flop_states:
                gprint(f"{v} [shape=rect];")
            for v in conj_inputs:
                gprint(f"{v} [shape=circle];")
            for u in outputs:
                for v in outputs[u]:
                    gprint(f"{u} -> {v};")
            gprint("}")

    # Find flip-flop chains.
    flop_succ = {}
    for u in outputs:
        if u not in flop_states:
            continue
        for v in outputs[u]:
            if v in flop_states:
                flop_succ[u] = v
    flop_heads = outputs['broadcaster']

    chains = {}
    for u in flop_heads:
        ch = []
        v = u
        while v:
            ch.append(v)
            v = flop_succ.get(v)
        chains[u] = ch

    chain_conj = {
        'fb': 'bz',
        'vj': 'jj',
        'gr': 'xz',
        'xk': 'gf',
    }
    chain_period = {}
    for head, conj in chain_conj.items():
        p = 0
        assert chains[head][0] == head
        # Connectivity of chains to their conjunctions give their periods in binary.
        for i, v in enumerate(chains[head]):
            if v in conj_inputs[conj]:
                p ^= 1 << i
        chain_period[head] = p

    class Executor():
        def __init__(self):
            self.pulse_counts = defaultdict(int)
            self.chain_state = {}

        def press(self):
            self.tracked_pulses = defaultdict(list)

            pulse_str = ['low', 'high']
            pulse_queue = [('button', 'broadcaster', 0)]
            while pulse_queue:
                u, v, p = pulse_queue.pop(0)
                dprint(f"{u} -{pulse_str[p]}-> {v}", debug=2)
                self.pulse_counts[p] += 1

                if v == 'broadcaster':
                    for w in outputs[v]:
                        pulse_queue.append((v, w, p))
                elif v in flop_states and p == 0:
                    flop_states[v] ^= 1
                    for w in outputs[v]:
                        pulse_queue.append((v, w, flop_states[v]))
                elif v in conj_inputs:
                    conj_inputs[v][u] = p
                    if all(conj_inputs[v].values()):
                        q = 0
                    else:
                        q = 1
                    for w in outputs[v]:
                        pulse_queue.append((v, w, q))

                if v == 'rx':
                    self.tracked_pulses[v].append((u, v, p))

                if u in chain_conj.values():
                    self.tracked_pulses[u].append((u, v, p))


            for u, ch in chains.items():
                s = 0 
                for i, v in enumerate(ch):
                    s |= flop_states[v] << i
                self.chain_state[u] = s

    ex = Executor()
    for t in range(1000):
        ex.press()
    r = ex.pulse_counts[0] * ex.pulse_counts[1]
    print("Part 1:", r)

    for v in flop_states:
        flop_states[v] = 0
    for v in conj_inputs:
        for u in conj_inputs[v]:
            conj_inputs[v][u] = 0

    # Verify chain periods and conjunction pulses.
    ex = Executor()
    t = 0
    for t in range(1 << 12):
        t += 1
        ex.press()

        for head, period in chain_period.items():
            if t == period:
                assert ex.chain_state[head] == 0
                v = chain_conj[head]
                trigger = any((p == 0 for _, _, p in ex.tracked_pulses[v]))
                assert trigger
                print(f"Verified chain {head}")

        #dat = [ex.chain_state[v] for v in flop_heads]
        #triggers = []
        #for u, v in chain_conj.items():
        #    if any((p == 0 for _, _, p in ex.tracked_pulses[v])):
        #        triggers.append("0")
        #    else:
        #        triggers.append("-")
        #print(t, *dat, "".join(triggers), sep='\t')

    def _lcm(x, y):
        return x * y // math.gcd(x, y)

    combined_period = reduce(_lcm, chain_period.values())
    print("Part 2:", combined_period)

main()

# multitime -n 5 ; median:
# cpython: 0.358s
# pypy:    0.237s
