"""green_auto.py (automatic greens): the pick on a synthetic P map, which holes it touches, the package stage hook.

    python3 -m pytest -q course_data/product/test_green_auto.py
"""
import copy
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import green_auto as GA  # noqa: E402

CD = os.path.dirname(HERE)
PKG = os.path.join(CD, "packages", "annbriar", "package.json")


def _window(n=280):
    return dict(n=n, res=GA.RES_M, x0=1000.0, y0=2000.0 + n * GA.RES_M)


def _disc(shape, c, r):
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    return (xx - c[0]) ** 2 + (yy - c[1]) ** 2 <= r * r


def test_pick_prefers_green_sized_blob_near_prior():
    w = _window()
    k = w["n"] // GA.STEP                      # 1 m cells
    P = np.full((k, k), 0.05)
    P[_disc(P.shape, (70, 70), 13)] = 0.9      # ~530 m2 green at the window centre
    P[_disc(P.shape, (120, 30), 13)] = 0.95    # a second green 60 m away (the next hole's)
    P[_disc(P.shape, (20, 120), 4)] = 0.99     # a 50 m2 blob (a tee / a collar): too small
    prior = (w["x0"] + 75.0, w["y0"] - 72.0)   # ~5 m from the first green's centre
    best = GA.pick(P, w, prior)
    assert best is not None and 400 < best["area_m2"] < 700 and best["d_prior_m"] < 8
    far = (w["x0"] + 121.0, w["y0"] - 31.0)
    assert GA.pick(P, w, far)["d_prior_m"] < 3   # the prior decides between two real greens
    poly = GA.mask_polygon(best["mask"], w)
    assert poly is not None and abs(poly.area - best["area_m2"]) / best["area_m2"] < 0.25


def test_pick_splits_green_from_fairway():
    """A green that touches the fairway (P 0.6 on the fairway, 0.95 on the green) is cut out at a higher threshold."""
    w = _window()
    k = w["n"] // GA.STEP
    P = np.full((k, k), 0.05)
    P[60:140, 62:78] = 0.62                    # fairway strip leading in (1280 m2) ...
    P[_disc(P.shape, (70, 50), 13)] = 0.95     # ... to the green
    best = GA.pick(P, w, (w["x0"] + 70.0, w["y0"] - 50.0))
    assert best is not None and best["area_m2"] < 800 and best["d_prior_m"] < 5


def test_area_prior():
    assert GA.area_prior(500) == 1.0 and GA.area_prior(50) == 0.0 and GA.area_prior(5000) == 0.0
    assert 0 < GA.area_prior(200) < 1 and 0 < GA.area_prior(1100) < 1


@pytest.mark.skipif(not os.path.exists(PKG), reason="fixture package not checked out")
def test_holes_touched_and_stage_hook():
    pkg = json.load(open(PKG))
    pkg["holes"] = {k: v for k, v in pkg["holes"].items() if k in ("2", "4")}
    assert not GA.estimated_green(pkg["holes"]["4"]) and GA.mapped_green(pkg["holes"]["4"])
    h = pkg["holes"]["2"]
    h["provenance"]["green"] = "hole_line_end"
    h["green_polygon_ll"] = h["green_polygon"] = None
    assert GA.estimated_green(h) and not GA.mapped_green(h)
    seg = copy.deepcopy(pkg["holes"]["4"])
    seg["provenance"]["green"] = "segment"
    assert not GA.estimated_green(seg)            # an imagery green from the segment workflow is kept
    sys.path.insert(0, os.path.join(CD, "mapper"))
    import apply as AP
    PK = AP.platform_package()
    off = PK.call_green_auto({"green_auto": False}, copy.deepcopy(pkg), [])
    assert off["stages"]["green_auto"].startswith("off")
    full = json.load(open(PKG))
    assert PK.call_green_auto({}, full, [])["stages"]["green_auto"].startswith("not needed")
