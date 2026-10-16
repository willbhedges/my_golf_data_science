"""Offline tests: package build from saved Spirit Hollow fixtures (OSM + scorecard), course module API,
fallbacks, gap-fill hook, elevation maths and the workflow's request plan."""
import importlib.util
import json
import math
import os
import shutil
import sys
import types

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import package as pk  # noqa: E402
import platform_common as pc  # noqa: E402
import run_requests  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
CARD = os.path.join(FIX, "spirit_hollow_scorecard.json")
BLACK = [391, 507, 148, 532, 384, 408, 154, 383, 365, 502, 338, 186, 409, 393, 145, 378, 445, 521]


def seed(tmp_path, slug="spirit_hollow"):
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    shutil.copy(os.path.join(FIX, "spirit_hollow_osm.geojson"), src / "osm.geojson")
    shutil.copy(os.path.join(FIX, "spirit_hollow_summary.json"), src / "summary.json")
    import fetch_package as fp
    pkg = tmp_path / slug
    fp.seed_from_dir(str(src), str(pkg))
    return str(pkg)


@pytest.fixture(scope="module")
def black(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("sh")
    pkg = seed(tmp)
    req = dict(course="Spirit Hollow", state="IA", tee_set="Black", scorecard=CARD)
    package = pk.build_package(req, pkg, gapfill=False)
    pk.write(package, pkg)
    return package, pkg


def test_package_contract(black):
    p, _ = black
    assert p["schema"] == "course_package/1" and p["frame"] == "yard"
    assert p["course"]["osm"] == dict(type="relation", id=13353211)
    assert p["tee_set"] == "Black" and p["scorecard"]["kind"] == "file"
    assert set(p["tee_sets"]) == {"Gold", "Black", "White", "Rust"}
    assert len(p["holes"]) == 18
    for k, h in p["holes"].items():
        assert h["tee"] == [0.0, 0.0] and h["dot270"] == [0.0, -270.0]
        assert 0 <= h["bearing_deg"] < 360 and 0 <= h["green_bearing_deg"] < 360
        assert len(h["tee_ll"]) == 2 and -92 < h["tee_ll"][0] < -91 and 40.7 < h["tee_ll"][1] < 40.8
        assert h["green"][1] < 0                                  # green is up the tee line
        assert {"tee", "green", "par", "length", "zones", "bearing"} <= set(h["provenance"])
        assert 0 < h["confidence"]["score"] <= 1
        assert len(h["zone_src"]) == len(h["zones"])
        assert set(h["tees"]) == {"Gold", "Black", "White", "Rust"} and h["yards"]["Black"] == BLACK[int(k) - 1]
        assert h["tee_ll"] == h["tees"]["Black"]["tee_ll"] and h["bearing_deg"] == h["tees"]["Black"]["bearing_deg"]
        assert h["zones_ll"] and all(set(z) == {"lie", "poly", "src", "p"} for z in h["zones_ll"])
        assert -92 < h["zones_ll"][0]["poly"][0][0] < -91 and len(h["green_polygon_ll"]) >= 3
        assert 0 <= h["exposure"] <= 1
        assert h["pixel"]["ppy"] > 0 and len(h["pixel"]["tee_px"]) == 2


def test_black_tees_match_the_card(black):
    p, _ = black
    lengths = [p["holes"][str(i + 1)]["length"] for i in range(18)]
    assert lengths == BLACK                                        # card convention
    measured = [p["holes"][str(i + 1)]["measured_length"] for i in range(18)]
    off = [abs(m - c) for m, c in zip(measured, BLACK)]
    assert sum(o <= 15 for o in off) >= 16, off                    # OSM boxes at the card yardage
    pars = [p["holes"][str(i + 1)]["par"] for i in range(18)]
    assert pars == [4, 5, 3, 5, 4, 4, 3, 4, 4, 5, 4, 3, 4, 4, 3, 4, 4, 5]
    assert sorted(k for k, h in p["holes"].items() if h.get("par3")) == ["12", "15", "3", "7"]


def test_bearing_matches_geometry(black):
    p, _ = black
    h = p["holes"]["1"]
    lon0, lat0 = h["tee_ll"]
    lon1, lat1 = h["aim_ll"]
    de = (lon1 - lon0) * math.cos(math.radians(lat0))
    dn = lat1 - lat0
    approx = math.degrees(math.atan2(de, dn)) % 360
    assert abs(approx - h["bearing_deg"]) < 0.5


def test_reframe_other_tee_set(black):
    p, _ = black
    g = pk.reframe(p, "Gold")
    assert g["tee_set"] == "Gold" and p["tee_set"] == "Black"           # input untouched
    for k in ("1", "10", "18"):
        assert g["holes"][k]["length"] == g["holes"][k]["yards"]["Gold"]
        assert g["holes"][k]["tee_ll"] != p["holes"][k]["tee_ll"]
        # the green is further up the line from the Gold tee
        assert -g["holes"][k]["green"][1] > -p["holes"][k]["green"][1]
    b = pk.reframe(g, "Black")                                         # round trip: same yard view
    for k in p["holes"]:
        assert b["holes"][k]["green"] == p["holes"][k]["green"]
        assert len(b["holes"][k]["zones"]) == len(p["holes"][k]["zones"])


def test_course_module_api(black):
    p, pkg = black
    spec = importlib.util.spec_from_file_location("ca_test", os.path.join(pkg, "course_auto.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert m.ORDER == list(range(1, 19))
    assert set(m.PAR3) == {3, 7, 12, 15} and len(m.HOLES) == 14
    for name in ("HOLES", "PAR3", "NOTES", "AIM_AT", "ORDER", "LABELS", "APP", "GREEN_SIDE"):
        assert hasattr(m, name)
    h = m.HOLES[1]
    # tee_strategy.hole_frame: 270 yds up the line at the hole's px/yd
    tee, d270 = np.array(h["tee"]), np.array(h["dot270"])
    assert abs(np.linalg.norm(d270 - tee) / 270 - h["px_per_yd"]) < 1e-3
    assert d270[0] == pytest.approx(tee[0]) and d270[1] < tee[1]
    # the green in pixels maps back to the yard-frame green
    g_y = np.array(p["holes"]["1"]["green"])
    assert np.allclose((np.array(h["green"]) - tee) / h["px_per_yd"], g_y, atol=0.1)
    for lie, poly in h["zones"]:
        assert lie in ("ob", "native", "recovery", "fairway", "water", "sand") and len(poly) >= 3
    p3 = m.PAR3[15]
    assert {"tee", "flag", "center", "front", "back", "green", "haz", "note", "short"} <= set(p3)
    assert p3["front"] < p3["center"] < p3["back"]


def test_lie_at_compatible(black):
    """mozingo/tee_strategy.lie_at semantics: later zones win, default rough."""
    _, pkg = black
    sys.path.insert(0, os.path.join(pc.ROOT, "mozingo"))
    spec = importlib.util.spec_from_file_location("ca_test2", os.path.join(pkg, "course_auto.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    from matplotlib.path import Path
    h = m.HOLES[10]
    tee, d270 = np.array(h["tee"]), np.array(h["dot270"])
    pts = tee + (d270 - tee) * np.linspace(0.8, 1.1, 7)[:, None]
    lie = np.array(["rough"] * len(pts), dtype=object)
    for name, poly in h["zones"]:
        lie[Path(poly).contains_points(pts)] = name
    assert (lie == "fairway").any()                                 # hole 10's fairway is on the line


def test_no_scorecard_falls_back_to_back_tee(tmp_path):
    pkg = seed(tmp_path)
    p = pk.build_package(dict(course="Spirit Hollow", state="IA", tee_set="White", local_scorecard=False), pkg,
                         gapfill=False)
    assert p["tee_set"] == "osm_back" and p["scorecard"]["kind"] is None
    assert any("no scorecard" in w for w in p["warnings"])
    assert all("hole-line start" in h["tee_choice"] for h in p["holes"].values())
    assert all(h["length"] == h["measured_length"] for h in p["holes"].values())


def test_request_yardages_and_unknown_set(tmp_path):
    pkg = seed(tmp_path)
    white = [376, 452, 134, 501, 361, 365, 136, 365, 323, 457, 305, 163, 389, 370, 132, 331, 397, 483]
    p = pk.build_package(dict(course="Spirit Hollow", state="IA", tee_set="White", yardages=white), pkg, gapfill=False)
    assert p["scorecard"]["kind"] == "request" and p["tee_set"] == "White"
    assert [p["holes"][str(i + 1)]["length"] for i in range(18)] == white
    p2 = pk.build_package(dict(course="Spirit Hollow", state="IA", tee_set="Purple", scorecard=CARD), pkg, gapfill=False)
    assert p2["tee_set"] == "Gold" and any("not on the card" in w for w in p2["warnings"])


def test_gapfill_hook_adds_zones_and_imagery_share(tmp_path, monkeypatch):
    pkg = seed(tmp_path)
    calls = {}

    def gapfill(package, imagery_dir):
        calls["dir"] = imagery_dir
        out = json.loads(json.dumps(package))
        for h in out["holes"].values():                           # a tree block right of the landing zone
            fr = pk._frame(h["tee_ll"], h["aim_ll"])
            ring = fr.yds_to_ll(np.array([[15, -230], [60, -230], [60, -330], [15, -330]], float)).tolist()
            h["zones_ll"].append(dict(lie="recovery", poly=ring, src="vision:test", p=0.9))
            # vision may also try to override a fairway: reframe's lie order keeps fairway on top
            h["zones_ll"].append(dict(lie="native", poly=ring, src="vision:test", p=0.8))
        return out
    monkeypatch.setitem(pk._MODS, "cdp_vision_gapfill", types.SimpleNamespace(gapfill=gapfill))
    img = tmp_path / "img"
    img.mkdir()
    (img / "georef.json").write_text(json.dumps({"imagery": {"source": "test", "year": 2023, "files": {}}}))
    p = pk.build_package(dict(course="Spirit Hollow", state="IA", tee_set="Black", scorecard=CARD,
                              imagery_dir=str(img)), pkg)
    assert calls["dir"] == str(img)
    assert p["stages"]["vision"].startswith("ok")
    h = p["holes"]["1"]
    assert h["confidence"]["imagery"] > 0 and h["landing_lies"].get("recovery", 0) > 0
    assert h["provenance"]["zones"]["recovery"] == "vision"
    assert any(z["src"] == "vision:test" for z in h["zones_ll"]) and "vision:test" in h["zone_src"]
    assert h["exposure"] > 0
    assert p["coverage"]["summary"]["holes_with_trees_or_long_grass_in_landing_zone"] >= 10


def test_gapfill_missing_is_reported(black):
    p, _ = black
    assert "vision" not in p["stages"] or "missing" in p["stages"]["vision"] or "skipped" in p["stages"]["vision"]


def test_elevation_plane():
    """A plane rising 2% along the line and 3% to the right, in the yard frame."""
    h = dict(ref="4", par=4, length=400, measured_length=400, green=[0.0, -400.0], bearing_deg=0.0)

    def yds_to_ll(xy):                                             # identity 'lonlat' = yard frame
        return np.atleast_2d(xy)

    def sample(ll):
        ll = np.atleast_2d(ll)
        along, right = -ll[:, 1], ll[:, 0]
        return 100.0 + (0.02 * along + 0.03 * right) * 0.9144     # metres
    e = pk.elevation_for_hole(h, sample, yds_to_ll)
    assert e["landing_slope"]["along_pct"] == pytest.approx(2.0, abs=0.05)
    assert e["landing_slope"]["cross_pct"] == pytest.approx(3.0, abs=0.05)
    assert e["landing"]["270"]["delta_ft"] == pytest.approx(0.02 * 270 * 3, abs=0.2)   # 5.4 yds = 16.2 ft
    assert e["green"]["delta_ft"] == pytest.approx(0.02 * 400 * 3, abs=0.2)
    if "adjustments" in e:                                          # elevation/adjust.py present
        assert e["adjustments"]["clubs"]["Driver"]["carry_delta_yds"] < 0          # uphill flies shorter


def test_coverage_counts(black):
    p, _ = black
    f = p["coverage"]["features"]
    assert f["golf=hole"] == 18 and f["golf=tee"] == 103 and f["golf=bunker"] == 50
    assert f.get("trees_polygons", 0) == 0
    s = p["coverage"]["summary"]
    assert s["greens_found"] == 18 and s["of_par4_5"] == 14 and 0 < s["osm_score"] < 1


def test_qa_md(black):
    _, pkg = black
    md = open(os.path.join(pkg, "qa.md")).read()
    assert "| 18 | 5 | 521 /" in md and "## Coverage" in md


def test_missing_raw_is_a_clear_error(tmp_path):
    with pytest.raises(SystemExit, match="fetch_package"):
        pk.build_package(dict(course="X", state="IA"), str(tmp_path / "nothing"))


def test_run_requests_plan(tmp_path, monkeypatch):
    monkeypatch.setattr(pc, "PACKAGES", str(tmp_path))
    req = tmp_path / "reqs"
    req.mkdir()
    for n in ("package_a.json", "package_b.json", "survey_x.json"):
        (req / n).write_text("{}")
    (tmp_path / "b" / "raw").mkdir(parents=True)
    (tmp_path / "b" / "raw" / "osm.geojson").write_text("{}")
    rel = lambda n: os.path.relpath(str(req / n), pc.ROOT)          # noqa: E731
    reqs = [str(req / n) for n in ("package_a.json", "package_b.json", "survey_x.json")]
    plan = dict((os.path.basename(p), a) for p, a in run_requests.plan([rel("package_b.json")], reqs))
    assert plan == {"package_a.json": "fetch", "package_b.json": "fetch", "survey_x.json": "skip"}
    plan = dict((os.path.basename(p), a) for p, a in run_requests.plan(["course_data/platform/package.py"], reqs))
    assert plan == {"package_a.json": "fetch", "package_b.json": "build", "survey_x.json": "skip"}
    plan = dict((os.path.basename(p), a) for p, a in run_requests.plan([rel("survey_x.json")], reqs))
    assert plan["package_b.json"] == "skip" and plan["survey_x.json"] == "survey"
