#!/usr/bin/env python3

import os
import sys
from pprint import pprint

import numpy as np
import numpy.linalg
from collections import defaultdict

import sympy

DEBUG = int(os.environ.get("DEBUG", "0"))

def dprint(*args):
    if DEBUG:
        print(*args)

def main():
    inp = open(sys.argv[1])
    isect_min = int(sys.argv[2])
    isect_max = int(sys.argv[3])

    pos = []
    vel = []
    for line in inp:
        posStr, velStr = line.split("@")
        p = np.array([int(x) for x in posStr.split(", ")])
        v = np.array([int(x) for x in velStr.split(", ")])
        pos.append(p)
        vel.append(v)

        assert (-999 <= v).all()
        assert (v <= 999).all()

    pos = np.array(pos)
    vel = np.array(vel)

    # p1x + v1x * t1 = p2x + v2x * t2
    # p1y + v1y * t1 = p2y + v2y * t2
    #
    # v1x * t1 - v2x * t2 = p2x - p1x
    # v1y * t1 - v2y * t2 = p2y - p1y

    crossed_paths = 0

    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            m = np.array([[vel[i][0], -vel[j][0]],
                          [vel[i][1], -vel[j][1]]])
            b = np.array([pos[j][0] - pos[i][0],
                          pos[j][1] - pos[i][1]])

            try:
                t = numpy.linalg.solve(m, b)
            except numpy.linalg.LinAlgError:
                continue

            if t[0] < 0 or t[1] < 0:
                continue

            cross = pos[i] + vel[i] * t[0]
            if (isect_min <= cross[0] <= isect_max and
                isect_min <= cross[1] <= isect_max):
                crossed_paths += 1

    print("Part 1:", crossed_paths)

    # Let pRx, pRy, pRz be the initial position of the rocks,
    # and vRx, vRy, vRz be the velocity.
    # (Capital R for visibility of these unknowns in the equations that follow)
    #
    # Hailstone i has a collision time of ti.
    # pix + vix * ti = pRx + vRx * ti
    # piy + viy * ti = pRy + vRy * ti
    # piz + viz * ti = pRz + vRz * ti
    #
    # Solve for ti:
    # ti = (pRx - pix) / (vix - vRx)
    #    = (pRy - piy) / (viy - vRy)
    #    = (pRz - piz) / (viz - vRz)
    #
    # Cross-multiply:
    #    pRx * viy - pRx * vRy - pix * viy + pix * vRy
    #  = pRy * vix - pRy * vRx - piy * vix + piy * vRx
    #
    # Isolate the non-linear terms:
    # pRx * vRy - pRy * vRx
    #  = viy * pRx - vix * pRy - piy * vRx + pix * vRy - pix * viy + piy * vix
    # The LHS of this doesn't depend on i, so I can set the RHS equal to the
    # corresponding terms for another hailstone j.
    #
    # (viy - vjy) * pRx + (vjx - vix) * pRy + (pjy - piy) * vRx + (pix - pjx) * vRy
    #  = pix * viy - piy * vix - pjx * vjy + pjy * vjx
    #
    # Likewise for y, z and x, z ==> 3 equations (or only 2?)
    #
    # With 3 hailstones, I can get 6 combinations of i and j.
    # ==> 6 unknowns, 9 equations
    # It looks overdetermined, but it shouldn't be.

    m = []
    b = []

    # Hailstone indices
    for i, j in [
        (0, 1),
        (1, 2),
        (2, 3),
        #(3, 4),
        #(4, 5),
        #(6, 5),
    ]:
        pi = pos[i]
        pj = pos[j]
        vi = vel[i]
        vj = vel[j]

        # Dimension indices
        for d, e in [
            (0, 1),
            (1, 2),
        ]:
            a = np.zeros((6,), dtype=int)
            a[d] = vi[e] - vj[e] # pRd
            a[e] = vj[d] - vi[d] # pRe
            a[d + 3] = pj[e] - pi[e] # vRd
            a[e + 3] = pi[d] - pj[d] # vRe
            m.append(a)
            b.append(pi[d] * vi[e] - pi[e] * vi[d] - pj[d] * vj[e] + pj[e] * vj[d])

    m = np.array(m, dtype=int)
    b = np.array(b, dtype=int)

    # Numpy has problems with precision when solving this.
    #s = numpy.linalg.solve(m, b)

    M = sympy.Matrix(m.astype(int))
    B = sympy.Matrix(b.astype(int))
    s = M.LUsolve(B)

    pos_sum = sum(int(x) for x in s[:3])
    print("Part 2:", pos_sum)

main()

# multitime -n 5 ; median:
# cpython: 1.193s
# pypy:    5.311s
