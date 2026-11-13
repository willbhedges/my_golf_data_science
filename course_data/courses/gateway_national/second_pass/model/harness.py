"""Second-pass model review harness (statistics specialist). Read-only on the engine: imports
course_data/courses/v2_course.py, activates Gateway `truth` (Back) and solves the central world the way
opt/solve2.py does (coarse 3,000 swings on the whole aim grid, then N2 fresh common swings on aim +/-10).
Experiments wrap / monkey-patch M.shots, M.Raster.strokes etc. in their own process; nothing is written to the
engine or the Gateway data.

    from harness import *          # course, meta, M, D, solve, table_row
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
# SNAP=<dir>: a frozen copy of the engine + Gateway inputs at one commit (git archive <commit> ... | tar -x), because
# the shared checkout moves under a running experiment (four states in 30 minutes on 2026-11-13)
ROOT = os.path.abspath(os.environ.get("SNAP") or REPO)
sys.path.insert(0, os.path.join(ROOT, "course_data", "courses"))
import v2_course as vc                                   # noqa: E402

WHICH = os.environ.get("WHICH", "truth")
course, meta, M, D = vc.activate(os.environ.get("SLUG", "gateway_national"), WHICH)
HOLES = [k for k in course.ORDER if k in course.HOLES]
import subprocess                                        # noqa: E402
try:                                                     # the shared checkout moves: every result names its state
    STATE = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    _dirty = subprocess.run(["git", "-C", REPO, "status", "--short", "--", "course_data/courses/v2_course.py",
                             "course_data/courses/gateway_national/config.json",
                             "course_data/courses/gateway_national/truth", "spirit_hollow"], capture_output=True, text=True).stdout.strip()
    STATE += "+dirty" if _dirty else ""
    if os.environ.get("SNAP"):
        STATE = "snapshot " + os.path.basename(ROOT)
except Exception:                                        # noqa: BLE001
    STATE = "?"
print("engine / map state:", STATE, "| temp_k", M.central()["temp_k"], flush=True)
N1, N2 = 3000, int(os.environ.get("N2", 16000))
_Z = {}


def zz(n, seed):
    if (n, seed) not in _Z:
        _Z[(n, seed)] = M.draws_z(n, seed)
    return _Z[(n, seed)]


_R = {}


def raster(h):
    if h not in _R:
        _R[h] = M.Raster(M.HOLES[h])
    return _R[h]


def solve(h, P=None, clubs=None, seed1=7, seed2=77, n2=None, S=None, keep=False, half=10.0, aim_fix=None):
    """Central-world two-stage solve of hole h under parameters P (default: D.central(h)).
    S: optional per-cell strokes array replacing R.strokes(P, length). aim_fix {club: aim}: score those aims
    (no optimisation). Returns dict(pick, runner, aim, margin, se, clubs{club: aim, ev, window}, [s per swing])."""
    P = D.central(h) if P is None else P
    hd = M.HOLES[h]
    R = raster(h)
    S = R.strokes(P, hd["length"]) if S is None else S
    n2 = n2 or N2
    z1, z2 = zz(N1, seed1), zz(n2, seed2)
    res = {}
    for c in (clubs or M.REAL_CLUBS):
        if aim_fix is not None:
            aims = np.array([aim_fix[c]])
            ev2, (a, l, lie, s) = M.ev_curve(R, S, hd, c, P, z2, aims)
            res[c] = dict(aim=float(aims[0]), ev=float(ev2[0]), window=None, s=1.0 + s[:, 0], lie=lie[:, 0],
                          a=a[:, 0], l=l[:, 0])
            continue
        ev, _ = M.ev_curve(R, S, hd, c, P, z1, D.AIMS)
        r = D.robust_aim(D.AIMS, ev)
        aims = np.arange(r["aim"] - half, r["aim"] + half + 0.01, 0.5)
        ev2, (a, l, lie, s) = M.ev_curve(R, S, hd, c, P, z2, aims)
        r2 = D.robust_aim(aims, ev2, lo=max(-D.AIM_LIMIT, aims[0]), hi=min(D.AIM_LIMIT, aims[-1]))
        j = int(np.argmin(np.abs(aims - r2["aim"])))
        res[c] = dict(aim=r2["aim"], ev=r2["ev"], window=r2["window"], s=1.0 + s[:, j], lie=lie[:, j],
                      a=a[:, j], l=l[:, j], curve=(aims, ev2))
    o = sorted(res, key=lambda c: res[c]["ev"])
    d = res[o[1]]["s"] - res[o[0]]["s"]
    out = dict(pick=o[0], runner=o[1], aim=res[o[0]]["aim"], margin=float(res[o[1]]["ev"] - res[o[0]]["ev"]),
               se=float(d.std(ddof=1) / np.sqrt(n2)), order=o,
               clubs={c: dict(aim=res[c]["aim"], ev=round(res[c]["ev"], 4), window=res[c]["window"]) for c in o})
    if keep:
        out["raw"] = res
    return out


def short(r):
    return "%-9s %+6.1f  m=%.3f+/-%.3f vs %s" % (r["pick"], r["aim"], r["margin"], r["se"], r["runner"])


def compare(base, new):
    """One-line description of what changed between two solve() results of the same hole."""
    if new["pick"] != base["pick"]:
        return "CLUB %s %+.1f -> %s %+.1f (m %.3f)" % (base["pick"], base["aim"], new["pick"], new["aim"], new["margin"])
    da = new["aim"] - base["aim"]
    return "%s aim %+.1f (%+.1f), m %.3f (was %.3f)" % (new["pick"], new["aim"], da, new["margin"], base["margin"])
