#!/usr/bin/env python3

import fileinput
import re

def calibration_value1(s: str) -> int:
    def _first_digit(t: str) -> str:
        if (m := re.search(r"\d", t)):
            return m.group(0)
        else:
            return "?"

    a = _first_digit(s)
    b = _first_digit(s[::-1])
    try:
        return int(a + b)
    except ValueError:
        return 0

word_value = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}

def calibration_value2(s: str) -> int:
    digit_re = re.compile(r"\d|one|two|three|four|five|six|seven|eight|nine")

    m = digit_re.search(s)
    first = m.group(0)
    a = word_value.get(first) or int(first)

    last = first
    i = m.start()
    while (m := digit_re.search(s, i + 1)):
        last = m.group()
        i = m.start()

    b = word_value.get(last) or int(last)
    return 10 * a + b

# Slower than the re-based one
def calibration_value_isdigit(s: str) -> int:
    a = b = "?"
    for c in s:
        if c.isdigit():
            a = c
            break
    for c in reversed(s):
        if c.isdigit():
            b = c

    return int(a + b)

lines = list(fileinput.input())

total1 = sum(calibration_value1(line) for line in lines)
print(total1)

total2 = sum(calibration_value2(line) for line in lines)
print(total2)

# multitime -n 5 ; median:
# cpython: 0.040s
# pypy:    0.099s
