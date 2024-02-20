#!/usr/bin/env python3

import fileinput
import re
from collections import defaultdict, namedtuple

Card = namedtuple('Card', 'winning have')

input_lines = list(line.rstrip() for line in fileinput.input())
cards = []
for line in input_lines:
    i = line.index(':')
    ws, hs = line[i:].split('|')
    winning = set(ws.split())
    have = set(hs.split())
    cards.append(Card(winning, have))

points = 0

for card in cards:
    matching = card.winning & card.have
    if not matching:
        continue
    n = len(matching)
    points += 1 << (n - 1)

print("Part 1:", points)

total_cards = defaultdict(int)
for i, card in enumerate(cards):
    total_cards[i] += 1
    n = len(card.winning & card.have)
    k = total_cards[i]
    for d in range(1, n + 1):
        j = i + d
        total_cards[j] += k

print("Part 2:", sum(total_cards.values()))

# multitime -n 5 ; median:
# cpython: 0.034s
# pypy:    0.070s
