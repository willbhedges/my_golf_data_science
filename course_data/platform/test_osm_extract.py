"""Offline tests: the Geofabrik extract path (osm_extract.py) gives exactly the Overpass answer.

Parity: committed Overpass answers (packages/<slug>/raw/osm_raw.json, `out body geom`) are turned back into OSM XML
(every node / way / relation they contain, plus decoys the query must NOT return: objects outside the bbox, tags the
query does not ask for, untagged nodes); the extract path run on that XML must reproduce the committed
raw/osm.geojson feature for feature. With osmium installed the same goes through `osmium cat` -> .osm.pbf ->
`osmium extract` (the Actions path), skipped otherwise.
Resolve: a tiny state file with three courses + holes; resolve.resolve() with OSM_SOURCE=geofabrik finds, ranks
and outlines the course exactly as from Overpass, and auto mode falls back when Overpass raises.
"""
import json
import os
import shutil
import subprocess
import sys
from xml.sax.saxutils import quoteattr

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import fetch_course as fcm  # noqa: E402
import osm_extract as ox  # noqa: E402
import osm_guard as og  # noqa: E402
import platform_common as pc  # noqa: E402
import resolve as rs  # noqa: E402

PKG = os.path.join(pc.COURSE_DATA, "packages")
# courses whose committed osm.geojson is the plain Overpass answer (source "overpass", no supplement / snapshot)
PARITY = ("amana_colonies", "buffalo_dunes")
HAVE_OSMIUM = shutil.which("osmium") is not None


# ----------------------------------------------------------------------------- Overpass answer -> OSM XML
def overpass_to_osm(elements, snwe):
    """OSM XML holding every object of an `out body geom` answer (member ways it only shows as geometry get
    synthetic node ids) plus decoys just outside the bbox / with tags the query does not ask for."""
    nodes, ways, rels = {}, {}, {}
    nid = [10 ** 12]

    def new_node(lat, lon, tags=None):
        nid[0] += 1
        nodes[nid[0]] = (lat, lon, tags or {})
        return nid[0]
    for e in elements:
        if e["type"] == "node":
            nodes[e["id"]] = (e["lat"], e["lon"], e.get("tags", {}))
    for e in elements:
        if e["type"] == "way":
            for n, g in zip(e["nodes"], e["geometry"]):
                nodes.setdefault(n, (g["lat"], g["lon"], {}))
            ways[e["id"]] = (e["nodes"], e.get("tags", {}))
    for e in elements:
        if e["type"] != "relation":
            continue
        mem = []
        for m in e["members"]:
            if m["type"] == "way" and m["ref"] not in ways:
                ways[m["ref"]] = ([new_node(g["lat"], g["lon"]) for g in m.get("geometry", [])], {})
            elif m["type"] == "node" and m["ref"] not in nodes and "lat" in m:
                nodes[m["ref"]] = (m["lat"], m["lon"], {})
            mem.append((m["type"], m["ref"], m.get("role", "")))
        rels[e["id"]] = (mem, e.get("tags", {}))
    s, w, n, e_ = snwe
    out_lat, mid_lon = n + 0.003, (w + e_) / 2                         # ~330 m north of the box: inside the cut margin
    a, b, c = new_node(out_lat, mid_lon), new_node(out_lat + 0.001, mid_lon), new_node(out_lat, mid_lon + 0.001)
    ways[9 * 10 ** 11 + 1] = ([a, b, c, a], {"golf": "green"})        # golf area outside the bbox
    new_node(out_lat, mid_lon - 0.001, {"golf": "pin"})                # golf node outside the bbox
    lat0, lon0 = (s + n) / 2, (w + e_) / 2
    p, q, r = new_node(lat0, lon0), new_node(lat0 + 1e-4, lon0), new_node(lat0, lon0 + 1e-4)
    ways[9 * 10 ** 11 + 2] = ([p, q, r, p], {"amenity": "parking"})   # inside, but not a tag the query asks for
    new_node(lat0 + 2e-4, lon0, {"amenity": "bench"})                 # tagged node the query does not ask for
    rels[9 * 10 ** 11 + 3] = ([("way", 9 * 10 ** 11 + 1, "outer")], {"type": "multipolygon", "natural": "wood"})
    ln = [new_node(s - 0.002, w + 1e-4), new_node(n + 0.002, w + 1e-4)]   # crosses the box, no node inside
    ways[9 * 10 ** 11 + 4] = (ln, {"highway": "track"})
    return nodes, ways, rels, 9 * 10 ** 11 + 4


