"""Adaptive aim bound for the spirit_hollow/v2 engine on library pages (spirit_hollow/ stays read-only).

  python3 course_data/library/v2_adaptive.py <course_data/courses/v2_course.py arguments>

spirit_hollow/v2/decide.py searches a fixed aim grid (-60..+60) and takes the robust aim inside a fixed +/-40 yds
bound off the tee line (AIM_LIMIT; the wind grid shifts it by the crosswind drift). On dog-legs the library QA
found many calm / forecast picks exactly on +/-40 (Colbert Hills 13, Weaver 10, Gustin 6/7/16, Hodge 10/15,
St Andrews 15, La Nickell 5/16/17, Pevely 16): the EV curve was still falling past the bound, so the printed aim
was an artifact of the clamp. This wrapper runs v2_course.py unchanged after install():

  * D.AIMS -> -80..+80 (0.5 yd), so the curve exists past the old grid edge;
  * D.robust_aim: the v2 answer inside the usual bound first; when it sits on the bound (at_bound), that side's
    bound steps out by 20 yds (to 60, then 80 off the tee line, both shifted by the wind drift exactly as the v2
    bound is) and the wider answer is kept only if it is better by > GAIN strokes (smoothed curve) and its aim
    passes the guard (product/decide.aim_problems, the printable-aim rule): its aim point (GUARD_CARRY yds out) is in fairway / first cut / rough (not
    trees, water, sand, OB, long grass or unverified ground) and within GUARD_LINE yds of the hole's line of play
    (else it is another hole). Holes without a line of play keep the fixed bound. The same rule as
    course_data/product/decide.py adaptive_bound (the quick / error-budget engine).

The guard needs the hole: M.ev_curve is wrapped to remember the raster / hole of the latest call (robust_aim is
always called on the curves of the hole just computed). V2_ADAPTIVE_AIM=0 turns it off.
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
VC_PY = os.path.join(CD, "courses", "v2_course.py")

AIMS = np.arange(-80, 80.001, 0.5)
STEP = 20.0             # each widening, yds
MAX_EXTRA = 40.0        # at most 40 yds past the v2 bound (+/-40 -> +/-80)
GAIN = 0.002            # strokes (smoothed curve) a widening must win
GUARD_CARRY = 260.0     # yds out: the aim point checked (between the 4-wood and Driver carries)
GUARD_LINE = 40.0       # yds: the aim point's distance from the line of play
OK_LIES = ("fairway", "first_cut", "rough")
CTX = {}


def enabled():
    return os.environ.get("V2_ADAPTIVE_AIM", "1") != "0"


def _play_line_yds(hd):
    """The hole's line of play in the tee-line frame (along, right) yds, or None."""
    line = hd.get("play_line")
    if not line or len(line) < 2:
        return None
    sys.path.insert(0, os.path.join(ROOT, "mozingo")) if os.path.join(ROOT, "mozingo") not in sys.path else None
    import tee_strategy as t
    tee, fwd, right, ppy = t.hole_frame(hd)
    rel = (np.asarray(line, float) - tee) / ppy
    return np.c_[rel @ fwd, rel @ right]


def _dist_to_line(p, L):
    a, b = L[:-1], L[1:]
    d = b - a
    u = np.clip(np.einsum("ij,ij->i", p - a, d) / np.maximum(np.einsum("ij,ij->i", d, d), 1e-9), 0, 1)
    return float(np.min(np.linalg.norm(a + u[:, None] * d - p, axis=1)))


def aim_ok(M, R, hd, aim, line=None):
    """The guard for one aim (lateral yds off the tee line): aim point lie + distance to the line of play."""
    line = _play_line_yds(hd) if line is None else line
    if line is None:
        return False
    p = np.array([GUARD_CARRY, float(aim)])
    if _dist_to_line(p, line) > GUARD_LINE:
        return False
    if R is not None:
        code = int(R.lie[R.idx(np.array([p[0]]), np.array([p[1]]))][0])
        names = {v: k for k, v in M.CODE.items()}
        if names.get(code) not in OK_LIES:
            return False
    return True


def adaptive_robust_aim(base, M, aim_limit):
    """robust_aim(aims, curve, lo, hi) with the adaptive bound (see the module doc)."""
    def robust_aim(aims, curve, lo=-aim_limit, hi=aim_limit):
        r = base(aims, curve, lo, hi)
        hd, R = CTX.get("hd"), CTX.get("R")
        if not enabled() or hd is None or lo is None or hi is None:
            return r
        line = _play_line_yds(hd)
        if line is None:
            return r
        drift = -(lo + hi) / 2.0           # the wind grid passes -AIM_LIMIT - drift .. AIM_LIMIT - drift
        extra = 0.0
        while r["at_bound"] and extra < MAX_EXTRA:
            side = 1 if r["aim"] >= hi - 1 else -1
            extra += STEP
            new = (hi if side > 0 else lo) + side * STEP
            nlo, nhi = (lo, new) if side > 0 else (new, hi)
            r2 = base(aims, curve, nlo, nhi)
            if r2["ev_smooth"] < r["ev_smooth"] - GAIN and aim_ok(M, R, hd, r2["aim"] + drift, line):
                lo, hi, r = nlo, nhi, r2
                r["aim_bound"] = [float(lo), float(hi)]
            else:
                break
        return r
    return robust_aim


def install(D, M):
    """Patch an imported spirit_hollow/v2 decide (D) / model (M) pair in place (idempotent)."""
    if getattr(D, "_adaptive_aim", False) or not enabled():
        return
    D.AIMS = AIMS
    D.robust_aim = adaptive_robust_aim(D.robust_aim, M, D.AIM_LIMIT)
    ev0 = M.ev_curve

    def ev_curve(R, S, hd, club, *a, **kw):
        CTX.update(R=R, hd=hd, club=club)
        return ev0(R, S, hd, club, *a, **kw)
    M.ev_curve = ev_curve
    D._adaptive_aim = True


def load_v2_course():
    spec = importlib.util.spec_from_file_location("v2_course", VC_PY)
    vc = importlib.util.module_from_spec(spec)
    sys.modules["v2_course"] = vc
    spec.loader.exec_module(vc)
    act = vc.activate

    def activate(slug, which):
        course, meta, M, D = act(slug, which)
        install(D, M)
        return course, meta, M, D
    vc.activate = activate
    return vc


if __name__ == "__main__":
    sys.argv[0] = VC_PY
    load_v2_course().main()
