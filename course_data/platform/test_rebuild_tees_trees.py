"""rebuild_tees_trees.retee: the S2 tee stage re-run on a committed package (error budget, mapper base packages).

Regression (pevely_farms, 2026-11-02): raw/osm.geojson also holds a neighbouring course's golf=hole ways (refs 1, 1,
9, 10, 18, 1 km north). build_package drops them (sanity.clean_osm) but retee fed the raw OSM to place_tees_v2, so
the neighbour's ways won the ref and every set on holes 1, 9, 10, 18 moved 1,100-1,700 yds (measured 780-1,738 vs
cards 403-527)."""
import copy
import math
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rebuild_tees_trees as RT  # noqa: E402

CD = os.path.dirname(HERE)
LON0, LAT0 = -94.6, 38.9
KX = math.cos(math.radians(LAT0)) * 111320 / 0.9144
KY = 111320 / 0.9144


def ll(x, y):
    """yards east / north of the origin -> [lon, lat]"""
    return [LON0 + x / KX, LAT0 + y / KY]


def hole_way(pts, **props):
    return dict(type="Feature", geometry=dict(type="LineString", coordinates=[ll(*p) for p in pts]),
                properties=dict(golf="hole", **props))


def pkg_of(n=18):
    holes = {}
    for i in range(n):
        x = i * 100
        holes[str(i + 1)] = dict(par=4, hole_line_ll=[ll(x, 0), ll(x, 400)], green_ll=ll(x, 400),
                                 tees={"Blue": dict(tee_ll=ll(x, 0), card_yards=400, measured_yards=400)})
    return dict(holes=holes, request=dict(course="Test GC"))


# ----------------------------------------------------------------------------- OSM preparation (the root cause)
def test_neighbour_hole_ways_with_repeated_refs_are_not_used():
    feats = [hole_way([(i * 100, 0), (i * 100, 400)], ref=str(i + 1), osm_id=100 + i) for i in range(18)]
    # a neighbouring course's 1, 9, 10, 18 (no inside_course flag, listed after this course's ways: they won the ref)
    feats += [hole_way([(i * 100, 2000), (i * 100, 2400)], ref=str(i + 1), osm_id=200 + i) for i in (0, 8, 9, 17)]
    fc, notes = RT.prepare_osm(dict(features=feats), pkg_of())
    ways = [f for f in fc["features"] if f["properties"].get("golf") == "hole"]
    assert len(ways) == 18
    assert sorted(f["properties"]["osm_id"] for f in ways) == list(range(100, 118))
    assert {f["properties"]["ref"] for f in ways} == {str(i + 1) for i in range(18)}
    assert any("neighbour" in n or "no package hole" in n for n in notes)


def test_osm_refs_follow_the_package_holes_by_geometry():
    """The build renumbers OSM holes (renumber_holes / hole_renumber); retee must use the package's numbering."""
    feats = [hole_way([(i * 100, 0), (i * 100, 400)], ref=str((i + 1) % 18 + 1), osm_id=100 + i) for i in range(18)]
    fc, _ = RT.prepare_osm(dict(features=feats), pkg_of())
    by_id = {f["properties"]["osm_id"]: f["properties"]["ref"] for f in fc["features"]}
    assert all(by_id[100 + i] == str(i + 1) for i in range(18))


def test_package_hole_without_a_matching_way_gets_no_line():
    feats = [hole_way([(i * 100, 0), (i * 100, 400)], ref=str(i + 1), osm_id=100 + i) for i in range(17)]
    feats.append(hole_way([(5000, 0), (5000, 400)], ref="18", osm_id=117))      # far from the package's 18
    fc, notes = RT.prepare_osm(dict(features=feats), pkg_of())
    refs = [f["properties"]["ref"] for f in fc["features"] if f["properties"].get("golf") == "hole"]
    assert "18" not in refs and len(refs) == 17
    assert any("18" in n for n in notes)


