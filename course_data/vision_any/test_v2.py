"""Light unit tests for the v2 hazard model (synthetic grids; no rasters, no training).

    python3 -m pytest -q course_data/vision_any/test_v2.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layers as L                      # noqa: E402
import v2_features as VF                # noqa: E402
import v2_labels as LB                  # noqa: E402
import v2_model as VM                   # noqa: E402


def fake_stack(W=400, H=500):
    from affine import Affine
    S = L.Stack()
    S.crs = "EPSG:32615"
    S.res = 1.0
    S.W, S.H = W, H
    x0, y1 = 655706.0, 4514910.0
    S.transform = Affine(1.0, 0, x0, 0, -1.0, y1)
    S.bounds = (x0, y1 - H, x0 + W, y1)
    return S


def ll_of(S, cr):
    xy = np.array([S.transform * (c, r) for c, r in cr])
    return S.xy_to_ll(xy).tolist()


def test_corridor_orientation_and_right():
    S = fake_stack()
    # tee at bottom centre, dot270 straight north: golfer's right = east = increasing column
    tee = ll_of(S, [(200, 480)])[0]
    dot = ll_of(S, [(200, 480 - 270 * LB.YD)])[0]
    h = dict(tee_ll=tee, dot270_ll=dot)
    along, lat = LB.corridor_coords(S, h)
    assert abs(along[480 - int(100 * LB.YD), 200] - 100) < 1.5
    assert lat[300, 250] > 40 and lat[300, 150] < -40


def test_rasterize_priority_and_footprint():
    S = fake_stack()
    sq = lambda c0, r0, c1, r1: ll_of(S, [(c0, r0), (c1, r0), (c1, r1), (c0, r1)])  # noqa: E731
    tee = ll_of(S, [(200, 480)])[0]
    dot = ll_of(S, [(200, 200)])[0]
    h = dict(key="1", ref="1", tee_ll=tee, dot270_ll=dot, footprint_ll=sq(50, 50, 350, 490),
             zones=[("native", sq(100, 100, 300, 300)), ("fairway", sq(180, 100, 220, 400))])
    r = LB.rasterize_hole(S, h)
    assert r["cls"][200, 120] == LB.CI["native"]
    assert r["cls"][200, 200] == LB.CI["fairway"]          # later zone wins
    assert r["cls"][10, 10] == -1                            # outside the footprint
    assert r["cls"][450, 100] == LB.CI["rough"]
    tm = LB.train_mask(r["cls"])
    assert not tm[200, 180] and tm[200, 200]                 # boundary cell dropped


def test_ref_groups():
    assert LB._ref("2B") == "2" and LB._ref("9F") == "9" and LB._ref("10") == "10"


def test_tree_rule_buffer_sign():
    c = np.zeros((60, 60), bool)
    c[20:40, 20:40] = True
    assert VM.tree_rule(c, 0, 30).sum() == 400
    assert VM.tree_rule(c, -2, 30).sum() < 400 < VM.tree_rule(c, 2, 30).sum()
    assert VM.tree_rule(c, 0, 500).sum() == 0                # clump smaller than min area dropped


def test_compose_keeps_hand_turf():
    cls = np.full((10, 10), LB.CI["rough"], np.int8)
    cls[:, :3] = LB.CI["fairway"]
    cls[0, :] = LB.CI["native"]
    trees = np.zeros_like(cls, bool)
    trees[:, 2:5] = True
    nat = np.zeros_like(trees)
    g = VM.compose(cls, trees, nat)
    assert g[5, 2] == LB.CI["fairway"] and g[5, 3] == LB.CI["recovery"]
    assert g[0, 8] == LB.CI["rough"]                         # hand native removed, model has none


def test_edge_stats():
    eh = np.array([np.nan, 10, 20, np.nan, 30])
    em = np.array([np.nan, 14, 30, 5, np.nan])
    e = VM.edge_stats(eh, em)
    assert e["agree"] == 2 and e["n_any"] == 4 and e["agree_any"] == 1
    assert sorted(e["abs_err"]) == [4.0, 10.0]


def test_edges_on_grid():
    S = fake_stack()
    tee = ll_of(S, [(200, 480)])[0]
    dot = ll_of(S, [(200, 480 - 270 * LB.YD)])[0]
    cls = np.zeros((S.H, S.W), np.int8)
    cls[:, 200 + int(20 * LB.YD):] = LB.CI["recovery"]       # trees from 20 yds right
    x = dict(h=dict(tee_ll=tee, dot270_ll=dot), S=S, sl=(slice(0, S.H), slice(0, S.W)))
    e = VM.edges(x, cls, ("recovery",), a0=190, a1=200, step=5)
    assert np.all(np.isnan(e[0::2]))                         # left side: none
    assert np.all(np.abs(e[1::2] - 20) <= 1.5)


def test_counts_iou():
    p = np.array([1, 1, 0, 0], bool)
    t = np.array([1, 0, 1, 0], bool)
    c = VM.counts(p, t)
    assert list(c) == [1, 1, 1] and abs(VM.iou_of(c) - 1 / 3) < 1e-9


def test_glcm_and_lbp():
    flat = np.zeros((40, 40), np.float32)
    rough = np.random.default_rng(0).integers(0, 8, (40, 40)).astype(np.float32)
    c0, h0 = VF.glcm_local(flat)
    c1, h1 = VF.glcm_local(rough)
    assert c1[20, 20] > c0[20, 20] and h1[20, 20] < h0[20, 20]
    ent, nu = VF.lbp_local(rough)
    assert ent.shape == rough.shape and np.isfinite(ent).all()


def test_native_mask_min_area():
    p = np.zeros((80, 80), np.float32)
    p[10:30, 10:30] = 0.9                                    # 400 m2 > 150 yd2
    p[50:55, 50:55] = 0.9                                    # 25 m2: removed
    m = VM.native_mask(p, np.ones_like(p, bool), 0.5)
    assert m[20, 20] and not m[52, 52]


def test_choose_trees_prefers_matching_buffer():
    holes = []
    for i in range(3):
        cls = np.zeros((40, 40), np.int8)
        cls[10:30, 10:30] = LB.CI["recovery"]
        corr = np.ones((40, 40), bool)
        can = np.zeros((40, 40), bool)
        can[8:32, 8:32] = True                               # canopy 2 m wider than the golfer's line
        cands = {}
        for k in (-2, 0, 2):
            cands[(2.5, k, 30)] = VM.tree_rule(can, k, 30)
        holes.append(dict(key=str(i), ref=str(i), cls=cls, corr=corr, cands=cands))
    sel, best, _ = VM.choose_trees(holes, {h["key"]: h["cands"] for h in holes})
    assert best == (2.5, -2, 30) and all(v == best for v in sel.values())
