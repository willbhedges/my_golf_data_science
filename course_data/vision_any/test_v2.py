"""Light unit tests for the v2 hazard model (synthetic grids; no rasters, no training).

    python3 -m pytest -q course_data/vision_any/test_v2.py
"""
import os
import sys

import numpy as np
import pytest

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


def _troon_grid():
    import types
    from affine import Affine
    # Troon North's package grid (run 41539188571): 3444 x 2884 m, EPSG:32612
    g = types.SimpleNamespace(crs="EPSG:32612", res=1.0, x0=418490, y0=3732792, x1=421934, y1=3735676, W=3444, H=2884,
                              ll_bbox=[-111.88014, 33.732028, -111.842701, 33.758296])
    g.transform = Affine(1.0, 0, g.x0, 0, -1.0, g.y1)
    return g


def test_ept_tiles_bound_each_pdal_read():
    """Troon North: one 10 km2 EPT read (even at a 0.5 m density cap) held every point in memory and the runner was
    shut down (exit 143, twice: runs 41114849392 and 41539188571). Big boxes are read in tiles that cover the grid
    exactly once, each no bigger than the boxes that always worked."""
    import fetch_any as FA
    g = _troon_grid()
    tiles = FA.ept_tiles(g)
    assert len(tiles) >= 4
    cover = np.zeros((g.H, g.W), np.int32)
    for t in tiles:
        assert (t["x1"] - t["x0"]) * (t["y1"] - t["y0"]) <= FA.EPT_TILE_M ** 2
        assert all(float(v) % 2 == 0 for v in (t["x0"], t["y0"], t["x1"], t["y1"]))       # the 2 m DTM grid too
        rx0, ry0, rx1, ry1 = t["read"]
        assert rx0 < t["x0"] or t["x0"] == g.x0
        assert rx0 <= t["x0"] and ry0 <= t["y0"] and rx1 >= t["x1"] and ry1 >= t["y1"]
        r0, c0, h, w = FA.tile_window(g, t)
        cover[r0:r0 + h, c0:c0 + w] += 1
    assert (cover == 1).all()
    small = _troon_grid()
    small.x1, small.y1, small.W, small.H = small.x0 + 1200, small.y0 + 1000, 1200, 1000
    assert len(FA.ept_tiles(small)) == 1


def test_fetch_ept_reads_in_tiles(tmp_path, monkeypatch):
    import json
    import types
    import rasterio
    from affine import Affine
    import fetch_any as FA
    g1 = _troon_grid()
    g2 = types.SimpleNamespace(**dict(vars(g1), res=2.0, W=g1.W // 2, H=g1.H // 2,
                                      transform=Affine(2.0, 0, g1.x0, 0, -2.0, g1.y1)))
    pdal = tmp_path / "pdal"
    pdal.write_text("")
    monkeypatch.setenv("PDAL_BIN", str(pdal))
    ring = [[-112.0, 33.6], [-111.7, 33.6], [-111.7, 33.9], [-112.0, 33.9], [-112.0, 33.6]]
    idx = dict(features=[dict(geometry=dict(type="Polygon", coordinates=[ring]),
                              properties=dict(name="AZ_MaricopaPinal_1_2020", url="u", count=1))])
    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(
        get=lambda *a, **k: types.SimpleNamespace(json=lambda: idx)))
    reads = []

    def fake_run(cmd, **kw):
        pipe = json.load(open(cmd[-1]))
        reads.append(pipe[0]["bounds"])
        for st in pipe:
            if st["type"] == "writers.gdal":
                r = st["resolution"]
                tr = Affine(r, 0, st["origin_x"], 0, -r, st["origin_y"] + st["height"] * r)
                with rasterio.open(st["filename"], "w", driver="GTiff", width=st["width"], height=st["height"],
                                   count=1, dtype="float32", crs=g1.crs, transform=tr) as dst:
                    dst.write(np.full((1, st["height"], st["width"]), 3.0, np.float32))
        return types.SimpleNamespace(returncode=0, stderr="", stdout="")
    import subprocess
    monkeypatch.setattr(subprocess, "run", fake_run)
    meta = {}
    hag = FA.fetch_ept(g1, g2, str(tmp_path), meta)
    assert len(reads) == len(FA.ept_tiles(g1)) and len(reads) >= 4
    assert hag is not None and np.isfinite(hag).all() and float(np.nanmax(hag)) == 3.0
    assert meta["ept"]["tiles"] == len(reads) and meta["ept"]["valid"] == 1.0


