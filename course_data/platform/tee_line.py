"""The tee line rule (ARCHITECTURE.md 9.1-8), shared by platform/package.py (reframe) and product/package.py.

The tee line runs from the tee to the point on the hole's line of play LANDING (250) yds from the tee,
measured along the line (at most SHORT_CAP = 62% of the hole on short holes); par 3s aim at the green.
Distance is measured from the tee to its nearest point on the hole line, then along the line (the green
centre is its last point). Without a usable hole line (none, or the tee more than MAX_OFF_LINE yds from it)
the line points at the green.

Pure numpy, no frames: local equirectangular yards about the tee (error < 0.1% inside a hole).
"""
import math

import numpy as np

LANDING = 250.0
SHORT_CAP = 0.62
MAX_OFF_LINE = 60.0
RULE = f"tee -> hole line {LANDING:.0f} yds along (<= {SHORT_CAP:.0%} of the hole); par 3: green"


def _k(lat):
    lat0 = math.radians(lat)
    return np.array([math.cos(lat0) * 111320 / 0.9144, 111320 / 0.9144])


def aim_point(tee_ll, line_ll, green_ll, length=None, par=None):
    """-> ([lon, lat], how) with how in 'green' (par 3), 'landing' (rule above), 'green_dir' (no usable line:
    the green direction, LANDING yds out)."""
    tee = np.asarray(tee_ll[:2], float)
    green = np.asarray(green_ll[:2], float)
    if par is not None and int(par) == 3:
        return [float(green[0]), float(green[1])], "green"
    k = _k(tee[1])
    g = (green - tee) * k
    want = None
    if line_ll is not None and len(line_ll) >= 2:
        P = (np.array([p[:2] for p in line_ll] + [list(green)], float) - tee) * k
        best = None
        for i in range(len(P) - 1):                         # the tee's nearest point on the polyline
            a, b = P[i], P[i + 1]
            d = b - a
            u = float(np.clip(-(a @ d) / max(float(d @ d), 1e-9), 0, 1))
            dist = float(np.linalg.norm(a + u * d))
            if best is None or dist < best[0]:
                best = (dist, i, u)
        if best[0] <= MAX_OFF_LINE:
            _, i, u = best
            pts = [P[i] + u * (P[i + 1] - P[i])] + list(P[i + 1:])
            segs = [float(np.linalg.norm(b - a)) for a, b in zip(pts[:-1], pts[1:])]
            run = float(np.linalg.norm(pts[0]))             # tee -> line offset counts toward the distance
            total = run + sum(segs)
            want = min(LANDING, SHORT_CAP * float(length or total))
            for (a, b), seg in zip(zip(pts[:-1], pts[1:]), segs):
                if run + seg >= want and seg > 0:
                    q = a + (b - a) * (want - run) / seg
                    return [float(tee[0] + q[0] / k[0]), float(tee[1] + q[1] / k[1])], "landing"
                run += seg
            return [float(green[0]), float(green[1])], "landing"   # line shorter than want: the green
    dg = float(np.linalg.norm(g))
    if dg < 1e-6:
        return [float(green[0]), float(green[1])], "green_dir"
    want = min(LANDING, SHORT_CAP * float(length or dg))
    q = g / dg * want
    return [float(tee[0] + q[0] / k[0]), float(tee[1] + q[1] / k[1])], "green_dir"
