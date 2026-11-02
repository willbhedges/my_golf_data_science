"""Fast checks for the unmapped-tier adapter (one dev course, no model fit)."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_u as PU  # noqa: E402
import percfeat as PF  # noqa: E402
import detect_eval as DE  # noqa: E402
import scene_fc as SF  # noqa: E402

B = PU.B


def _row():
    rows = B.courses("dev", tier="unmapped_card")
    return next(r for r in rows if r["slug"] == "falmouth_me") if any(r["slug"] == "falmouth_me" for r in rows) else rows[0]


def test_scene_fc_tags():
    row = _row()
    x = B.inputs(row, "unmapped_nocard")
    assert not any((f["properties"] or {}).get("golf") for f in x["fc"]["features"])     # tier has no OSM golf
    feats = SF.golf_features(x["scene"])
    kinds = {f["properties"]["golf"] for f in feats}
    assert {"green", "tee", "fairway"} <= kinds
    n_green = sum(1 for g in x["scene"]["greens"] if g.get("polygon"))
    assert sum(1 for f in feats if f["properties"]["golf"] == "green") == n_green


def test_build_and_perc_columns():
    row = _row()
    d = PU.build(row, dict(g_min=0.0, t_min=0.0, f_min=0.0, extra_tees=False, tee_mode="boxes"))
    assert len(d["greens"]) and len(d["tees"]) and d["hX"].shape[0] == len(d["hp"])
    w = {k: d[k].shape[1] for k in ("hX", "tX", "tpX")}
    d = PF.augment(d, DE.load_scene(row), "all")
    assert d["hX"].shape[1] == w["hX"] + len(PF.HOLE_P)
    assert d["tX"].shape[1] == w["tX"] + len(PF.TRANS_P)
    assert d["tpX"].shape[1] == w["tpX"] + 1
    o = dict(hX=np.zeros((3, w["hX"])), tX=np.zeros((2, w["tX"])), tpX=np.zeros((1, w["tpX"])))
    PF.pad_osm(o, "all")
    assert o["hX"].shape[1] == d["hX"].shape[1] and o["tpX"].shape[1] == d["tpX"].shape[1]


def test_detection_oracle():
    """Truth greens / tees fed as candidates are found with recall = precision = 1."""
    row = _row()
    t = B.truth(row["slug"])
    G = [dict(ll=h["green_ll"], p=1.0, kind="hole") for h in t["holes"]]
    T = [dict(ll=h["tee_ll"], pts=[h["tee_ll"]], p=1.0) for h in t["holes"]]
    d = DE.detect_course(t, G, T, lambda g: True, lambda x: True)
    assert d["g_rec"] == d["N"] == d["g_true"] == d["t_rec"] == d["t_true"]


def test_perception_provenance():
    """held-out = the scene's perception models never trained on the course's state (perc_provenance.json)."""
    old = "perception-20261017-1247"
    pv = DE.provenance()[old]
    assert set(pv["train_states"]) == {"CA", "IL", "MA", "MS", "NH", "WI"}
    assert DE.perc_split(dict(slug="x_ar", state="AR"), mid=old) == "held_out"
    assert DE.perc_split(dict(slug="x_ca", state="CA"), mid=old) == "in_sample"
    assert DE.perc_split(dict(slug="x_ca", state="CA"), mid="no-such-model") == "unknown"
    assert DE.perc_course_seen(dict(slug=pv["train_courses"][0], state="CA"), mid=old)


# ------------------------------------------------------------------ tee-candidate re-scorer (tee_rescore.py)
def _toy_scene():
    sq = lambda x, y, d=0.0001: [[x, y], [x + d, y], [x + d, y + d], [x, y + d], [x, y]]   # noqa: E731
    return dict(
        greens=[dict(id="g1", p=0.9, p_hole=0.9, kind="hole", centroid=[-95.0, 39.0], polygon=sq(-95.0, 39.0)),
                dict(id="g2", p=0.8, p_hole=0.8, kind="hole", centroid=[-95.0, 39.004], polygon=sq(-95.0, 39.004))],
        tee_complexes=[dict(id="t1", p=0.6, p_range_tee=0.0, centroid=[-95.0, 39.0035], src=["segment"], virtual=False,
                            boxes=[dict(id="t1.1", p=0.7, centroid=[-95.0, 39.0035], area_m2=200.0,
                                        polygon=sq(-95.0, 39.0035))]),
                       dict(id="t2", p=0.4, p_range_tee=0.5, centroid=[-95.003, 39.0], src=["lidar_pad"], virtual=False,
                            boxes=[])],
        fairways=[dict(id="f1", p=0.9, ends=[[-95.0, 39.0005], [-95.0, 39.003]], axis_deg=0.0)],
        clubhouse=dict(ll=[-95.004, 39.0], p=0.9), relations=dict(green_to_tee=[
            dict(green="g1", tee="t1", p_next=0.2, p_edge=0.1, aims_at_green=False)]))


def test_tee_rescore_features_shape_and_finite():
    import tee_rescore as TS
    ids, X = TS.features(_toy_scene())
    assert ids == ["t1", "t2"] and X.shape == (2, len(TS.FEATS))
    j = TS.FEATS.index("d_green1")
    assert 50 < X[0, j] < 62 and np.isfinite(X[:, j]).all()            # t1 -> g2: 0.0005 deg lat = ~56 m
    assert X[0, TS.FEATS.index("n_green_range")] == 1                  # g1 at ~389 m is in hole range, g2 is not
    assert X[1, TS.FEATS.index("lidar_only")] == 1 and X[0, TS.FEATS.index("lidar_only")] == 0


def test_tee_rescore_apply_overrides_p_and_filters():
    import tee_rescore as TS
    sc = TS.apply(_toy_scene(), {"t1": 0.05, "t2": 0.9})
    pc = {t["id"]: float(t["p"]) * (1 - float(t.get("p_range_tee") or 0)) for t in sc["tee_complexes"]}
    assert pc == {"t1": 0.05, "t2": 0.9}
    feats = SF.golf_features(sc, t_min=0.1)
    assert {f["properties"]["complex"] for f in feats if f["properties"]["golf"] == "tee"} == {"t2"}
    assert TS.apply(_toy_scene(), None)["tee_complexes"][0]["p"] == 0.6         # no scores -> scene unchanged


def test_tee_rescore_folds_hold_out_states():
    import tee_rescore as TS
    rows = [dict(slug=f"c{i}_{s.lower()}", state=s) for i, s in enumerate("GA GA KY ME MN UT WY KY ME".split())]
    folds = TS.state_folds(rows, k=5)
    assert set(folds.values()) <= set(range(5))
    for a in rows:
        for b in rows:
            if a["state"] == b["state"]:
                assert folds[a["slug"]] == folds[b["slug"]]


def test_prep_u_uses_tee_scores():
    row = _row()
    sc = DE.load_scene(row)
    keep = sc["tee_complexes"][0]["id"]
    scores = {row["slug"]: {t["id"]: (0.99 if t["id"] == keep else 0.01) for t in sc["tee_complexes"]}}
    kw = dict(g_min=0.0, t_min=0.5, f_min=0.0, extra_tees=False, tee_mode="boxes")
    d = PU.build(row, dict(kw, tee_scores=scores))
    n_box = max(1, len([b for b in sc["tee_complexes"][0].get("boxes", []) if b.get("polygon") and len(b["polygon"]) >= 3]))
    assert len(d["tees"]) <= n_box < len(PU.build(row, kw)["tees"])
