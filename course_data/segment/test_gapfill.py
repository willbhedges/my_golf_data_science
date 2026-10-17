"""Unit tests for the segment gap-fill rules (no model, no rasters): python3 -m pytest course_data/segment/test_gapfill.py"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gapfill as G  # noqa: E402

LON0, LAT0 = -93.65, 42.04
M_LON = 1 / (111320 * 0.7431)     # degrees per metre at 42 N
M_LAT = 1 / 110950


def sq(x0, y0, w, h):
    """[[lon, lat]...] rectangle, metres from the origin."""
    return [[LON0 + x * M_LON, LAT0 + y * M_LAT] for x, y in ((x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0))]


def feat(cls, ring, p=0.9, src="segment:ariadgolf-v4@abc"):
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {"class": cls, "src": src, "p": p}}


def package():
    line = [[LON0, LAT0 + 0 * M_LAT], [LON0, LAT0 + 400 * M_LAT]]
    return {"course": {"center": [LON0, LAT0]}, "stages": {}, "sources": {}, "holes": {
        "1": {"hole_line_ll": line, "green_ll": line[-1], "provenance": {"green": "osm_green"},
              "green_polygon_ll": sq(-10, 390, 20, 20), "tees": {},
              "zones_ll": [{"lie": "fairway", "poly": sq(-20, 150, 40, 100), "src": "osm", "p": 1.0},
                           {"lie": "sand", "poly": sq(25, 200, 8, 8), "src": "osm", "p": 1.0}]}}}


def run(feats, pkg=None, scope="course"):
    with tempfile.NamedTemporaryFile("w", suffix=".geojson", delete=False) as fh:
        json.dump({"type": "FeatureCollection", "features": feats, "properties": {"model_sha": "abc"}}, fh)
    try:
        return G.segment_gapfill(pkg or package(), fh.name, reframe=False, scope=scope, log=lambda *a: None)
    finally:
        os.unlink(fh.name)


def added(out):
    return [z for z in out["holes"]["1"]["zones_ll"] if z.get("gapfill")]


def test_mapped_fairway_not_overridden_but_unmapped_one_added():
    out = run([feat("fairway", sq(-22, 148, 44, 104)),          # = the OSM fairway (slightly bigger)
               feat("fairway", sq(-20, 280, 40, 60))])          # a second fairway OSM lacks
    a = added(out)
    assert len(a) == 1 and a[0]["lie"] == "fairway" and a[0]["src"].startswith("segment:")
    assert all(z["src"] == "osm" for z in out["holes"]["1"]["zones_ll"] if not z.get("gapfill"))


def test_bunker_overlapping_osm_skipped_new_bunker_added():
    out = run([feat("bunker", sq(26, 201, 7, 7)), feat("bunker", sq(-35, 220, 8, 8))])
    a = added(out)
    assert len(a) == 1 and a[0]["lie"] == "sand"


def test_unet_water_ignored_nir_water_added_and_low_p_dropped():
    out = run([feat("water", sq(40, 300, 30, 30)),                               # U-Net water: never used
               feat("water", sq(-80, 300, 45, 45), src="segment:nir", p=0.8),
               feat("bunker", sq(-35, 100, 8, 8), p=0.3)])                        # below MIN_P
    a = added(out)
    assert [z["lie"] for z in a] == ["water"] and a[0]["src"] == "segment:nir"


def test_green_only_when_osm_has_none():
    pkg = package()
    out = run([feat("green", sq(-12, 388, 24, 24))], pkg)
    assert out["holes"]["1"]["green_polygon_ll"] == pkg["holes"]["1"]["green_polygon_ll"]
    pkg["holes"]["1"].pop("green_polygon_ll")
    pkg["holes"]["1"]["provenance"]["green"] = "hole_line_end"
    out = run([feat("green", sq(-12, 388, 24, 24))], pkg)
    assert out["holes"]["1"]["provenance"]["green"] == "segment"


def test_provenance_fields():
    out = run([feat("fairway", sq(-20, 280, 40, 60))])
    assert out["stages"]["segment"].startswith("ok: segment gap-fill")
    assert "licence" in out["sources"]["segment"]
    assert any("segment gap-fill" in f for f in out["holes"]["1"]["flags"])


def test_hole_scope_leaves_mapped_holes_alone_and_fills_poorly_mapped_ones():
    f = [feat("fairway", sq(-20, 280, 40, 60)), feat("bunker", sq(-35, 220, 8, 8))]
    assert added(run(f, scope="hole")) == []                     # hole 1 has OSM fairway + sand
    pkg = package()
    pkg["holes"]["1"]["zones_ll"] = []                           # poorly mapped hole
    assert sorted(z["lie"] for z in added(run(f, pkg, scope="hole"))) == ["fairway", "sand"]
