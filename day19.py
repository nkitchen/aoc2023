#!/usr/bin/env python3

import fileinput
import os
from pprint import pprint

import operator
import re
from collections import namedtuple
from functools import reduce

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args):
    if DEBUG:
        print(*args)

Rule = namedtuple('Rule', 'var rel rhs dest')

def main():
    lines = [line.rstrip() for line in fileinput.input()]

    i = lines.index('')
    workflow_lines = lines[:i]
    part_lines = lines[i + 1:]

    workflows = {}
    for line in workflow_lines:
        if not line:
            break

        i = line.index('{')
        name = line[:i]
        assert line[-1] == '}'
        rules = []
        segs = line[i + 1 : -1].split(',')
        for seg in segs:
            m = re.match(r"(?P<var>[xmas])(?P<rel>[<>])(?P<rhs>\d+):(?P<dest>\w+)", seg)
            if m:
                g = m.groupdict()
                g['rhs'] = int(g['rhs'])
                rule = Rule(**g)
                rules.append(rule)
            else:
                assert re.match(r"\w+$", seg)
                rules.append(Rule(var=None, rel=None, rhs=None, dest=seg))

        workflows[name] = rules

    parts = []
    for line in part_lines:
        part = {}
        for m in re.finditer(r"(?P<var>[xmas])=(?P<val>-?\d+)", line):
            part[m.group('var')] = int(m.group('val'))
        parts.append(part)

    op = {
        '<': operator.lt,
        '>': operator.gt,
    }
    def _accepted(part):
        flow = workflows['in']
        while True:
            dest = None
            for rule in flow:
                if rule.var is None or op[rule.rel](part[rule.var], rule.rhs):
                    dest = rule.dest
                    break

            assert dest is not None
            if dest == 'A':
                return True
            elif dest == 'R':
                return False
            else:
                flow = workflows[dest]

    total_rating = 0
    for part in parts:
        if _accepted(part):
            total_rating += sum(part.values())
    print("Part 1:", total_rating)

    if (graph_file := os.environ.get("GRAPH")):
        write_dot(workflows, graph_file)

    def _accepted_ranges(flow_name, pr):
        if flow_name == 'A':
            yield pr
            return
        elif flow_name == 'R':
            return

        flow = workflows[flow_name]
        for rule in flow:
            if rule.var is None:
                yield from _accepted_ranges(rule.dest, pr)
                return

            pr2 = pr.copy()
            if rule.rel == '<':
                pr2[rule.var] = range(pr[rule.var].start, rule.rhs)
                yield from _accepted_ranges(rule.dest, pr2)
                pr[rule.var] = range(rule.rhs, pr[rule.var].stop)
            else:
                assert rule.rel == '>'
                pr2[rule.var] = range(rule.rhs + 1, pr[rule.var].stop)
                yield from _accepted_ranges(rule.dest, pr2)
                pr[rule.var] = range(pr[rule.var].start, rule.rhs + 1)

        assert False

    full_range = range(1, 4001)
    fpr = {var: full_range for var in 'xmas'}
    combos = 0
    for pr in _accepted_ranges('in', fpr):
        combos += reduce(operator.mul, (len(r) for r in pr.values()))
    print("Part 2:", combos)


def write_dot(workflows, graph_file):
    with open(graph_file, "w") as f:
        f.write("digraph {\n")
        f.write("node [shape=record];\n")
        for name, flow in workflows.items():
            f.write(f'{name} [label="' + '{' + name)
            for i, rule in enumerate(flow):
                f.write('|')
                if rule.var:
                    if rule.rel == '>':
                        rel = '&gt;'
                    else:
                        rel = '&lt;'
                    f.write(f'<r{i}> {rule.var}{rel}{rule.rhs}')
                else:
                    f.write(f'<r{i}> else')
            f.write('}"];\n')

            for i, rule in enumerate(flow):
                if rule.dest in "AR":
                    f.write(f'{name}:r{i} -> {rule.dest};\n')
                else:
                    f.write(f'{name}:r{i} -> {rule.dest}:r0;\n')
        f.write('}\n')

main()

# multitime -n 5 ; median:
# cpython: 0.062s
# pypy:    0.139s
