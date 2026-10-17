"""Unit tests for the truth-map tools (light: no rasters, no simulation).

  python3 -m pytest -q course_data/truth/test_corridor.py
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import corridor as C                                      # noqa: E402

FJ = dict(ref="1", par=4, frame=dict(tee_ll=[-93.6514799, 42.0414217], aim_ll=[-93.6513061, 42.0393752]))


def test_corridor_frame_round_trip():
    xy = np.array([[-30.0, 150.0], [12.5, 270.0], [60.0, 340.0]])
    ll = C.ring_ll(FJ, xy)
    fr = C.frame_of(FJ, 1.0)
    back = fr.ll_to_yds(ll)
    assert np.allclose(back[:, 0], xy[:, 0], atol=0.01) and np.allclose(-back[:, 1], xy[:, 1], atol=0.01)


def test_render_px_matches_frame():
    fr = C.frame_of(FJ, 5.0)
    xy = np.array([[10.0, 200.0]])
    px = C.yd_to_px(fr, xy)[0]
    ll = C.ring_ll(FJ, xy)
    assert np.allclose(fr.ll_to_px(ll)[0], px, atol=0.05)


def test_lie_grid_order_and_edges():
    zones = [C.Z("recovery", C.rect(-60, -20, 140, 350)), C.Z("fairway", C.rect(-15, 15, 140, 350)),
             C.Z("first_cut", C.rect(-18, -15, 140, 350))]
    A, X, lie = C.lie_grid(zones)
    i = int(np.argmin(abs(A - 250)))
    assert lie[i, int(np.argmin(abs(X - 0)))] == "fairway"
    assert lie[i, int(np.argmin(abs(X + 16.5)))] == "first_cut"
    assert lie[i, int(np.argmin(abs(X + 30)))] == "recovery"
    rows = C.edges(zones)
    r = next(r for r in rows if r["along"] == 250)
    assert r["L"]["hazard"] == "recovery" and r["L"]["near"] and r["R"]["hazard"] is None


def test_hand_maps_schema():
    for p in glob.glob(os.path.join(HERE, "*", "hand_zones_ll.json")):
        d = json.load(open(p))
        assert set(d) >= {"doc", "source", "holes", "missing"}
        for k, h in d["holes"].items():
            assert h["par"] >= 4 and len(h["footprint_ll"]) == 4
            for key in ("tee_ll", "dot270_ll", "frame"):
                assert key in h, (p, k, key)
            for z in h["zones"]:
                assert z["lie"] in C.LIES and len(z["poly_ll"]) >= 3
                a = np.asarray(z["poly_ll"])
                assert np.all(np.abs(a - np.asarray(h["tee_ll"])) < 0.02), (p, k)      # within ~1.5 km of the tee