def write_osm(path, nodes, ways, rels):
    def tg(t):
        return "".join(f"<tag k={quoteattr(k)} v={quoteattr(str(v))}/>" for k, v in t.items())
    with open(path, "w") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<osm version="0.6" generator="test">\n')
        for i in sorted(nodes):
            lat, lon, t = nodes[i]
            fh.write(f'<node id="{i}" version="1" lat="{lat:.7f}" lon="{lon:.7f}">{tg(t)}</node>\n')
        for i in sorted(ways):
            nd, t = ways[i]
            fh.write(f'<way id="{i}" version="1">' + "".join(f'<nd ref="{n}"/>' for n in nd) + tg(t) + "</way>\n")
        for i in sorted(rels):
            mem, t = rels[i]
            fh.write(f'<relation id="{i}" version="1">' + "".join(
                f'<member type="{a}" ref="{b}" role={quoteattr(c)}/>' for a, b, c in mem) + tg(t) + "</relation>\n")
        fh.write("</osm>\n")


def committed(slug):
    raw = os.path.join(PKG, slug, "raw")
    data = pc.read_json(os.path.join(raw, "osm_raw.json"))
    fc = pc.read_json(os.path.join(raw, "osm.geojson"))
    snwe = tuple(pc.read_json(os.path.join(raw, "summary.json"))["bbox_wgs84_snwe"])
    for f in fc["features"]:
        f["properties"].pop("inside_course", None)
    return data, fc, snwe


def fixture(slug, tmp_path):
    data, fc, snwe = committed(slug)
    nodes, ways, rels, crossing = overpass_to_osm(data["elements"], snwe)
    p = str(tmp_path / f"{slug}.osm")
    write_osm(p, nodes, ways, rels)
    return p, data, fc, snwe, crossing


def norm(fc):
    return sorted((json.dumps(f, sort_keys=True) for f in fc["features"]))


# ----------------------------------------------------------------------------- the filters
def test_filters_mirror_the_overpass_query():
    f = ox.query_filters()
    keys = {(t, k, op, v) for t, k, op, v in f}
    assert (("node", "way", "relation"), "golf", None, None) in keys
    assert (("node", "way", "relation"), "leisure", "~", "golf_course|pitch|park") in keys
    assert (("way",), "highway", None, None) in keys and (("way",), "waterway", None, None) in keys
    # one filter per statement of the query
    assert len(f) == fcm.features_query((1, 2, 3, 4)).count("(1,2,3,4)")
    assert ox.tags_match("way", {"building": "yes"}, f)
    assert not ox.tags_match("node", {"building": "yes"}, f)          # `way["building"]` only
    assert ox.tags_match("relation", {"leisure": "golf_course"}, f)
    assert not ox.tags_match("way", {"amenity": "parking"}, f)


def test_filters_of_another_bbox_query():
    q = """[out:json][timeout:180];
    (
      nwr["building"](38.1,-94.2,38.2,-94.1);
      nwr["golf"="out_of_bounds"](38.1,-94.2,38.2,-94.1);
      nwr["boundary"="protected_area"](38.1,-94.2,38.2,-94.1);
    );
    out body geom;"""
    f = ox.query_filters(q)
    assert len(f) == 3 and f[1][1:] == ("golf", "=", "out_of_bounds")
    assert ox.tags_match("way", {"golf": "out_of_bounds"}, f) and not ox.tags_match("way", {"golf": "green"}, f)


def test_segment_crossing_counts_as_in_the_box():
    box = (0.0, 0.0, 1.0, 1.0)
    assert ox._line_hits_box([(-1, 0.5), (2, 0.5)], box)
    assert not ox._line_hits_box([(-1, 1.5), (2, 1.5)], box)
    assert ox._line_hits_box([(0.5, 0.5)], box)


