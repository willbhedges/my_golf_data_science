"""Offline tests for routing_v2.py, confirm.py on test_routing's synthetic 18-hole course."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import confirm as CF  # noqa: E402
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402
from test_routing import synthetic  # noqa: E402


def _setup(seed=1):
    fc, card, _ = synthetic(seed)
    fc0 = dict(fc, features=[f for f in fc["features"] if f["properties"].get("golf") != "hole"])
    inp = R.inputs_from_fc(fc, hide_holes=True)
    return fc, fc0, card, inp


def test_v2_recovers_synthetic_course_and_features_are_exact():
    fc, fc0, card, inp = _setup()
    ctx = R2.context(inp, card, fc=fc0)
    res = R2.solve(ctx, beam=1500)
    sc = R.score(res, R.truth_from_fc(fc))
    assert sc["hole_number_acc"] >= 0.89, sc
    a = [(h["t_idx"], h["g_idx"]) for _, h in sorted(res["holes"].items(), key=lambda kv: int(kv[0]))]
    w, _, _ = R2.load_weights()
    f, c = R2.assign_features(ctx, a, w)
    assert abs(c - res["cost"]) < 1e-3 and np.allclose(f, res["features"], atol=1e-6)
    assert all(0 <= h["p_hole"] <= 1 for h in res["holes"].values())


def test_fixed_and_exclude_propagate():
    fc, fc0, card, inp = _setup(seed=2)
    ctx = R2.context(inp, card, fc=fc0)
    res = R2.solve(ctx, beam=1500)
    h1 = res["holes"]["1"]
    # pin hole 1 to hole 2's answer: the solver must re-route hole 2 elsewhere (greens used once)
    h2 = res["holes"]["2"]
    r2 = R2.solve(ctx, beam=1500, fixed={"1": (h2["t_idx"], h2["g_idx"])})
    assert r2["holes"]["1"]["g_idx"] == h2["g_idx"] and r2["holes"]["2"]["g_idx"] != h2["g_idx"]
    assert r2["holes"]["1"]["status"] == "ok"
    # "no, that is not hole 1": the shown green + nearby boxes are excluded for hole 1
    r3 = R2.solve(ctx, beam=1500, exclude={"1": {R2.reject(ctx, h1["t_idx"], h1["g_idx"])}})
    h = r3["holes"]["1"]
    assert not (h["g_idx"] == h1["g_idx"] and h["t_idx"] >= 0 and
                np.hypot(*(ctx["txy"][h["t_idx"]] - ctx["txy"][h1["t_idx"]])) < 45)


def test_confirm_session_payload_and_answers():
    fc, fc0, card, inp = _setup(seed=3)
    s = CF.Session(inp, card, fc=fc0)
    pl = s.payload(course=dict(name="synthetic"))
    assert pl["schema"] == "golf_confirm/1" and len(pl["holes"]) == 18
    assert all(set(q) >= {"id", "kind", "ref", "taps", "bits_per_tap", "prompt"} for q in pl["questions"])
    truth = R.truth_from_fc(fc)
    # locate hole 5 by tapping the true tee and green: hole 5 becomes confirmed and correct
    s.answer(dict(kind="locate", ref="5", answer=dict(tee_ll=list(truth["5"]["tee_ll"]), green_ll=list(truth["5"]["green_ll"]))))
    assert "5" in s.fixed and R.score(s.res, truth)["per_hole"]["5"]["hole_ok"]
    # a tap far from every candidate adds a golfer candidate
    n0 = len(s.ctx["G"])
    s.answer(dict(kind="locate", ref="6", answer=dict(tee_ll=list(truth["6"]["tee_ll"]),
                                                      green_ll=[truth["6"]["green_ll"][0] + 0.003, truth["6"]["green_ll"][1]])))
    assert len(s.ctx["G"]) == n0 + 1 and s.res["holes"]["6"]["green_id"].startswith("golfer:")
    assert s.payload()["summary"]["taps_so_far"] == 4


def test_cart_graph_links_green_to_next_tee():
    pr = R.Proj(-93.0, 42.0)

    def ll(x, y):
        lo, la = pr.inv(x, y)
        return [float(lo), float(la)]
    fc = dict(features=[dict(type="Feature", properties=dict(golf="cartpath"),
                             geometry=dict(type="LineString", coordinates=[ll(0, 0), ll(60, 0), ll(60, 80)]))])
    gxy = np.array([[0.0, 5.0]])
    txy = np.array([[60.0, 85.0], [300.0, 0.0]])
    link, far, n = R2.cart_features(fc, pr, gxy, txy)
    assert n > 0 and link[0, 0] == 1 and link[0, 1] == 0
