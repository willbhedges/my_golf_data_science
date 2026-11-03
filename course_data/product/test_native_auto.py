"""Tests for the automatic native-side classifier (product/native_auto.py).

    python3 -m pytest -q course_data/product/test_native_auto.py

Synthetic holes and rasters only (a straight corridor frame, a 30-yd fairway): no course data is read.
"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import native_auto as NA  # noqa: E402

M = NA.M
NC = NA.NC
TEE, AIM = [-93.0, 38.9], [-93.0, 38.9 + 250 * 0.9144 / 110574.0]   # due north, 250 yds, on the UTM 15N meridian


def _fj():
    fr = M.corridor_frame(TEE, AIM, 1.0)
    return dict(ref="1", par=4, tee_ll=TEE, aim_ll=AIM, frame=fr.to_json())


def _ring(fj, xy):
    return [[float(x), float(y)] for x, y in M.xy_to_ll(fj, xy)]


def _box(x0, x1, a0, a1):
    return [(x0, a0), (x1, a0), (x1, a1), (x0, a1)]


def _pkg(fj, native=()):
    zs = [dict(lie="fairway", poly=_ring(fj, _box(-15, 15, 100, 430)), src="osm")]
    for x0, x1 in native:
        zs.append(dict(lie="native", poly=_ring(fj, _box(x0, x1, 150, 350)), src="osm"))
    return dict(holes={"1": dict(ref="1", par=4, tee_ll=TEE, aim_ll=AIM, green_ll=AIM, zones_ll=zs)})


def _rasters(fj, s2_left=0.9, s2_right=0.1, hag_left=0.5):
    """1 m HAG / CHM, 0.6 m NAIP and a 10 m S2 P grid in UTM 15N around the hole; the left half of the corridor
    (x < -20 yds) gets s2_left / hag_left, the rest s2_right / 0."""
    from affine import Affine
    from pyproj import Transformer
    tr = Transformer.from_crs("EPSG:4326", "EPSG:32615", always_xy=True)
    e0, n0 = tr.transform(*TEE)
    x0, y1 = e0 - 200, n0 + 500

    def grid(res, fill_left, fill_right, dtype=np.float32):
        W = H = int(round(700 / res))
        t = Affine(res, 0, x0, 0, -res, y1)
        cols = x0 + (np.arange(W) + 0.5) * res
        a = np.where(cols[None, :] < e0 - 20 * 0.9144, fill_left, fill_right).astype(dtype)
        return np.repeat(a, H, 0), t
    hag, th = grid(1.0, hag_left, 0.0)
    s2, ts = grid(10.0, s2_left, s2_right)
    W = H = int(round(700 / 0.6))
    tn = Affine(0.6, 0, x0, 0, -0.6, y1)
    rng = np.random.default_rng(0)
    naip = dict(year="2023", t=tn)
    for k in NA.NAIP_KEYS:
        naip[k] = rng.normal(0.5, 0.05, (H, W)).astype(np.float32)
    return {"crs": "EPSG:32615", "hag": (hag, th), "s2": (s2, ts), "naip": [naip, dict(naip, year="2021")]}


def test_side_features_sees_the_left_side():
    fj = _fj()
    rows = NA.side_features("synthetic", _pkg(fj), {"1": fj}, rs=_rasters(fj), step=2.0)
    by = {r["side"]: r for r in rows}
    assert set(by) == {"L", "R"}
    assert by["L"]["s2_O"] > 0.8 and by["R"]["s2_O"] == pytest.approx(0.1, abs=1e-6)   # 10 m cells at the edge
    assert by["L"]["s2ge5_O"] > 0.85 and by["R"]["s2ge5_O"] == 0.0
    assert by["L"]["hag_ge25_O"] == 1.0 and by["L"]["hag_ge25_F"] == 0.0
    assert by["L"]["open_O"] == pytest.approx(1.0) and by["L"]["tree_O"] == 0.0
    d = NA.derive(rows)
    dl = next(r for r in d if r["side"] == "L")
    assert dl["d_hag_OF"] == pytest.approx(1.0)
    assert dl["c_s2ge5_O"] == pytest.approx(0.5, abs=0.05)
    assert dl["z_s2ge5_O"] == 0.0                       # <= 2 sides on the course: no within-course spread
    assert NA.matrix(d).shape == (2, len(NA.FEATURES)) and np.isfinite(NA.matrix(d)[:, NA.FEATURES.index("s2_O")]).all()


def test_no_s2_means_no_automatic_native():
    fj = _fj()
    rs = _rasters(fj)
    rows = NA.side_features("synthetic", _pkg(fj), {"1": fj}, rs=rs, step=2.0)
    assert NA.course_usable(rows)
    del rs["s2"]
    rows = NA.side_features("synthetic", _pkg(fj), {"1": fj}, rs=rs, step=2.0)
    assert not NA.course_usable(rows) and not np.isfinite(rows[0]["s2_O"])
    p = {str(i): {"L": 0.9, "R": 0.1} for i in range(8)}
    assert NA.course_share(p, 0.7) == 0.5 and NA.course_fires(p, 0.7)
    p.update({str(i): {"L": 0.1, "R": 0.1} for i in range(8, 20)})
    assert not NA.course_fires(p, 0.7)                  # 8 of 40 sides: isolated hits, the gate stays shut


def test_trees_and_hazards_are_not_open_ground():
    fj = _fj()
    pkg = _pkg(fj)
    pkg["holes"]["1"]["zones_ll"].append(dict(lie="water", poly=_ring(fj, _box(20, 70, 140, 360)), src="osm"))
    rs = _rasters(fj, hag_left=10.0)                       # left: 10 m canopy everywhere off the fairway
    by = {r["side"]: r for r in NA.side_features("synthetic", pkg, {"1": fj}, rs=rs, step=2.0)}
    assert by["L"]["tree_O"] > 0.95 and by["L"]["open_O"] < 0.05
    assert by["R"]["haz_O"] > 0.8 and by["R"]["open_O"] < 0.2


def test_weights_balance_courses_and_classes():
    s = ["a"] * 10 + ["b"] * 30
    y = [1] * 5 + [0] * 5 + [1] * 3 + [0] * 27
    w = NA.balanced_weights(s, y)
    assert w.mean() == pytest.approx(1.0)
    y = np.array(y)
    assert (w * y).sum() == pytest.approx((w * (1 - y)).sum())


def test_lr_separates_and_matches_sklearn_objective():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(200, 3))
    y = (X[:, 0] + 0.5 * X[:, 1] + rng.normal(0, 0.5, 200) > 0).astype(float)
    coef, b0 = NA._lr(X, y, np.ones(200), C=0.5)
    assert coef[0] > coef[1] > abs(coef[2])
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError:
        return
    m = LogisticRegression(C=0.5, max_iter=5000, tol=1e-10).fit(X, y)
    assert np.allclose(coef, m.coef_[0], atol=1e-4) and b0 == pytest.approx(m.intercept_[0], abs=1e-4)


def test_fit_predict_loco_and_threshold():
    rng = np.random.default_rng(2)
    rows, y = [], []
    for c in "abcd":
        for i in range(40):
            yi = int(i % 3 == 0)
            r = {f: float(rng.normal()) for f in NA.FEATURES}
            r.update(slug=c, hole=str(i), side="L", s2_O=yi + rng.normal(0, 0.3), open_O=float("nan") if i == 5 else 0.5)
            rows.append(r)
            y.append(yi)
    y = np.array(y)
    m = NA.fit(rows, y)
    assert set(m) >= {"features", "median", "mu", "sd", "coef", "intercept"}
    p = NA.predict_rows(m, rows)
    assert p[y == 1].mean() > 0.7 and p[y == 0].mean() < 0.3
    pl = NA.loco(rows, y)
    assert ((pl >= 0.5) == (y == 1)).mean() > 0.85
    t = NA.pick_threshold(pl, y, prec=0.9)
    sel = pl >= t
    assert y[sel].mean() >= 0.9
    assert NA.pick_threshold(np.zeros(10), np.zeros(10), prec=0.9) == pytest.approx(0.95)


def test_apply_sides_adds_band_without_erasing():
    fj = _fj()
    pkg = _pkg(fj, native=[(30, 60)])                       # existing native on the right
    out = NA.apply_sides(pkg, {"1": fj}, {"1": ["L"]}, p={"1": {"L": 0.91, "R": 0.2}})
    assert len(pkg["holes"]["1"]["zones_ll"]) == 2           # input untouched
    zs = out["holes"]["1"]["zones_ll"]
    auto = [z for z in zs if z.get("src") == NA.SRC]
    assert auto and all(z["side"] == "L" and z["p"] == 0.91 for z in auto)
    assert any(z.get("src") == "osm" and z["lie"] == "native" for z in zs)    # the right-side native stays
    g = NC.native_xy(fj, out["holes"]["1"])
    from shapely.geometry import box
    assert g.intersection(box(-65, 150, -26, 345)).area > 0.9 * 39 * 195        # beyond 10 yds of the fairway edge
    assert g.intersection(box(-25, 150, -15, 345)).area < 1.0                     # mown rough stays clear
    assert out["holes"]["1"]["verification"]["native_auto"]["sides"] == "L"
    assert NA.sides_from_p({"1": {"L": 0.8, "R": 0.4}, "2": {"L": 0.1, "R": 0.7}}, 0.7) == {"1": ["L"], "2": ["R"]}


def test_confirm_priors_clip():
    pri = NA.confirm_priors({"3": {"L": 1.0, "R": 0.0}})
    assert pri["3"]["L"]["p"] == 0.97 and pri["3"]["R"]["p"] == 0.03 and pri["3"]["L"]["w"] is None
    assert NC.state_p(pri["3"], "L") == pytest.approx(0.97 * 0.97)


def test_shipped_model_shape():
    m = NA.load_model()
    if m is None:
        pytest.skip("no native_auto_model.json")
    assert m["features"] == NA.FEATURES
    assert len(m["coef"]) == len(m["median"]) == len(m["mu"]) == len(m["sd"]) == len(NA.FEATURES)
    assert 0.3 <= m["thr"] <= 0.95


def test_build_layer_gate_and_enabled_flag(monkeypatch):
    monkeypatch.setattr(NA, "ENABLED", False)
    fj = _fj()
    k = len(NA.FEATURES)
    sure = dict(features=NA.FEATURES, median=[0.0] * k, mu=[0.0] * k, sd=[1.0] * k, coef=[0.0] * k, intercept=3.0, thr=0.7)
    pkg = _pkg(fj)
    out, info = NA.build_layer("synthetic", pkg, frames={"1": fj}, model=sure, rs=_rasters(fj))
    assert out is pkg and info["sides"] == {"1": "both"} and info["share"] == 1.0
    assert info["why"].startswith("ENABLED is False")
    out, info = NA.build_layer("synthetic", pkg, frames={"1": fj}, model=sure, rs=_rasters(fj), force=True)
    assert info["why"] == "added" and out["stages"]["native_auto"].startswith("ok: 1 holes")
    assert {z["side"] for z in out["holes"]["1"]["zones_ll"] if z.get("src") == NA.SRC} == {"L", "R"}
    unsure = dict(sure, intercept=-3.0)
    out, info = NA.build_layer("synthetic", pkg, frames={"1": fj}, model=unsure, rs=_rasters(fj), force=True)
    assert out is pkg and info["why"].startswith("course gate shut")
    rs = _rasters(fj)
    del rs["s2"]
    out, info = NA.build_layer("synthetic", pkg, frames={"1": fj}, model=sure, rs=rs, force=True)
    assert out is pkg and info["why"].startswith("no S2")
