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
