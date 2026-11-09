"""joint routing: where a missing detection must be, from the routing and the card.

When the solver numbers a hole whose tee (or whose tee and green) was not detected, the app still needs a place to
show and to ask about. Proposals are marked `virtual` in the result and are never shown as certain.

  virtual tee (green g found): the tee lies at the card yardage from g, back along the fairway that leads to the
      green (far end of its centreline, extended); with no fairway: towards the previous hole's green.
  missing hole (no green): the next tee is a short walk after the missing green, the previous green a short walk
      before the missing tee, so the hole is proposed as (previous green + 60 yd) -> (next tee - 60 yd).
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Point


def _unit(v):
    n = float(np.hypot(*v))
    return v / n if n > 1e-6 else np.array([1.0, 0.0])


def virtual_tee(co, g, yards=None, prev_green=None):
    q = co["G"][g]
    qp = Point(q[0], q[1])
    best = None
    for f in co["fair"]:
        dg = f["poly"].distance(qp)
        if dg > 75:
            continue
        cl = f["cl"]
        far = cl[int(np.argmax(np.hypot(*(cl - q).T)))]
        L = float(np.hypot(*(far - q)))
        if L < 90:
            continue
        if best is None or dg < best[0]:
            best = (dg, far, L)
    if best is not None:
        _, far, L = best
        u = _unit(far - q)
        return q + u * max(float(yards or 0.0), L + 35.0)
    if prev_green is not None:
        v = co["G"][prev_green] - q
        L = float(np.hypot(*v))
        return q + _unit(v) * (float(yards) if yards else max(L - 60.0, 100.0))
    return None


def propose(d, sol):
    """-> {position: dict(tee=xy | None, green=xy | None)} for the virtual / missing holes of a solution."""
    co, pr = d["co"], sol["pr"]
    hs = sol["holes"]
    out = {}
    for i, (t, g) in enumerate(hs):
        if t >= 0 and g >= 0:
            continue
        y = None
        if pr.Y is not None:
            y = float(pr.Y[pr.kstar if pr.kstar is not None else 0, i])
        pg = hs[i - 1][1] if i > 0 and hs[i - 1][1] >= 0 else None
        if g >= 0:
            out[i] = dict(tee=virtual_tee(co, g, y, pg), green=None)
            continue
        nt = hs[i + 1][0] if i + 1 < len(hs) and hs[i + 1][0] >= 0 else None
        a = co["G"][pg] if pg is not None else None
        b = d["geo"]["Tc"][nt] if nt is not None else None
        tee = green = None
        if a is not None and b is not None:
            u = _unit(b - a)
            L = float(np.hypot(*(b - a)))
            if y and abs(L - y) > 150:                     # the hole does not run straight between them: dog-leg out
                n = np.array([-u[1], u[0]])
                h = np.sqrt(max((y / 2.0) ** 2 - (L / 2.0) ** 2, 0.0)) if y > L else 0.0
                tee, green = a + u * 40.0, (a + b) / 2.0 + n * h
            else:
                tee, green = a + u * 60.0, b - u * 60.0
        elif a is not None:
            tee, green = a + np.array([60.0, 0.0]), a + np.array([60.0 + (y or 350.0), 0.0])
        elif b is not None:
            tee, green = b - np.array([60.0 + (y or 350.0), 0.0]), b - np.array([60.0, 0.0])
        out[i] = dict(tee=tee, green=green)
    return out