# ----------------------------------------------------------------------------- parity with Overpass
@pytest.mark.parametrize("slug", PARITY)
def test_extract_xml_reproduces_the_overpass_geojson(slug, tmp_path):
    p, data, fc, snwe, crossing = fixture(slug, tmp_path)
    got = ox.features_from_osm_file(p, snwe)
    want_ids = [(e["type"], e["id"]) for e in data["elements"]]
    got_ids = [(e["type"], e["id"]) for e in got["elements"]]
    assert ("way", crossing) in got_ids                                # Overpass bbox semantics: segment crossing
    got_ids.remove(("way", crossing))
    assert got_ids == want_ids                                         # same objects, same order
    gj = fcm.to_geojson([e for e in got["elements"] if e["id"] != crossing])
    assert norm(gj) == norm(fc)                                        # the committed raw/osm.geojson
    assert og.golf_counts(gj) == og.golf_counts(fc)


@pytest.mark.skipif(not HAVE_OSMIUM, reason="osmium-tool not installed")
@pytest.mark.parametrize("slug", PARITY)
def test_osmium_pbf_path_reproduces_the_overpass_geojson(slug, tmp_path, monkeypatch):
    p, data, fc, snwe, crossing = fixture(slug, tmp_path)
    st = "IA" if slug == "amana_colonies" else "KS"
    monkeypatch.setenv("OSM_PBF_DIR", str(tmp_path / "gf"))
    os.makedirs(tmp_path / "gf")
    subprocess.run(["osmium", "cat", p, "-o", ox.pbf_path(st), "--overwrite"], check=True, capture_output=True)
    got = ox.features_data(st, snwe)
    gj = fcm.to_geojson([e for e in got["elements"] if e["id"] != crossing])
    assert norm(gj) == norm(fc)
    assert not [f for f in os.listdir(tmp_path / "gf") if f.startswith("cut_")]   # the cut is cleaned up


def test_guard_uses_the_extract_when_every_mirror_fails(tmp_path, monkeypatch):
    p, data, fc, snwe, crossing = fixture("amana_colonies", tmp_path)
    monkeypatch.setattr(ox, "_failed_overpass", [False])

    def down(url, q, timeout):
        raise RuntimeError("ReadTimeout")
    course = dict(state="IA", osm=dict(type="way", id=1))
    d, gj, prov = og.fetch_guarded(snwe, course, post=down, snapshots=[], sleep=lambda s: None,
                                   extract=lambda st, b: ox.features_from_osm_file(p, b, "2026-11-01T20:00:00Z"))
    assert prov["source"] == "geofabrik" and prov["mirror"] == "geofabrik:IA" and prov["reason"] == "complete"
    assert prov["osm_base"] == "2026-11-01T20:00:00Z"
    assert norm(dict(features=[f for f in gj["features"] if f["properties"]["osm_id"] != crossing])) == norm(fc)
    assert len(prov["attempts"]) == 3 * len(og.MIRRORS) + 1


def test_guard_forced_geofabrik_skips_overpass(tmp_path, monkeypatch):
    p, data, fc, snwe, _ = fixture("amana_colonies", tmp_path)
    monkeypatch.setenv("OSM_SOURCE", "geofabrik")
    called = []
    d, gj, prov = og.fetch_guarded(snwe, dict(state="IA"), post=lambda *a: called.append(a), snapshots=[],
                                   extract=lambda st, b: ox.features_from_osm_file(p, b))
    assert not called and prov["source"] == "geofabrik" and prov["mirrors_tried"] == ["geofabrik:IA"]


def test_guard_without_pbf_dir_never_reaches_for_the_extract(monkeypatch):
    monkeypatch.delenv("OSM_PBF_DIR", raising=False)
    monkeypatch.delenv("OSM_SOURCE", raising=False)
    assert not ox.allowed()
    with pytest.raises(RuntimeError):
        og.fetch_guarded((0, 0, 1, 1), dict(state="IA"), post=lambda *a: (_ for _ in ()).throw(RuntimeError("x")),
                         snapshots=[], sleep=lambda s: None)


# ----------------------------------------------------------------------------- resolve from the extract
def square(lat, lon, d):
    return [(lat, lon), (lat + d, lon), (lat + d, lon + d), (lat, lon + d)]


