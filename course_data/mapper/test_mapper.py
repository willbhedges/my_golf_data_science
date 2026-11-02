"""Tests for the agent mapper's apply step (course_data/mapper/apply.py), the edits -> layers conversion
(write_layers.build) and the package-build hook (platform/package.apply_agent_layers).

    python3 -m pytest -q course_data/mapper/test_mapper.py

Fixture: two holes of a committed package (course_data/packages/annbriar), copied into a temp dir; the agent folder
is written by the test (no mapper output of any course is read).
"""
import copy
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import apply as AP  # noqa: E402
import common as M  # noqa: E402

PKG = os.path.join(M.CD, "packages", "annbriar", "package.json")
pytestmark = pytest.mark.skipif(not os.path.exists(PKG), reason="fixture package not checked out")


@pytest.fixture(scope="module")
def pkg():
    p = json.load(open(PKG))
    p["holes"] = {k: v for k, v in p["holes"].items() if k in ("2", "3")}
    return p


@pytest.fixture(scope="module")
def fj(pkg):
    return M.make_frames(pkg, pkg["tee_set"])


def lie_at(h, ll):
    """Visible lie at WGS84 points from the hole's zones_ll, package precedence (later wins)."""
    from matplotlib.path import Path
    PKm = AP.platform_package()
    order = PKm.LIE_ORDER
    zs = sorted(h["zones_ll"], key=lambda z: order.index(z["lie"]) if z["lie"] in order else 0)
    out = []
    for p in np.atleast_2d(ll):
        lie = "rough"
        for z in zs:
            r = AP._ring(z["poly"])
            if len(r) >= 3 and Path(np.asarray(r, float)[:, :2]).contains_point(p):
                lie = z["lie"]
        out.append(lie)
    return out


def write_agent(d, feats=(), tees=None):
    os.makedirs(d, exist_ok=True)
    json.dump(dict(type="FeatureCollection", properties=dict(mapper="test"), features=list(feats)),
              open(os.path.join(d, AP.ZONE_FILE), "w"))
    if tees is not None:
        json.dump(dict(holes=tees), open(os.path.join(d, AP.TEE_FILE), "w"))


def feat(fj, ref, op, lie, xy, **kw):
    ll = M.xy_to_ll(fj[ref], xy).tolist()
    return dict(type="Feature", properties=dict(hole=ref, op=op, lie=lie, **kw),
                geometry=dict(type="Polygon", coordinates=[ll + [ll[0]]]))


def test_frame_round_trip(fj):
    xy = np.array([[-30.0, 200.0], [12.5, 310.0]])
    back = M.ll_to_xy(fj["2"], M.xy_to_ll(fj["2"], xy))
    assert np.abs(back - xy).max() < 0.01


def test_add_then_erase_layer_by_layer(pkg, fj, tmp_path):
    box = [[-60, 200], [-40, 200], [-40, 260], [-60, 260]]
    write_agent(str(tmp_path), [feat(fj, "2", "add", "native", box, note="tan in 2 years", confidence="medium")])
    out, rep = AP.apply(pkg, str(tmp_path))
    h = out["holes"]["2"]
    pt = M.xy_to_ll(fj["2"], [[-50, 230]])
    assert lie_at(h, pt) == ["native"] or lie_at(pkg["holes"]["2"], pt) != ["rough"]
    added = [z for z in h["zones_ll"] if z.get("src") == AP.SRC]
    assert added and added[0]["lie"] == "native" and added[0]["note"] == "tan in 2 years"
    assert "native" in h["provenance"]["zones"] and "agent" in h["provenance"]["zones"]["native"]
    assert h["provenance"]["agent"].startswith("add native")
    assert out["stages"]["agent_layers"].startswith("ok:") and rep["ops"] == 1
    assert out["agent_layers"]["files"][AP.ZONE_FILE]
    # the yard-frame zones (what the planner reads) carry the new zone too
    assert len(h["zones"]) == len(pkg["holes"]["2"]["zones"]) + 1 or len(h["zones"]) > len(pkg["holes"]["2"]["zones"])
    # input untouched
    assert not any(z.get("src") == AP.SRC for z in pkg["holes"]["2"]["zones_ll"])
    # erase only that lie: every native zone loses the box, the fairway is untouched
    write_agent(str(tmp_path), [feat(fj, "2", "erase", "native", [[-70, 120], [70, 120], [70, 400], [-70, 400]])])
    out2, rep2 = AP.apply(out, str(tmp_path))
    h2 = out2["holes"]["2"]
    pts = M.xy_to_ll(fj["2"], [[x, a] for x in range(-65, 66, 10) for a in range(130, 400, 15)])
    assert "native" not in lie_at(h2, pts)
    fw = lambda hh: sum(1 for z in hh["zones_ll"] if z["lie"] == "fairway")              # noqa: E731
    assert fw(h2) == fw(out["holes"]["2"])
    # native zones wholly inside the box are dropped, those crossing it are clipped (agent_clipped)
    assert rep2["holes"]["2"]["ops"][0]["op"] == "erase" and rep2["holes"]["2"]["ops"][0]["yd2"] > 0


