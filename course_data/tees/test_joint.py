"""Synthetic tests for the Q2 joint tee assignment, green centroid, Q1 labels and Q3 lidar pads
(python -m pytest -q course_data/tees)."""
import json
import math
import os
import random
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lidar_pads as lp  # noqa: E402
import place_tee as pt  # noqa: E402
from test_place_tee import F, box, ll, straight_hole  # noqa: E402


def d_green(r, green_xy):
    x, y = F.fwd(r["lat"], r["lon"])
    return math.hypot(x - green_xy[0], y - green_xy[1])


def ring(cx, cy, w, h):
    return [ll(cx + dx, cy + dy) for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]]


# ----------------------------------------------------------------------------- joint assignment
def test_sets_back_to_front_on_their_boxes():
    line = straight_hole(400)
    tees = [box(0, -30, tid="gold"), box(2, 0, tid="black"), box(-3, 40, tid="white"), box(0, 90, tid="rust")]
    out = pt.assign_tee_sets(line, tees, {"Gold": 430, "Black": 400, "White": 360, "Rust": 310})
    assert [out[s]["tee_id"] for s in ("Gold", "Black", "White", "Rust")] == ["gold", "black", "white", "rust"]
    assert all(r["order_ok"] for r in out.values())
    assert all(r["source"] == "osm" for r in out.values())


def test_shared_long_box_keeps_gold_behind_black():
    out = pt.assign_tee_sets(straight_hole(400), [box(0, -10, h=40, tid="long")], {"Gold": 425, "Black": 405})
    assert out["Gold"]["tee_id"] == out["Black"]["tee_id"] == "long"
    assert out["Gold"]["shared_with"] == ["Black"]
    assert out["Gold"]["dist_yd"] > out["Black"]["dist_yd"]
    assert abs(out["Gold"]["dist_yd"] - 425) < 0.6 and abs(out["Black"]["dist_yd"] - 405) < 0.6


def test_never_out_of_order_on_random_holes():
    """Property: whatever the boxes, the placed tees keep the card order along the line of play."""
    rng = random.Random(3)
    for _ in range(150):
        L = rng.uniform(320, 520)
        tees = [box(rng.uniform(-15, 15), rng.uniform(-60, 120), h=rng.uniform(6, 30), tid=i) for i in range(rng.randint(1, 6))]
        ys = sorted((L + rng.uniform(-110, 40) for _ in range(4)), reverse=True)
        sets = dict(zip(["Gold", "Black", "White", "Rust"], ys))
        out = pt.assign_tee_sets(straight_hole(L), tees, sets, order_penalty=1e4)
        d = [out[s]["dist_yd"] for s in sets]
        assert all(a + 2.0 + 1e-6 >= b for a, b in zip(d, d[1:])), (sets, d)


def test_walkback_only_when_nothing_fits():
    out = pt.assign_tee_sets(straight_hole(400), [box(0, 0, tid="b")], {"Gold": 480, "Black": 400})
    assert out["Gold"]["method"] == "walkback" and out["Gold"]["source"] == "hole_line"
    assert out["Black"]["tee_id"] == "b"
    assert abs(d_green(out["Gold"], (0, 400)) - 480) < 0.6


def test_green_centroid_is_the_measuring_point():
    # the line runs 12 yds past the green centre: measuring to the centroid picks the nearer box
    line = straight_hole(412)
    tees = [box(0, 0, h=8, tid="a"), box(0, 12, h=8, tid="b")]
    to_end = pt.assign_tee_sets(line, tees, {"Black": 400})
    to_green = pt.assign_tee_sets(line, tees, {"Black": 400}, green=ll(0, 400))
    assert to_end["Black"]["tee_id"] == "b" and to_green["Black"]["tee_id"] == "a"


def test_green_for_line():
    greens = [dict(coords=ring(0, 400, 20, 30)), dict(coords=ring(200, 400, 20, 30))]
    g = pt.green_for_line(straight_hole(405), greens)
    x, y = F.fwd(*g)
    assert abs(x) < 0.5 and abs(y - 400) < 0.5                    # line end inside: its centroid
    g2 = pt.green_for_line(straight_hole(440), greens)            # 25 yds past the edge: nearest within 40
    assert g2 is not None and abs(F.fwd(*g2)[1] - 400) < 0.5
    assert pt.green_for_line(straight_hole(500), greens) is None


def test_centroid_ll_is_exact():
    c = pt.centroid_ll(ring(37.0, -211.0, 14, 9))
    x, y = F.fwd(*c)
    assert abs(x - 37.0) < 0.05 and abs(y + 211.0) < 0.05


def test_dogleg_back_tee_off_the_line_found_on_relaxed_pass():
    # new back tee 80 yds left of the first leg (SH 2: the 607 Gold shares hole 18's complex)
    line = [ll(0, 0), ll(0, 300), ll(150, 300)]                    # 450 yds
    green = (150, 300)
    gold_xy = (-80, -60)
    gold_d = math.hypot(gold_xy[0], 300 - gold_xy[1]) + 150
    lines = {"2": line}
    tees = [box(0, 0, tid="black"), box(*gold_xy, tid="gold_new")]
    res = pt.place_course_sets(lines, tees, {"2": {"Gold": round(gold_d), "Black": 450}})["2"]
    assert res["tees"]["Black"]["tee_id"] == "black"
    assert res["tees"]["Gold"]["tee_id"] == "gold_new" and res["tees"]["Gold"]["relaxed"]
    assert abs(res["tees"]["Gold"]["dist_yd"] - gold_d) < 2 and abs(green[0] - 150) < 1e-9
    plain = pt.assign_tee_sets(line, tees, {"Gold": round(gold_d), "Black": 450})
    assert plain["Gold"]["method"] == "walkback"                    # outside the 45-yd window


