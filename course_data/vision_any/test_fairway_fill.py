"""fairway_fill: a synthetic course on a 1 m UTM grid (two par-4s, a 32-yd mown strip down each line in smooth bright
turf, textured rough elsewhere): the fill recovers the strips, is gated when fairway and rough look alike, and never
touches a hole whose landing corridor already has a fairway."""
import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
pytest.importorskip("cv2")
import fairway_fill as FF  # noqa: E402
import layers as L  # noqa: E402

LON0, LAT0 = -94.45, 38.83
YD = 0.9144


def _stack(separable=True, seed=3):
    from affine import Affine
    from pyproj import Transformer
    S = L.Stack()
    S.res, S.W, S.H = 1.0, 700, 600
    tr = Transformer.from_crs("EPSG:4326", "EPSG:32615", always_xy=True)
    x0, y0 = tr.transform(LON0, LAT0)
    x0, y0 = x0 - 200, y0 - 100
    S.crs = "EPSG:32615"
    S.transform = Affine(1.0, 0, x0, 0, -1.0, y0 + S.H)
    S.bounds = (x0, y0, x0 + S.W, y0 + S.H)
    rng = np.random.default_rng(seed)
    lines = {}
    strip = np.zeros((S.H, S.W), bool)
    rows = np.arange(S.H)[:, None]
    cols = np.arange(S.W)[None, :]
    for ref, cx in (("1", 150), ("2", 450)):                  # two holes running north, 300 m apart
        strip |= (np.abs(cols - cx) <= 14.6) & (rows >= 120) & (rows <= 480)
        xs, ys = S.transform * (np.array([cx + 0.5, cx + 0.5]), np.array([560.5, 60.5]))
        inv = Transformer.from_crs("EPSG:32615", "EPSG:4326", always_xy=True)
        lon, lat = inv.transform(xs, ys)
        lines[ref] = [[float(lon[0]), float(lat[0])], [float(lon[1]), float(lat[1])]]
    S.naip = []
    for yr in (2020, 2022):
        b = np.empty((S.H, S.W, 4), np.float32)
        rough = np.array([0.30, 0.38, 0.25, 0.45]) + rng.normal(0, 0.06, (S.H, S.W, 1))
        mown = np.array([0.30, 0.46, 0.24, 0.62]) + rng.normal(0, 0.012, (S.H, S.W, 1))
        b[:] = np.where(strip[..., None] if separable else False, mown, rough)
        S.naip.append((yr, b))
    S.layers = {"hag": np.zeros((S.H, S.W), np.float32)}
    return S, lines, strip


def _pkg(lines, fairway_on=()):
    holes = {}
    for ref, ln in lines.items():
        h = dict(ref=ref, par=4, tee_ll=ln[0], aim_ll=ln[1], green_ll=ln[1], hole_line_ll=ln,
                 tees={"Blue": dict(tee_ll=ln[0], aim_ll=ln[1])}, zones_ll=[])
        if ref in fairway_on:                               # a mapped fairway across the landing corridor
            f = FF._xy(*ln[0])
            k = np.array(f([ln[1]])[0])
            u = k / np.linalg.norm(k)
            r = np.array([u[1], -u[0]])
            kx, ky = math.cos(math.radians(ln[0][1])) * 111320.0 / YD, 110574.0 / YD
            ring = [u * s + r * v for s, v in ((100, -15), (380, -15), (380, 15), (100, 15))]
            h["zones_ll"].append(dict(lie="fairway", src="osm",
                                      poly=[[ln[0][0] + x / kx, ln[0][1] + y / ky] for x, y in ring]))
        holes[ref] = h
    return dict(tee_set="Blue", holes=holes)


def _masks(S):
    z = np.zeros((S.H, S.W), bool)
    return {k: z.copy() for k in ("green", "tee", "bunker", "water", "building", "road", "course", "fairway")}


def test_fill_recovers_mown_strips():
    S, lines, strip = _stack()
    out, rep = FF.fill_holes(_pkg(lines), S, _masks(S))
    assert rep["status"].startswith("ok: 2/2") and rep["dprime"] > 2
    got = np.zeros(strip.shape, bool)
    for h in out["holes"].values():
        zs = [z for z in h["zones_ll"] if z["src"] == FF.SRC]
        assert zs and all(z["lie"] == "fairway" for z in zs)
        got |= S.rasterize([__import__("shapely.geometry", fromlist=["Polygon"]).Polygon(z["poly"]) for z in zs])
        assert 25 <= rep["holes"][h["ref"]]["width_yd"] <= 40
    inter, union = (got & strip).sum(), (got | strip).sum()
    assert inter / union > 0.75


def test_fill_gated_when_fairway_not_separable():
    S, lines, _ = _stack(separable=False)
    out, rep = FF.fill_holes(_pkg(lines), S, _masks(S))
    assert rep["status"].startswith("gated") and rep["dprime"] < FF.MIN_DPRIME
    assert not any(z.get("src") == FF.SRC for h in out["holes"].values() for z in h["zones_ll"])


def test_holes_with_a_fairway_are_left_alone():
    S, lines, _ = _stack()
    pkg = _pkg(lines, fairway_on=("1",))
    assert not FF.needs_fill(pkg["holes"]["1"], "Blue") and FF.needs_fill(pkg["holes"]["2"], "Blue")
    out, rep = FF.fill_holes(pkg, S, _masks(S))
    assert rep["wanted"] == ["2"]
    assert out["holes"]["1"]["zones_ll"] == pkg["holes"]["1"]["zones_ll"]
    assert any(z.get("src") == FF.SRC for z in out["holes"]["2"]["zones_ll"])
    pkg2 = _pkg(lines, fairway_on=("1", "2"))
    _, rep2 = FF.fill_package(pkg2, "nowhere", None, S=S)
    assert rep2["status"].startswith("not needed")