def test_grow_only_inside_region(pkg, fj, tmp_path):
    h0 = pkg["holes"]["3"]
    trees = [z for z in h0["zones_ll"] if z["lie"] == "recovery"]
    if not trees:
        pytest.skip("no trees on the fixture hole")
    region = [[-70, 120], [70, 120], [70, 400], [-70, 400]]
    write_agent(str(tmp_path), [feat(fj, "3", "grow", "recovery", region, by=5.0)])
    out, rep = AP.apply(pkg, str(tmp_path))
    grown = rep["holes"]["3"]["ops"][0]
    assert grown["op"] == "grow" and grown["yd2"] > 0
    new = [z for z in out["holes"]["3"]["zones_ll"] if z.get("src") == AP.SRC]
    assert new and all(z["lie"] == "recovery" for z in new)
    # every new piece is inside the region (+ tolerance) and touches the old canopy (within 5 yds)
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    L = AP.Local(*h0["tee_ll"])
    reg = Polygon(L.fwd(M.xy_to_ll(fj["3"], region))).buffer(0.5)
    old = unary_union([AP._geom(L, AP._ring(z["poly"])) for z in trees])
    for z in new:
        g = AP._geom(L, AP._ring(z["poly"]))
        assert reg.contains(g.buffer(-0.05))
        assert g.distance(old) < 0.5


def test_tee_move_and_keep(pkg, fj, tmp_path):
    h0 = pkg["holes"]["2"]
    S = pkg["tee_set"]
    new_ll = M.xy_to_ll(fj["2"], [[0.0, -10.0]])[0].tolist()            # 10 yds behind the auto tee
    other = next(s for s in h0["tees"] if s != S)
    write_agent(str(tmp_path), [], tees={"2": {S: dict(action="move", tee_ll=new_ll, evidence="box visible 10 yds back",
                                                        confidence="high"),
                                               other: dict(action="keep")}})
    out, rep = AP.apply(pkg, str(tmp_path))
    t = out["holes"]["2"]["tees"][S]
    assert t["method"] == "agent" and t["tee_source"] == "agent"
    assert abs(t["agent_checked"]["moved_yd"] - 10.0) < 0.5
    assert t["measured_yards"] >= h0["tees"][S]["measured_yards"] + 7
    assert t["aim_ll"] != h0["tees"][S]["aim_ll"]                          # aim re-derived from the new tee
    assert out["holes"]["2"]["tee_ll"] == t["tee_ll"]                       # yard frame re-derived (reframe)
    assert out["holes"]["2"]["tees"][other]["tee_ll"] == h0["tees"][other]["tee_ll"]
    assert out["holes"]["2"]["tees"][other]["agent_checked"]["action"] == "keep"
    assert rep["tees_moved"] == 1 and rep["tees_checked"] == 2


def test_unknown_hole_is_skipped_not_fatal(pkg, fj, tmp_path):
    f = feat(fj, "2", "add", "water", [[0, 200], [10, 200], [10, 210], [0, 210]])
    f["properties"]["hole"] = "17"
    write_agent(str(tmp_path), [f])
    out, rep = AP.apply(pkg, str(tmp_path))
    assert rep["skipped"] and "17" in rep["skipped"][0]
    assert out["holes"]["2"]["zones_ll"] == pkg["holes"]["2"]["zones_ll"]


def test_write_layers_validation(pkg, fj):
    import write_layers as WL
    ok = dict(holes={"2": dict(reviewed=["long_grass"], edits=[
        dict(op="add", lie="native", shape={"beyond_fairway": {"w": 10, "side": "L", "a0": 180, "a1": 330}},
             confidence="medium", evidence="tan both years")])},
        tees={"2": {pkg["tee_set"]: dict(action="move", to=[0, -6], evidence="box")}})
    feats, tees, rev, probs = WL.build("t", ok, pkg, fj, fj)
    assert feats and feats[0]["properties"]["lie"] == "native" and feats[0]["geometry"]["type"] in ("Polygon", "MultiPolygon")
    assert abs(tees["2"][pkg["tee_set"]]["moved_yd"] - 6.0) < 0.5
    for bad in (dict(op="add", lie="trees", shape={"rect": [0, 10, 200, 220]}),          # 'trees' is a layer, not a lie
                dict(op="paint", lie="native", shape={"rect": [0, 10, 200, 220]}),
                dict(op="add", lie="native", shape={"rect": [200, 220, 0, 10]}),          # [along, x] swapped
                dict(op="grow", lie="recovery", shape={"rect": [0, 10, 200, 220]})):     # grow without by
        with pytest.raises(WL.EditError):
            WL.build("t", dict(holes={"2": dict(edits=[bad])}), pkg, fj, fj)
    with pytest.raises(WL.EditError):
        WL.build("t", dict(tees={"2": {pkg["tee_set"]: dict(action="move", to=[0, -6])}}), pkg, fj, fj)  # no evidence


