"""Drop-in replacement for tee_strategy.expected_strokes (review patch, not wired in).

Two fixes, both in mozingo/tee_strategy.py::_expected_strokes / expected_strokes:

 1. Lost ball in native grass. The original scores a lost ball as "1 + rough at the same
    distance", which is a penalty-area drop. A ball lost outside a penalty area is stroke and
    distance (or the 2-stroke Model Local Rule E-5), i.e. the same cost the code already gives
    OB ("2 + rough"). At ~150 yds in, the original under-charges each lost ball by 1 stroke
    (SG about -1.2 instead of Broadie's about -2, research.md section 4). If the native is
    staked as a penalty area, keep the original -- set NATIVE_IS_PENALTY_AREA = True.

 2. HCP_BASELINE consistency. The original applies the lie multiplier to (lie - fairway), which
    for native also scales the penalty stroke (x1.3), while water/OB keep their stroke unscaled
    and use the *tour* rough gap (x1.0, not the 0.7 used for an actual rough lie). Here every
    lie is a mixture of (weight, playing lie, penalty strokes); the multiplier applies to the
    playing lie's gap only and penalty strokes are added unscaled.

    import baseline_patch as BP; BP.install()   # monkeypatches tee_strategy
    BP.uninstall()
"""
import numpy as np

import tee_strategy as t

NATIVE_IS_PENALTY_AREA = False
_ORIG = {}


def _mixture(lie):
    if lie == "water":
        return [(1.0, "rough", 1.0)]
    if lie == "ob":
        return [(1.0, "rough", 2.0)]
    if lie == "native":
        L = t.NATIVE_LOST
        pen = 1.0 if NATIVE_IS_PENALTY_AREA else 2.0
        return [(L, "rough", pen), (1 - L, "recovery_hard", 0.0)]
    if lie == "recovery":
        return [(t.TREE_SEVERITY, "recovery_hard", 0.0), (1 - t.TREE_SEVERITY, "rough", 0.0)]
    return [(1.0, lie, 0.0)]


def _tour(base, d):
    key = "recovery" if base == "recovery_hard" else base
    return np.interp(np.clip(d, t.DIST[0], t.DIST[-1]), t.DIST, t.BASELINE[key])


def expected_strokes(lie, dist):
    dist = np.asarray(dist, float)
    beyond = np.maximum(dist - t.DIST[-1], 0) * t.LONG_SLOPE
    fw = _tour("fairway", dist) + beyond
    out = np.zeros_like(dist)
    for w, base, pen in _mixture(lie):
        e = _tour(base, dist) + beyond
        if t.HCP_BASELINE:
            mult = t.HCP_LIE_MULT.get("recovery" if base == "recovery_hard" else base, 1.0)
            e = fw + 0.40 + 0.001 * (np.clip(dist, 20, 450) - 150) + mult * (e - fw)
        out = out + w * (e + pen)
    return out


def install():
    if not _ORIG:
        _ORIG["es"] = t.expected_strokes
    t.expected_strokes = expected_strokes


def uninstall():
    if _ORIG:
        t.expected_strokes = _ORIG.pop("es")
