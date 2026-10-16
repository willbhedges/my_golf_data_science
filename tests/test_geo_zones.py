"""spirit_hollow/geo_zones.py + tee_sets.py: coordinate round trip and holes_for() schema (offline, fast)."""
import os

import numpy as np
import pytest
from matplotlib.path import Path

import geo_zones as GZ
import tee_sets as TS

HAVE_HAND = os.path.exists(GZ.OUT_PATH)
needs_hand = pytest.mark.skipif(not HAVE_HAND, reason="run spirit_hollow/geo_zones.py first")


@pytest.fixture(scope="module")
def G():
    return GZ.transforms_from_json()


@needs_hand
def test_every_traced_hole_georeferenced(course, G):
    assert set(G) == set(course.HOLES)


@needs_hand
def test_px_ll_px_round_trip(course, G):
    rng = np.random.default_rng(0)
    for k, g in G.items():
        pts = np.c_[rng.uniform(0, 920, 200), rng.uniform(GZ.Y0, GZ.Y1, 200)]
        pts = np.r_[pts, [course.HOLES[k]["tee"], course.HOLES[k]["dot270"]]]
        back = g.ll_to_px(g.px_to_ll(pts))
        assert np.abs(back - pts).max() < 0.5, k


@needs_hand
def test_json_zones_match_course(course, G):
    data = GZ.load()
    for k, h in course.HOLES.items():
        rec = data["holes"][str(k)]
        assert [z["lie"] for z in rec["zones"]] == [lie for lie, _ in h["zones"]], k
        g = G[k]
        for z, (_, poly) in zip(rec["zones"], h["zones"]):
            assert np.abs(g.ll_to_px(z["poly_ll"]) - np.asarray(poly, float)).max() < 0.5
        # the 270 dot sits ~270 ground yds from the tee
        fr = g.frame
        d = np.linalg.norm(fr._to_yd([rec["dot270_ll"]]) - fr._to_yd([rec["tee_ll"]]))
        assert 240 < d < 300, (k, d)


def test_shotgeo_inverse_exact():
    import render as R
    fr = R.Frame((-91.15, 40.76), (-91.15, 40.765), ppy=3.5, tee_px=(500, 2100), size=(1440, 2520))
    W = np.array([[0.99, -0.05, 300.0], [0.06, 0.98, 250.0]])
    g = GZ.ShotGeo(fr, W, "test")
    p = np.array([[0, 0], [920, 2000], [460, 1900.5]], float)
    assert np.abs(g.ll_to_px(g.px_to_ll(p)) - p).max() < 1e-6


def test_point_along_line_distance():
    import render as R
    tee = (-91.15, 40.76)
    line = [(-91.15, 40.7595), (-91.15, 40.763), (-91.148, 40.765)]
    p = TS.point_along_line(tee, line, 250)
    fr = R.Frame(tee, line[-1], proj="enu")
    assert abs(np.linalg.norm(fr.ll_to_yds([p])[0]) - 250) < 1.5


@needs_hand
@pytest.mark.parametrize("tee_set", ["Gold", "Rust"])
def test_holes_for_schema(course, t, tee_set):
    holes, par3, images = TS.holes_for(tee_set, render=False)
    assert set(holes) | set(par3) == set(range(1, 19))
    assert set(par3) == set(course.PAR3)
    yards, par = TS.card(tee_set)
    known = {"fairway", "first_cut", "rough", *t.HAZARDS}
    for k, h in holes.items():
        for f in ("par", "length", "tee", "dot270", "green", "zones", "image", "aim_min", "aim_max"):
            assert f in h, (k, f)
        assert h["length"] == yards[k] and h["par"] == par[k]
        assert abs(np.linalg.norm(np.subtract(h["dot270"], h["tee"])) - 270 * h["frame"]["ppy"]) < 1e-6
        assert h["tee"][1] == pytest.approx(TS.TEE_PX_Y)
        for lie, poly in h["zones"]:
            assert lie in known
            assert len(poly) >= 3 and np.isfinite(np.asarray(poly, float)).all()
            Path(poly)
        assert images[k] == h["image"]
    for k, p in par3.items():
        p0 = course.PAR3[k]
        for f in p0:
            assert f in p, (k, f)
        assert p["center"] == yards[k]
        assert p["haz"] == p0["haz"]
        assert len(p["green"]) == len(p0["green"])
        assert p["front"] < p["center"] < p["back"]


@needs_hand
def test_holes_for_runs_in_tee_strategy(t, z):
    holes, _, _ = TS.holes_for("White", render=False)
    t.HOLES = holes
    r = t.best_aim(5, "Driver", aims=np.array([0.0]), z=z[:, :300])
    assert np.isfinite(r["ev"]) and 2.5 < r["ev"] < 6
