#!/usr/bin/env python3

from collections import Counter
from enum import IntEnum, auto
import fileinput
from pprint import pprint

def main():
    hands = [line.split() for line in fileinput.input()]

    hands.sort(key=lambda h: strength(h[0]))

    winnings = 0
    for i, (hand, bid) in enumerate(hands):
        rank = i + 1
        winnings += rank * int(bid)

    print("Part 1:", winnings)

    hands.sort(key=lambda h: strength_with_wilds(h[0]))
    winnings = 0
    for i, (hand, bid) in enumerate(hands):
        rank = i + 1
        winnings += rank * int(bid)
    print("Part 2:", winnings)

class HandType(IntEnum):
    HIGH_CARD = auto()
    ONE_PAIR = auto()
    TWO_PAIR = auto()
    THREE_KIND = auto()
    FULL_HOUSE = auto()
    FOUR_KIND = auto()
    FIVE_KIND = auto()

type_table = {
    (5,): HandType.FIVE_KIND,
    (1, 4): HandType.FOUR_KIND,
    (2, 3): HandType.FULL_HOUSE,
    (1, 1, 3): HandType.THREE_KIND,
    (1, 2, 2): HandType.TWO_PAIR,
    (1, 1, 1, 2): HandType.ONE_PAIR,
    (1, 1, 1, 1, 1): HandType.HIGH_CARD,
}

card_order = "23456789TJQKA"

def strength(hand):
    s = [classify(hand)]
    s.extend(card_order.index(c) for c in hand)
    return s

def classify(hand):
    c = Counter(iter(hand))
    return type_table[tuple(sorted(c.values()))]

card_order_with_wilds = "J23456789TQKA"

def strength_with_wilds(hand):
    s = [classify_wildly(hand)]
    s.extend(card_order_with_wilds.index(c) for c in hand)
    return s

def classify_wildly(hand):
    c = Counter(iter(hand))
    jokers = c['J']
    if jokers == 5:
        return HandType.FIVE_KIND
    if jokers == 0:
        return type_table[tuple(sorted(c.values()))]

    del c['J']

    match max(c.values()) + jokers:
        case 5:
            return HandType.FIVE_KIND
        case 4:
            return HandType.FOUR_KIND
        case 3:
            # jokers <= 2, or else the case would be 4.
            match [jokers, sorted(c.values())]:
                case [2, [1, 1, 1]]:
                    return HandType.THREE_KIND
                case [1, [2, 2]]:
                    return HandType.FULL_HOUSE
                case [1, [1, 1, 2]]:
                    return HandType.THREE_KIND
        case 2:
            # 1 J, 1, 1, 1, 1
            return HandType.ONE_PAIR

    assert False, "unreachable"

main()

# multitime -n 5 ; median:
# cpython: 0.064s
# pypy:    0.087s