def test_native_threshold_none_must_be_explained():
    import json
    import pytest
    # a bare None threshold (the "LightGBM P(native) >= None" packages) is refused
    with pytest.raises(ValueError):
        VM.check_native_settings(dict(native_thr=None))
    with pytest.raises(ValueError):
        VM.check_native_settings(dict(native_thr=None, native_off="  "))
    for bad in (0, 1.0, 1.5, -0.1, "0.3", True):
        with pytest.raises(ValueError):
            VM.check_native_settings(dict(native_thr=bad))
    assert VM.check_native_settings(dict(native_thr=0.3)) is True
    assert VM.check_native_settings(dict(native_thr=None, native_off="not adopted")) is False
    # the committed product settings pass, and the package note never reads "None"
    meta = json.load(open(os.path.join(HERE, "model_v2", "model.json")))
    VM.check_native_settings(meta["settings"])
    how = VM.native_how(meta, [2023, 2022])
    assert "None" not in how
    if meta["settings"]["native_thr"] is None:
        assert how.startswith("no long grass")
    on = dict(meta, settings=dict(meta["settings"], native_thr=0.5))
    assert "P(native) >= 0.5" in VM.native_how(on, [2023])


def test_lidar_v2_reads_in_tiles(tmp_path, monkeypatch):
    """raw2 (v2_fetch.py) reads the same EPT box as fetch_any: tiled the same way."""
    import json
    import subprocess
    import types
    import rasterio
    from affine import Affine
    import fetch_any as FA
    import v2_fetch as V2
    g = _troon_grid()
    pdal = tmp_path / "pdal"
    pdal.write_text("")
    monkeypatch.setenv("PDAL_BIN", str(pdal))
    monkeypatch.setattr(V2, "ept_candidates", lambda g: ([dict(name="AZ", url="u", cov=1.0, year=2020, count=1)], None))
    reads = []

    def fake_run(cmd, **kw):
        pipe = json.load(open(cmd[-1]))
        if pipe[0]["type"] == "readers.ept":
            reads.append(pipe[0]["bounds"])
            open(pipe[-1]["filename"], "w").write("laz")
        for st in pipe:
            if st["type"] == "writers.gdal":
                r = st["resolution"]
                tr = Affine(r, 0, st["origin_x"], 0, -r, st["origin_y"] + st["height"] * r)
                with rasterio.open(st["filename"], "w", driver="GTiff", width=st["width"], height=st["height"],
                                   count=1, dtype="float32", crs=g.crs, transform=tr) as dst:
                    dst.write(np.full((1, st["height"], st["width"]), 5.0, np.float32))
        return types.SimpleNamespace(returncode=0, stderr="", stdout="")
    monkeypatch.setattr(subprocess, "run", fake_run)
    written = {}
    monkeypatch.setattr(FA, "write_tif", lambda path, arr, g, **k: written.update(arr=arr) or 1.0)
    meta = {}
    V2.fetch_lidar_v2(g, str(tmp_path), meta)
    assert len(reads) == len(FA.ept_tiles(g)) >= 4
    assert meta["lidar_v2"]["valid"] == 1.0 and np.isfinite(written["arr"]).all()


def _course_dir(tmp_path, feats, bounds=None):
    import json as _j
    d = tmp_path / "raw"
    d.mkdir()
    sm = {"course": {"name": None}}
    if bounds:
        sm["course"]["bounds"] = bounds
    (d / "summary.json").write_text(_j.dumps(sm))
    (d / "osm.geojson").write_text(_j.dumps({"type": "FeatureCollection", "features": feats}))
    return str(d)


def _poly(golf, w, s, e, n):
    return {"type": "Feature", "properties": {"golf": golf},
            "geometry": {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]]}}


def test_course_bbox_ignores_a_huge_water_hazard(tmp_path):
    """A golf=lateral_water_hazard way kept whole by the extract (a river shoreline running for km) must not grow
    the 1 m vision grid past the course: play features + the outline set the box, others add <= 300 m."""
    import fetch_any as FA
    feats = [_poly("green", -76.180, 38.980, -76.179, 38.981), _poly("tee", -76.170, 38.990, -76.169, 38.991),
             _poly("lateral_water_hazard", -76.40, 38.80, -75.90, 39.20)]
    (s, w, n, e), _ = FA.bbox_from_course_dir(_course_dir(tmp_path, feats))
    assert 38.976 < s < 38.980 and 38.991 < n < 38.995 and -76.184 < w < -76.180 and -76.169 < e < -76.165
    g = FA.Grid((s, w, n, e), 120, 1.0)
    assert g.W * g.H < 4e6


def test_course_bbox_keeps_a_nearby_water_hazard(tmp_path):
    import fetch_any as FA
    feats = [_poly("green", -76.180, 38.980, -76.179, 38.981), _poly("tee", -76.170, 38.990, -76.169, 38.991),
             _poly("water_hazard", -76.1815, 38.9795, -76.1805, 38.9805)]
    (s, w, n, e), _ = FA.bbox_from_course_dir(_course_dir(tmp_path, feats))
    assert abs(s - 38.9795) < 1e-6 and abs(w - -76.1815) < 1e-6


def test_grid_guard_refuses_a_runaway_box():
    import fetch_any as FA
    with pytest.raises(SystemExit, match="too big"):
        FA.check_grid(FA.Grid((38.8, -76.4, 39.2, -75.9), 120, 1.0))
    FA.check_grid(FA.Grid((38.976, -76.185, 38.997, -76.160), 120, 1.0))