def test_write_layers_native_keepout_and_checks(pkg, fj):
    """Unsure native never comes within NATIVE_KEEPOUT yds of the fairway; high-confidence native is kept (listed)."""
    import write_layers as WL
    from shapely.geometry import shape
    from shapely.ops import unary_union
    strip = {"beyond_fairway": {"w": 2, "side": "both", "a0": 180, "a1": 330}}
    out = {}
    for conf in ("medium", "high"):
        ed = dict(holes={"2": dict(edits=[dict(op="add", lie="native", shape=strip, confidence=conf, evidence="x")])})
        feats, _, _, probs = WL.build("t", ed, pkg, fj, fj)
        g = unary_union([shape(dict(type="Polygon", coordinates=[M.ll_to_xy(fj["2"], r[0] if isinstance(r[0][0], list) else r).tolist()]))
                         for r in ([feats[0]["geometry"]["coordinates"]] if feats[0]["geometry"]["type"] == "Polygon"
                                   else feats[0]["geometry"]["coordinates"])]).buffer(0)
        mown = WL._mown(fj["2"], pkg["holes"]["2"])
        out[conf] = (g.intersection(mown.buffer(WL.NATIVE_KEEPOUT - 0.5)).area, probs)
    assert out["medium"][0] < 2 and any("removed" in p for p in out["medium"][1])
    assert out["high"][0] > 100 and any("high-confidence" in p for p in out["high"][1])
    # sand over the canopy is flagged, not refused
    can = WL._canopy(fj["3"], pkg["holes"]["3"])
    can = can.intersection(M.window(-10)) if can is not None else None
    assert can is not None and can.area > 50
    c = can.representative_point()
    ed = dict(holes={"3": dict(edits=[dict(op="add", lie="sand", shape={"ell": [c.x, c.y, 2, 2]}, evidence="x")])})
    feats, _, _, probs = WL.build("t", ed, pkg, fj, fj)
    assert feats and any("canopy" in p for p in probs)


def test_package_build_hook(pkg, fj, tmp_path):
    PKm = AP.platform_package()
    d = tmp_path / "agent"
    write_agent(str(d), [feat(fj, "2", "add", "water", [[30, 250], [45, 250], [45, 270], [30, 270]])])
    out = PKm.apply_agent_layers({"agent_layers": str(d)}, copy.deepcopy(pkg), [])
    assert out["stages"]["agent_layers"].startswith("ok:")
    assert any(z.get("src") == AP.SRC and z["lie"] == "water" for z in out["holes"]["2"]["zones_ll"])
    w = []
    same = PKm.apply_agent_layers({"agent_layers": str(tmp_path / "nope")}, copy.deepcopy(pkg), w)
    assert same["stages"]["agent_layers"].startswith("missing") and w
    assert same["holes"]["2"]["zones_ll"] == pkg["holes"]["2"]["zones_ll"]
    assert PKm.apply_agent_layers({}, pkg, []) is pkg


def test_course_page_passes_agent_layers(tmp_path, monkeypatch):
    sys.path.insert(0, os.path.join(M.CD, "library"))
    import course_page as CP
    monkeypatch.setattr(CP, "wj", lambda p, d, **kw: captured.update(d))
    captured = {}
    q = dict(name="X Golf Club", state="KS", slug="x", path="r.json", out="course_data/library/x",
             agent_layers="course_data/mapper/x/")
    CP.pkgreq(q)
    assert captured["agent_layers"] == "course_data/mapper/x/"