def state_file(path):
    """Three courses: 'The Plantation Course at Kapalua' (way, 3 holes), 'Bay Course' (multipolygon relation,
    1 hole), an unnamed course node."""
    nodes, ways, rels, k = {}, {}, {}, [100]

    def nd(lat, lon, t=None):
        k[0] += 1
        nodes[k[0]] = (lat, lon, t or {})
        return k[0]

    def ring(pts):
        ids = [nd(*p) for p in pts]
        return ids + ids[:1]
    ways[1] = (ring(square(21.00, -156.66, 0.01)), {"leisure": "golf_course", "name": "The Plantation Course at Kapalua",
                                                    "addr:city": "Lahaina"})
    ways[2] = (ring(square(21.02, -156.64, 0.01)), {})
    rels[3] = ([("way", 2, "outer")], {"type": "multipolygon", "leisure": "golf_course", "name": "Bay Course"})
    for i in range(3):
        ways[10 + i] = ([nd(21.002 + i * 0.002, -156.658), nd(21.003 + i * 0.002, -156.652)],
                        {"golf": "hole", "ref": str(i + 1)})
    ways[20] = ([nd(21.022, -156.638), nd(21.025, -156.635)], {"golf": "hole", "ref": "1"})
    nd(21.10, -156.70, {"leisure": "golf_course"})
    write_osm(path, nodes, ways, rels)
    return path


def test_state_index_queries(tmp_path):
    ix = ox.StateIndex.from_file(state_file(str(tmp_path / "HI.golf.osm")))
    assert [e["id"] for e in ix.by_name(pc.name_regex("Kapalua Plantation"))] == []      # words out of order
    assert [e["id"] for e in ix.by_name("kapalua", "plantation")] == [1]
    assert [e["id"] for e in ix.by_name(pc.name_regex("bay"))] == [3]
    el = ix.by_name("bay")[0]
    assert el["type"] == "relation" and el["bounds"]["minlat"] == 21.02 and el["center"]["lat"] == pytest.approx(21.025)
    assert ix.hole_count("way", 1) == 3 and ix.hole_count("relation", 3) == 1
    assert [e["id"] for e in ix.enclosing(21.005, -156.655)] == [1]
    assert sorted(e["id"] for e in ix.around(21.0, -156.67, 1500)) == [1]
    assert sorted(e["type"] for e in ix.around(21.05, -156.66, 9000)) == ["node", "relation", "way"]
    g = ix.body_geom("relation", 3)
    assert g["members"][0]["geometry"][0] == dict(lat=21.02, lon=-156.64)


def test_resolve_from_the_extract(tmp_path, monkeypatch):
    ix = ox.StateIndex.from_file(state_file(str(tmp_path / "HI.golf.osm")))
    monkeypatch.setattr(ox, "_INDEX", {"HI": ix})
    monkeypatch.setattr(pc, "nominatim", lambda *a, **k: None)
    monkeypatch.setenv("OSM_SOURCE", "geofabrik")

    def no_overpass(*a, **k):
        raise AssertionError("Overpass called in geofabrik mode")
    monkeypatch.setattr(pc, "overpass", no_overpass)
    r = rs.resolve("Kapalua Plantation Course", "HI", town="Lahaina")
    assert r["status"] == "ok" and r["osm"] == dict(type="way", id=1)
    assert r["holes_mapped"] == 3 and r["town"] == "Lahaina"
    assert r["boundary"]["type"] == "Polygon" and len(r["boundary"]["coordinates"][0]) == 5
    assert r["bbox"] == pytest.approx([-156.66, 21.0, -156.65, 21.01])


def test_resolve_auto_falls_back_when_overpass_fails(tmp_path, monkeypatch):
    ix = ox.StateIndex.from_file(state_file(str(tmp_path / "HI.golf.osm")))
    monkeypatch.setattr(ox, "_INDEX", {"HI": ix})
    monkeypatch.setattr(ox, "_failed_overpass", [False])
    monkeypatch.setattr(pc, "nominatim", lambda *a, **k: None)
    monkeypatch.setenv("OSM_SOURCE", "auto")
    monkeypatch.setenv("OSM_PBF_DIR", str(tmp_path))
    calls = []

    def down(q, **kw):
        calls.append(kw)
        raise RuntimeError("all Overpass endpoints failed: ReadTimeout")
    monkeypatch.setattr(pc, "overpass", down)
    r = rs.resolve("Bay Course", "HI")
    assert r["status"] == "ok" and r["osm"] == dict(type="relation", id=3) and r["holes_mapped"] == 1
    assert calls == [{"tries": 1}]                       # one failed pass, then the extract for everything else
    assert ox.forced()