def test_lidar_pad_used_only_where_osm_has_no_box():
    lines = {"1": straight_hole(400)}
    tees = [box(0, 0, tid="black")]
    pads = [dict(id="lidar:0", coords=ring(0, -45, 10, 14), source="lidar"),
            dict(id="lidar:1", coords=ring(0, 1, 10, 14), source="lidar")]
    res = pt.place_course_sets(lines, tees, {"1": {"Gold": 445, "Black": 400}}, pads=pads)["1"]
    assert res["tees"]["Gold"]["tee_id"] == "lidar:0" and res["tees"]["Gold"]["method"] == "lidar_pad"
    assert res["tees"]["Gold"]["source"] == "lidar" and res["tees"]["Gold"]["confidence"] != "high"
    assert res["tees"]["Black"]["tee_id"] == "black"               # the OSM box wins over the duplicate pad
    none = pt.place_course_sets(lines, tees, {"1": {"Black": 400}}, pads=pads)["1"]
    assert none["tees"]["Black"]["tee_id"] == "black" and none["sets_without_box"] == []


def test_borrowed_box_needs_a_tight_match():
    lines = {"A": straight_hole(400), "B": [ll(40, 0), ll(40, 350)]}
    tees = [box(0, 0, tid="a"), box(30, -20, tid="b_back")]         # b_back is B's (closer to B's line)
    res = pt.place_course_sets(lines, tees, {"A": {"Gold": 420, "Black": 400}})
    assert res["A"]["tees"]["Gold"]["tee_id"] == "b_back" and res["A"]["tees"]["Gold"]["borrowed"]


# ----------------------------------------------------------------------------- Q1 labels
def test_screenshot_tee_sets_file():
    import screenshot_sets
    sets = screenshot_sets.load()
    assert {"1", "2B", "2F", "9B", "9F", "17", "7", "15"} <= set(sets)
    assert {k for k, v in sets.items() if v == "Gold"} == {"1", "2B", "9B", "11"}
    assert sets["2F"] == sets["9F"] == sets["13"] == "Black" and sets["15"] == "White"
    d = json.load(open(screenshot_sets.OUT))
    assert d["holes"]["1"]["position_yd"]["Gold"] < 10 < d["holes"]["1"]["position_yd"]["Black"]
    assert not any(v.get("conflict") for v in d["holes"].values())


# ----------------------------------------------------------------------------- Q3 lidar pads
def synthetic_dem(n=160):
    """4 % slope with a levelled pad (14 x 24 m, fill up to ~1 m, 1:3 banks) running out onto a flat
    floodplain (flat, but not raised: the top-hat is ~0 there)."""
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    z = 200 + 0.04 * yy
    cy, cx = 50, 50
    inside = (abs(yy - cy) <= 12) & (abs(xx - cx) <= 7)
    top = 200 + 0.04 * (cy + 12) + 0.6
    dist = np.maximum(abs(yy - cy) - 12, abs(xx - cx) - 7)
    bank = np.clip(top - dist / 3.0, None, None)
    z = np.where(inside, top, np.maximum(z, np.where(dist < 6, bank, z)))
    z = np.minimum(z, 200 + 0.04 * 105)                           # flat valley floor below row 105
    return z


def test_components_find_the_pad_not_the_terrace():
    comps = lp.components(synthetic_dem())
    assert len(comps) == 1
    c = comps[0]
    assert abs(np.mean(c["rows"]) - 50) < 3 and abs(np.mean(c["cols"]) - 50) < 3
    assert 150 <= c["area_m2"] <= 400 and c["bank_frac"] >= lp.BANK_FRAC and c["tophat_m"] >= lp.TOPHAT_MEAN_M


def test_detect_pads_georeferenced(tmp_path):
    rasterio = pytest.importorskip("rasterio")
    from pyproj import Transformer
    from rasterio.transform import from_origin
    z = synthetic_dem()
    x0, y0 = 655800.0, 4514000.0
    path = str(tmp_path / "dem.tif")
    with rasterio.open(path, "w", driver="GTiff", width=z.shape[1], height=z.shape[0], count=1, dtype="float32",
                       crs="EPSG:26915", transform=from_origin(x0, y0, 1.0, 1.0)) as dst:
        dst.write(z.astype("float32"), 1)
    pads = lp.detect_pads(path)
    assert len(pads) == 1
    lon, lat = Transformer.from_crs("EPSG:26915", "EPSG:4326", always_xy=True).transform(x0 + 50.5, y0 - 50.5)
    assert pt.haversine_yd(pads[0]["centroid"], (lat, lon)) < 3
    assert pads[0]["source"] == "lidar" and len(pads[0]["coords"]) >= 4
    v = lp.validate(pads, [dict(coords=[(lat, lon)]), dict(coords=[(lat + 0.01, lon)])])
    assert v["precision"] == 1.0 and v["recall"] == 0.5
    near_green = lp.detect_pads(path, greens=[dict(coords=[(lat + 1e-5, lon), (lat, lon + 1e-5), (lat - 1e-5, lon)])])
    assert near_green == []                                       # greens are flat and raised too