# ----------------------------------------------------------------------------- S2 native suggestions (s2_suggest.py)
def fake_pg(fj, box_xy=(-60, -20, 200, 300), p_in=0.9):
    """A synthetic 10 m S2 P grid around the hole: p_in inside box_xy (x0, x1, a0, a1 in the corridor frame), else 0.1."""
    from pyproj import Transformer
    tee = fj["frame"]["tee_ll"]
    epsg = 32600 + int((tee[0] + 180) // 6) + 1
    fw = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    bw = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
    X0, Y0 = fw.transform(*tee)
    X0, Y1 = np.floor(X0 / 10) * 10 - 600, np.ceil(Y0 / 10) * 10 + 600
    H = W = 120
    cx, cy = np.meshgrid(X0 + 5 + 10 * np.arange(W), Y1 - 5 - 10 * np.arange(H))
    lon, lat = bw.transform(cx.ravel(), cy.ravel())
    xy = M.ll_to_xy(fj, np.c_[lon, lat])
    x0, x1, a0, a1 = box_xy
    inside = (xy[:, 0] > x0) & (xy[:, 0] < x1) & (xy[:, 1] > a0) & (xy[:, 1] < a1)
    p = np.where(inside, p_in, 0.1).astype(np.float32).reshape(H, W)
    return dict(p=p, transform=(10.0, 0.0, X0, 0.0, -10.0, Y1), crs=f"EPSG:{epsg}", source="loco", note="test",
                tr=fw)


def test_s2_candidates_template_and_decisions(pkg, fj):
    import s2_suggest as S2S
    import write_layers as WL
    h = pkg["holes"]["2"]
    pg = fake_pg(fj["2"])
    P = S2S.p_frame(pg, fj["2"], 120, 400, 70, 1.0)
    assert P.shape == (280, 140) and np.nanmax(P) == pytest.approx(0.9) and np.nanmin(P) == pytest.approx(0.1)
    cands = S2S.candidates(pg, fj["2"], h, "2")
    assert cands and all(c["side"] == "L" for c in cands)          # the box is left of the tee line only
    c = max(cands, key=lambda c: c["area_yd2"])
    assert c["id"].startswith("S2-2-L") and 1500 < c["area_yd2"] < 4600 and c["p"] == pytest.approx(0.9)
    assert 190 <= c["along"][0] <= 215 and 285 <= c["along"][1] <= 310
    # nothing of the candidate lies on the package fairway / trees / water
    blk = S2S._not_native(fj["2"], h)
    if blk is not None:
        assert M._poly(c["shape"]["poly"]).intersection(blk).area < 0.05 * c["area_yd2"]
    t = S2S.template_entry(cands)
    assert set(t) == {"L", "R"} and not t["R"] and t["L"][0]["decision"] == "" and "poly" in t["L"][0]["shape"]
    # decisions in edits.json -> write_layers: accept adds native (keep-out applies), reject / replace add nothing
    blk_ = {"L": [dict(t["L"][0], decision="accept", confidence="medium", evidence="tufted both years")]}
    feats, _, rev, probs = WL.build("t", dict(holes={"2": dict(edits=[], s2_suggested=blk_)}), pkg, fj, fj)
    assert len(feats) == 1 and feats[0]["properties"]["s2"] == c["id"] and feats[0]["properties"]["lie"] == "native"
    assert rev["2"]["s2"][0]["decision"] == "accept"
    for d in ("reject", "replace"):
        b = {"L": [dict(t["L"][0], decision=d, evidence="green smooth mown rough in 2021")]}
        feats, _, rev, _ = WL.build("t", dict(holes={"2": dict(s2_suggested=b)}), pkg, fj, fj)
        assert not feats and rev["2"]["s2"][0]["decision"] == d
    feats, _, rev, probs = WL.build("t", dict(holes={"2": dict(s2_suggested=t)}), pkg, fj, fj)
    assert not feats and any("undecided" in p for p in probs)
    for bad in (dict(decision="maybe", evidence="x"), dict(decision="reject"),
                dict(decision="accept", evidence="x")):                      # accept without confidence
        with pytest.raises(WL.EditError):
            WL.build("t", dict(holes={"2": dict(s2_suggested={"L": [dict(t["L"][0], **bad)]})}), pkg, fj, fj)


def test_s2_native_model_is_loco_safe():
    """Training courses get their leave-one-course-out grid, never the full model; no stack -> None."""
    import s2_suggest as S2S
    NM = S2S._nm()
    md = NM.meta()
    if not md:
        pytest.skip("native_model not checked out")
    assert len(md["courses"]) >= 20 and md["thr"] == S2S.THR
    have = [c for c in md["courses"] if os.path.exists(os.path.join(NM.HERE, c, "s2_stack.npz"))]
    for c in md["courses"]:
        assert os.path.exists(NM.loco_path(c)), c                     # every training course has its fold grid
    if not have:
        pytest.skip("no S2 stack checked out")
    r = NM.p_grid(have[0], allow_full=False)
    assert r["source"] == "loco" and r["p"].shape == NM._stack_meta(have[0])["shape"]
    assert np.nanmax(r["p"]) <= 1.0 and np.nanmin(r["p"]) >= 0.0
    assert NM.p_grid("no_such_course_xyz") is None
    assert NM._decode(NM._encode(np.array([0.0, 0.5, 1.0, np.nan]))).tolist()[:3] == [0.0, 0.5, 1.0]
