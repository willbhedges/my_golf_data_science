"""tee_strategy.simulate with its roll-out loop in C (fastc/perception kernel.c fp_roll), for the fast-path solve.

solve.py's lie raster (raster_lie_at) makes every lie lookup a cell read; what is left of the solve's time is the
roll-out: a Python while-loop of 2-yd steps over all moving balls, each step a raster lookup. fp_roll runs each
ball's loop in C with the same arithmetic in the same order, so simulate_c returns exactly what simulate returns
(test_solve_c.py: every hole x club x aim of two built courses, identical arrays). The landing draw and the
strokes table stay numpy: this file repeats tee_strategy.simulate's code around the loop (keep it in step).

    import solve_c; solve_c.install()        # after solve.use_raster(); tee_strategy.simulate -> simulate_c
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "fastc", "perception"))


def _sv():
    """the module whose raster_lie_at is installed (solve.py runs as __main__ in the fast path)"""
    import tee_strategy as t
    return sys.modules[t.lie_at.__module__]


def _raster(t, h):
    SV = _sv()
    SV.raster_lie_at(h, np.zeros((1, 2)))                 # builds / caches the hole's label raster
    _, lo, lab, names = SV._RASTER[id(h["zones"])]
    return lo, lab, list(names)


def simulate_c(hole_no, club, aim_lat=0.0, n=None, z=None):
    import ctypes
    import fastperc
    import tee_strategy as t
    SV = _sv()
    n = t.N_SHOTS if n is None else n
    h = t.HOLES[hole_no]
    tee, fwd, right, ppy = t.hole_frame(h)
    carry, total, width, depth = {**t.CLUBS, **t.IRONS}[club]
    roll0 = total - carry
    kick = 0.0
    elev = h.get("elev", {}).get(club) if t.USE_ELEVATION else None
    if elev:
        carry = carry + elev[0]
        roll0 = roll0 * elev[1]
        kick = elev[2]
    if z is None:
        z = t.Z if n == t.N_SHOTS else np.vstack([t.RNG.standard_normal((2, n)), t.RNG.random((2, n))])
    n = z.shape[1]
    z_lat = z[1]
    if t.TAIL_NU:
        chi = t.CHI if (z is t.Z and t.CHI is not None) else t._chi_for(z, t.TAIL_NU)
        z_lat = z[1] / np.sqrt(chi) * (1.959964 / t.T975[t.TAIL_NU])
    z_car = z[0]
    if t.RHO:
        z_car = -t.RHO * z_lat + np.sqrt(1 - t.RHO ** 2) * z[0]
    along = carry + depth / 4 * z_car
    mishit = z[2] < t.MISHIT_RATE.get(club, 0.0)
    lo_, hi_ = t.MISHIT_CARRY
    along[mishit] = carry * (lo_ + (hi_ - lo_) * z[3][mishit])
    lat = aim_lat + width / 4 * z_lat
    pts = tee + (along[:, None] * fwd + lat[:, None] * right) * ppy
    lo, lab, names = _raster(t, h)
    lie_id = np.zeros(n, np.int32)
    ok = None
    # the landing lie, as raster_lie_at reads it
    c = np.round((pts[:, 0] - lo[0]) * SV.RASTER_SCALE).astype(np.int64)
    r = np.round((pts[:, 1] - lo[1]) * SV.RASTER_SCALE).astype(np.int64)
    ok = (c >= 0) & (r >= 0) & (c < lab.shape[1]) & (r < lab.shape[0])
    lie_id[ok] = lab[r[ok], c[ok]]
    heading = (pts - tee) / np.linalg.norm(pts - tee, axis=1)[:, None]
    roll_total = float(roll0 + h.get("extra_roll", 0))
    if kick and roll_total > 0:
        heading = heading * roll_total + right[None, :] * kick
        heading = heading / np.linalg.norm(heading, axis=1)[:, None]
        roll_total = float(np.hypot(roll_total, kick))
    roll_left = np.full(n, roll_total)
    rough = names.index("rough")
    roll_left[lie_id == rough] *= t.ROUGH_ROLL
    hazard = np.array([nm in t.HAZARDS for nm in names] + [False] * (256 - len(names)), np.uint8)
    fair = names.index("fairway") if "fairway" in names else -1
    pts = np.ascontiguousarray(pts, np.float64)
    heading = np.ascontiguousarray(heading, np.float64)
    lab_c = np.ascontiguousarray(lab, np.uint8)
    P = fastperc._p
    fastperc.lib().fp_roll(P(pts), P(heading), P(roll_left), P(lie_id), n, ctypes.c_double(ppy), P(lab_c),
                           lab_c.shape[0], lab_c.shape[1], ctypes.c_double(lo[0]), ctypes.c_double(lo[1]),
                           ctypes.c_double(SV.RASTER_SCALE), P(hazard), fair, rough, ctypes.c_double(t.ROUGH_ROLL))
    lie = np.array(names, dtype=object)[lie_id]
    to_green = np.linalg.norm(pts - np.array(h["green"], float), axis=1) / ppy
    strokes = np.empty(n)
    for name in set(lie):
        m = lie == name
        strokes[m] = t.expected_strokes(name, to_green[m])
    return pts, lie, to_green, 1.0 + strokes


def install():
    """tee_strategy.simulate -> simulate_c (needs solve.use_raster() first; GOLF_FASTC=0 keeps the numpy loop)."""
    import tee_strategy as t
    if os.environ.get("GOLF_FASTC", "1") == "0" or getattr(t.lie_at, "__name__", "") != "raster_lie_at":
        return False
    try:
        import fastperc
        fastperc.lib()
    except Exception:                                            # noqa: BLE001
        return False
    if not hasattr(t, "_simulate_py"):
        t._simulate_py = t.simulate
    t.simulate = simulate_c
    return True
