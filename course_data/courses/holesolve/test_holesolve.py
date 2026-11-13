"""holesolve checks (python3 course_data/courses/holesolve/test_holesolve.py, or pytest; about 1 minute).

  1. the C kernel against the numpy copy of its swing loop (HoleSolve.swings) on a real hole, drop rule included
  2. the flat hole: the calibrated DP returns the engine's table
  3. gone balls (stroke and distance) in closed form against the numpy copy, on a flat hole with an OB strip
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solver as S                                                        # noqa: E402

_W = {}


def world():
    if "w" not in _W:
        _W["w"] = S.World("gateway_national", "truth")
    return _W["w"]


def _ev_numpy(hs, a, l, lie, club, th, cal):
    s = hs.swings(a, l, lie, club, th)
    gone = np.isnan(s["v"])
    n = len(gone)
    return (n + np.nansum(s["v"]) + gone.sum() * (1.0 + cal)) / (n - gone.sum()), s


def test_kernel_matches_numpy():
    W = world()
    cal = W.calibration()
    hs = W.solve_hole(10, cal=cal)
    worst, pen = 0.0, 0
    for a, l, lie in ((184, 0, "fairway"), (160, -3, "fairway"), (212, 8, "rough"), (200, 8, "sand"), (120, 20, "rough")):
        q = hs.query(a, l, lie)
        for r in q["rows"][:6]:
            th = np.arctan2(hs.G.green[1] - l, hs.G.green[0] - a) + np.radians(r["ang"])
            e, s = _ev_numpy(hs, a, l, lie, r["club"], np.float32(th), q["cal"])
            worst = max(worst, abs(e + q["cal"] - r["strokes"]))
            pen += int((s["kind"] == 3).sum())
    print("kernel vs numpy: worst difference %.5f over 30 club-directions, %d dropped balls among them" % (worst, pen))
    assert worst < 2e-3 and pen > 0


def test_flat_hole_returns_table():
    W = world()
    cal = W.calibration()
    G = W.flat_ground()
    hs = S.HoleSolve(G, W.bag, cal=cal).solve()
    T = hs.Tn[hs.st[:, 0], hs.st[:, 1], hs.st[:, 2]]
    m = np.abs(hs.sl_) <= 60
    gap = (hs.V - T)[m]
    print("flat hole, calibrated: DP - table mean %+.4f, sd %.4f, worst %.4f over %d states" %
          (gap.mean(), gap.std(), np.abs(gap).max(), m.sum()))
    assert abs(gap.mean()) < 0.01 and np.percentile(np.abs(gap), 95) < 0.03


def test_gone_ball_closed_form():
    W = world()
    R, origin = W.flat_raster()
    R.lie[(R.LL > 30) & (R.AA > 300)] = W.M.CODE["ob"]                    # an OB strip right of the fairway
    G = S.Ground(W.M, R, W.P, W.cfg["flat"]["length"], origin)
    hs = S.HoleSolve(G, W.bag, cal=None)
    a, l = 400.0, 10.0
    q = hs.query(a, l, "fairway", clubs=["4-wood"])
    r = q["rows"][0]
    th = np.arctan2(G.green[1] - l, G.green[0] - a) + np.radians(r["ang"])
    e, s = _ev_numpy(hs, a, l, "fairway", "4-wood", np.float32(th), 0.0)
    th2 = np.float32(th + np.radians(8.0))                                 # a line with OB in play
    e2, s2 = _ev_numpy(hs, a, l, "fairway", "4-wood", th2, 0.0)
    import ctypes
    ev, pen = np.zeros(1, np.float32), np.zeros(1, np.float32)
    B = W.bag
    c = B.names.index("4-wood")
    S.K().hs_curve(S._p(G.rk), S._p(hs.cellv), S._p(hs.dropv), G.na, G.nl, G.A0, G.L0, G.res, G.P["rough_roll"],
                   B.car.shape[2], S._p(np.ascontiguousarray(B.car[0, c])), S._p(np.ascontiguousarray(B.dev[0, c])),
                   S._p(np.ascontiguousarray(B.roll[0, c])), 1, S._p(np.array([th2], np.float32)),
                   ctypes.c_float(a), ctypes.c_float(l), ctypes.c_float(0.0), ctypes.c_float(0.0), S._p(ev), S._p(pen))
    gone = np.isnan(s2["v"]).mean()
    print("gone balls: best line %.4f (kernel %.4f); 8 deg right %.4f (kernel %.4f), %.1f %% gone" %
          (e, r["strokes"], e2, ev[0], 100 * gone))
    assert abs(e - r["strokes"]) < 2e-3 and abs(e2 - ev[0]) < 2e-3 and gone > 0.02 and abs(pen[0] - gone) < 1e-6


if __name__ == "__main__":
    for f in (test_kernel_matches_numpy, test_flat_hole_returns_table, test_gone_ball_closed_form):
        f()
    print("ok")