# ----------------------------------------------------------------------------- sanity guard
def pos_at(x, y, s="Blue"):
    lon, lat = ll(x, y)
    return {"tees": {s: dict(lon=lon, lat=lat, method="walkback")}}


def test_guard_keeps_package_tee_on_a_big_move():
    pkg = pkg_of(2)
    pos = {"1": pos_at(0, -1200), "2": pos_at(100, -10)}            # 1: 1,200 yds back; 2: 10 yds back (fine)
    out, kept = RT.guard_positions(pkg, pos)
    assert "Blue" not in out["1"]["tees"] and "Blue" in out["2"]["tees"]
    assert len(kept) == 1 and kept[0].startswith("1 Blue") and "moved" in kept[0]
    assert "Blue" in pos["1"]["tees"]                                 # input untouched


def test_guard_keeps_package_tee_when_card_deviation_exceeds_15pct():
    pkg = pkg_of(1)
    out, kept = RT.guard_positions(pkg, {"1": pos_at(0, -100)})       # 100 yds: < 150, but 500 vs 400 = 25 %
    assert "Blue" not in out["1"]["tees"] and "card" in kept[0]
    out, kept = RT.guard_positions(pkg, {"1": pos_at(0, -50)})        # 450 vs 400 = 12.5 %: allowed
    assert "Blue" in out["1"]["tees"] and not kept


def test_guard_allows_a_move_that_brings_a_stale_tee_closer_to_the_card():
    pkg = pkg_of(1)
    t = pkg["holes"]["1"]["tees"]["Blue"]
    t["tee_ll"], t["measured_yards"] = ll(0, 200), 200                 # package tee 50 % short of the card
    out, kept = RT.guard_positions(pkg, {"1": pos_at(0, 100)})         # 300 vs 400: still > 15 % but better
    assert "Blue" in out["1"]["tees"] and not kept


def test_retee_reports_guard(monkeypatch):
    pkg = pkg_of(1)
    sys.path.insert(0, os.path.join(CD, "tees"))
    import picks_localize as PL
    seen = {}
    monkeypatch.setattr(RT, "tee_positions", lambda *a: {"1": pos_at(0, -1500)})
    monkeypatch.setattr(PL, "retee", lambda p, pos, label: (seen.update(pos=pos) or copy.deepcopy(p), 0))
    out, msg = RT.retee(copy.deepcopy(pkg), "/nonexistent", "x")
    assert seen["pos"]["1"]["tees"] == {}                              # PL.retee keeps the package tee
    assert "guard kept 1 package tee" in msg and out["stages"]["retee_guard"][0].startswith("1 Blue")


# ----------------------------------------------------------------------------- pevely_farms regression
PEVELY = os.path.join(CD, "packages", "pevely_farms")


@pytest.mark.skipif(not os.path.exists(os.path.join(PEVELY, "raw", "osm.geojson")), reason="no pevely_farms raw OSM")
def test_pevely_farms_retee_stays_on_the_card():
    import json
    pkg = json.load(open(os.path.join(PEVELY, "package.json")))
    pos = RT.tee_positions(pkg, PEVELY, "pevely_farms")
    worst = 0.0
    for k in ("1", "9", "10", "18"):
        for s, r in pos[k]["tees"].items():
            d = RT.hav_yd(pkg["holes"][k]["tees"][s]["tee_ll"], [r["lon"], r["lat"]])
            worst = max(worst, d)
    assert worst < 60, f"S2 tees on 1/9/10/18 are {worst:.0f} yds from the committed package"
    out, msg = RT.retee(pkg, PEVELY, "pevely_farms")
    for k, h in out["holes"].items():
        for s, t in h["tees"].items():
            c = t.get("card_yards")
            assert RT.hav_yd(t["tee_ll"], pkg["holes"][k]["tees"][s]["tee_ll"]) <= RT.MAX_MOVE_YD, (k, s)
            if c:
                assert abs(t["measured_yards"] - c) <= max(0.15 * c, abs(pkg["holes"][k]["tees"][s]["measured_yards"] - c)) + 1, (k, s, t["measured_yards"], c)
