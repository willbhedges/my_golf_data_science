"""Offline tests for national_index.py (tiled fetch, incremental writes, counts, tiers, merge)."""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import national_index as ni  # noqa: E402


def course_json(st_area=True, holes=18):
    """A fake Overpass answer: one way course with a full hole set, one node-only course, a place."""
    els = []
    if st_area:
        els.append({"type": "area", "id": 3600000001})
    els.append({"type": "way", "id": 10, "center": {"lat": 40.05, "lon": -91.05},
                "tags": {"leisure": "golf_course", "name": "Test Hollow Golf Course"}})
    els.append({"type": "node", "id": 11, "lat": 40.3, "lon": -91.3,
                "tags": {"leisure": "golf_course", "name": "Node Only Golf Club"}})
    els.append({"type": "way", "id": 10, "bounds": {"minlat": 40.0, "minlon": -91.1, "maxlat": 40.1,
                                                    "maxlon": -91.0}})
    els.append({"type": "node", "id": 11, "lat": 40.3, "lon": -91.3})      # `out ids bb` of a node: no tags
    for h in range(1, holes + 1):
        lat, lon = 40.0 + h * 0.005, -91.05
        els.append({"type": "way", "id": 1000 + h, "center": {"lat": lat, "lon": lon},
                    "tags": {"golf": "hole", "ref": str(h) if h != 5 else "Hole 5"}})
        els.append({"type": "way", "id": 2000 + h, "center": {"lat": lat, "lon": lon + 0.001},
                    "tags": {"golf": "green"}})
        els.append({"type": "node", "id": 3000 + h, "lat": lat, "lon": lon - 0.001, "tags": {"golf": "tee"}})
        els.append({"type": "way", "id": 4000 + h, "center": {"lat": lat, "lon": lon}, "tags": {"golf": "fairway"}})
        els.append({"type": "node", "id": 5000 + h, "lat": lat, "lon": lon + 0.001, "tags": {"golf": "pin"}})
    els.append({"type": "node", "id": 9, "lat": 40.06, "lon": -91.2, "tags": {"place": "town", "name": "Testville"}})
    return {"elements": els, "osm3s": {"timestamp_osm_base": "2026-11-01T00:00:00Z"}}


def test_slim_joins_bbox_and_drops_tagless():
    rows = ni.slim_elements(course_json())
    c = [r for r in rows if r["g"].get("leisure")]
    assert {r["id"] for r in c} == {10, 11}
    assert [r for r in c if r["id"] == 10][0]["bb"] == [40.0, -91.1, 40.1, -91.0]
    assert "bb" not in [r for r in c if r["id"] == 11][0]


def ia(lat, lon, addr=None):
    return "IA" if 40 <= lat <= 43.5 and -96.7 <= lon <= -90 else None


def test_build_state_counts_and_tier():
    rows = ni.build_rows(ni.slim_elements(course_json()), ia)
    by = {r["name"]: r for r in rows}
    t = by["Test Hollow Golf Course"]
    assert (t["osm_holes"], t["greens"], t["tees"], t["fairways"], t["pins"], t["outline"]) == (18, 18, 18, 18, 18, 1)
    assert t["holes"] == 18 and t["city"] == "Testville" and t["state"] == "IA"
    assert ni.tier(t) == "B"
    assert ni.tier(dict(t, card="oga")) == "A"
    n = by["Node Only Golf Club"]
    assert n["outline"] == 0 and ni.tier(n) == "D"
    assert ni.tier(dict(t, osm_holes=12)) == "C"
    assert ni.build_rows(ni.slim_elements(course_json()), lambda *a: None) == []      # outside the US: dropped


def test_hole_refs():
    assert ni.hole_ref("Hole 07") == "7"
    assert ni.hole_ref("Red 3") == "red3"
    assert ni.hole_ref("x-y") is None


def test_cells_cover_states_once():
    allc = ni.cells_for(ni.STATES)
    assert len(allc) == len(set(allc)) and 1000 < len(allc) < 1600
    for st in ("MO", "AK", "DC", "TX"):
        s, w, n, e = ni.STATE_BBOX[st]
        cs = ni.state_cells(st)
        assert min(c[0] for c in cs) <= s and max(c[2] for c in cs) >= n
        assert min(c[1] for c in cs) <= w and max(c[3] for c in cs) >= e
    shards = [ni.shard_cells(ni.STATES, i, 6) for i in range(6)]
    assert sorted(c for sh in shards for c in sh) == allc


class FakeMirrors(ni.Mirrors):
    def __init__(self, answer):
        super().__init__(0, post=answer, sleep=lambda s: None)


def test_fetch_is_incremental_and_splits(tmp_path, monkeypatch):
    monkeypatch.setitem(ni.STATE_BBOX, "IA", (40.2, -91.8, 40.8, -91.2))     # one 1-degree cell
    calls = []

    def post(url, q, timeout):
        calls.append(q)
        if "(40.0000,-92.0000,41.0000,-91.0000)" in q:
            raise TimeoutError("too slow")               # the whole cell fails on every mirror -> split in four
        if "(40.0000,-91.5000,40.5000,-91.0000)" in q:
            return course_json()
        return {"elements": []}
    left = ni.fetch(["IA"], str(tmp_path), budget_min=5, mirrors=FakeMirrors(post), sleep=lambda s: None)
    assert left == []
    d = tmp_path / "cells"
    assert len(list(d.glob("c_*.json"))) == 5                  # four quarters + the parent's split marker
    n_calls = len(calls)
    ni.fetch(["IA"], str(tmp_path), budget_min=5, mirrors=FakeMirrors(post), sleep=lambda s: None)
    assert len(calls) == n_calls                               # nothing fetched twice
    els, have = ni.load_cells(str(tmp_path))
    assert (40.0, -92.0, 41.0, -91.0) in have
    assert any(e["g"].get("name") == "Test Hollow Golf Course" for e in els)


def test_tired_mirror_rests():
    t = [0.0]
    seen = []

    def post(url, q, timeout):
        seen.append(url)
        if url == ni.OVERPASS[0]:
            raise TimeoutError("x")
        return {"elements": []}
    m = ni.Mirrors(0, post=post, now=lambda: t[0], sleep=lambda s: None)
    for _ in range(3):
        m.ask("q", 1)
    seen.clear()
    m.ask("q", 1)
    assert ni.OVERPASS[0] not in seen                          # resting after 3 failures in a row
    t[0] += ni.MIRROR_REST_S + 1
    m.order = list(ni.OVERPASS)
    seen.clear()
    m.ask("q", 1)
    assert seen[0] == ni.OVERPASS[0]


def test_partial_state_and_merge(tmp_path, monkeypatch):
    monkeypatch.setitem(ni.STATE_BBOX, "IA", (40.2, -91.8, 40.8, -90.2))     # two cells
    monkeypatch.setattr(ni, "STATES", ["IA", "MO"])

    def post(url, q, timeout):
        if "-92.0000" in q:
            return course_json()
        raise TimeoutError("down")
    left = ni.fetch(["IA"], str(tmp_path / "raw"), budget_min=5, mirrors=FakeMirrors(post), sleep=lambda s: None)
    assert left                                                # the east cell (and its quarters) failed
    for f in ("OUT_GZ", "OUT_READY", "LIB_INDEX"):
        monkeypatch.setattr(ni, f, str(tmp_path / f))
    monkeypatch.setattr(ni, "state_locator", lambda shapes: ia)
    rows = ni.merge(str(tmp_path / "raw"), [], shapes={})
    assert any(r["name"] == "Test Hollow Golf Course" for r in rows)
    ready = json.load(open(tmp_path / "OUT_READY"))
    assert "IA" in ready["partial_states"] and "MO" in ready["missing_states"]
    doc = json.load(gzip.open(tmp_path / "OUT_GZ", "rt"))
    assert doc["schema"] == "us_courses/2" and "fairways" in doc["fields"]


def test_state_locator_geojson(tmp_path):
    gj = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": n},
         "geometry": {"type": "Polygon", "coordinates": [[[w, s], [e, s], [e, n_], [w, n_], [w, s]]]}}
        for n, (s, w, n_, e) in [(ni._STATE_NAMES[k], ni.STATE_BBOX[k]) for k in ni.STATE_BBOX]]}
    p = tmp_path / "s.json"
    p.write_text(json.dumps(gj))
    loc = ni.state_locator(ni.load_state_shapes(str(p)))
    assert loc(38.9, -77.03) in ("DC", "MD", "VA")
    assert loc(38.9, -77.03, "DC") == "DC"
    assert loc(41.6, -93.6) == "IA"
    assert loc(52.0, -100.0) is None                           # Canada


def test_oga_card_and_readme_block(tmp_path, monkeypatch):
    rows = ni.build_rows(ni.slim_elements(course_json()), ia)
    d = tmp_path / "oga"
    d.mkdir()
    json.dump({"state": "IA", "courses": [{"name": "Test Hollow Golf Course", "state": "IA", "par": 72,
                                           "latitude": 40.05, "longitude": -91.05}]}, open(d / "oga_IA.json", "w"))
    monkeypatch.setattr(ni, "LIB_INDEX", str(tmp_path / "none.json"))
    listed, matched = ni.attach_cards(rows, [str(d)])
    assert (listed, matched) == (1, 1)
    for r in rows:
        r["tier"] = ni.tier(r)
    assert {r["name"]: r["tier"] for r in rows}["Test Hollow Golf Course"] == "A"
    ready = tmp_path / "ready.json"
    monkeypatch.setattr(ni, "OUT_READY", str(ready))
    ni.write_readiness(rows, "now", [], [], {}, {})
    rd = tmp_path / "README.md"
    rd.write_text("x\n<!-- NATIONAL_COUNTS -->\ny\n")
    ni.write_readme(str(rd), str(ready))
    ni.write_readme(str(rd), str(ready))                       # idempotent: the block is replaced, not repeated
    txt = rd.read_text()
    assert txt.count("<!-- NATIONAL_COUNTS -->") == 1 and "tier A" in txt and txt.endswith("y\n")


# ------------------------------------------------------------------------------------- Geofabrik state extracts
def osm_xml(holes=18):
    """A tiny `osmium tags-filter -f osm` output: a way course with 18 holes / greens / tees / pins, a relation
    course of two member ways, an unnamed course node (dropped, as the Overpass query drops it), a town."""
    nodes, ways = [], []
    nid = [100]

    def node(lat, lon, tags=None):
        nid[0] += 1
        t = "".join(f'<tag k="{k}" v="{v}"/>' for k, v in (tags or {}).items())
        nodes.append(f'<node id="{nid[0]}" version="1" lat="{lat}" lon="{lon}">{t}</node>')
        return nid[0]

    def way(wid, pts, tags=None):
        refs = [node(a, b) for a, b in pts]
        t = "".join(f'<tag k="{k}" v="{v}"/>' for k, v in (tags or {}).items())
        ways.append(f'<way id="{wid}" version="1">' + "".join(f'<nd ref="{r}"/>' for r in refs) + t + "</way>")
    way(10, [(40.0, -91.1), (40.1, -91.1), (40.1, -91.0), (40.0, -91.0), (40.0, -91.1)],
        {"leisure": "golf_course", "name": "Test Hollow Golf Course", "addr:city": "Testville"})
    for h in range(1, holes + 1):
        lat, lon = 40.0 + h * 0.005, -91.05
        way(1000 + h, [(lat - 0.001, lon), (lat + 0.001, lon)], {"golf": "hole", "ref": str(h)})
        way(2000 + h, [(lat, lon + 0.0009), (lat, lon + 0.0011), (lat + 0.0002, lon + 0.001)], {"golf": "green"})
        node(lat, lon - 0.001, {"golf": "tee"})
        node(lat, lon + 0.001, {"golf": "pin"})
    way(50, [(41.0, -92.0), (41.1, -92.0)])                              # relation members (untagged)
    way(51, [(41.1, -91.8), (41.2, -91.9)])
    node(40.3, -91.3, {"leisure": "golf_course"})                         # unnamed node course: dropped
    node(40.31, -91.31, {"leisure": "golf_course", "name": "Node Only Golf Club"})
    node(40.06, -91.2, {"place": "town", "name": "Testville"})
    node(40.07, -91.2, {"place": "hamlet", "name": "Tiny"})                # not a city / town / village
    rel = ('<relation id="70" version="1"><member type="way" ref="50" role="outer"/>'
           '<member type="way" ref="51" role="outer"/><member type="way" ref="999" role="outer"/>'
           '<tag k="leisure" v="golf_course"/><tag k="name" v="Relation Links"/><tag k="type" v="multipolygon"/>'
           '</relation>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<osm version="0.6" generator="osmium">'
            + "".join(nodes) + "".join(ways) + rel + "</osm>")


def test_osm_xml_rows_match_overpass_rows(tmp_path):
    p = tmp_path / "f.osm"
    p.write_text(osm_xml())
    rows = ni.osm_xml_rows(str(p))
    by = {(r["t"], r["id"]): r for r in rows}
    assert by[("w", 10)]["bb"] == [40.0, -91.1, 40.1, -91.0]
    assert (by[("w", 10)]["lat"], by[("w", 10)]["lon"]) == (40.05, -91.05)       # bbox centre, as `out center`
    assert by[("r", 70)]["bb"] == [41.0, -92.0, 41.2, -91.8]                     # union of the member ways found
    assert "bb" not in by[("w", 1001)] and by[("w", 1001)]["g"] == {"golf": "hole", "ref": "1"}
    names = {r["g"].get("name") for r in rows if r["g"].get("leisure")}
    assert names == {"Test Hollow Golf Course", "Node Only Golf Club", "Relation Links"}
    assert not any(r["g"].get("place") == "hamlet" for r in rows)
    assert not any(r["t"] == "w" and r["id"] in (50, 51) for r in rows)        # untagged members are not rows
    out = ni.build_rows(rows, ia)
    t = {r["name"]: r for r in out}["Test Hollow Golf Course"]
    assert (t["osm_holes"], t["greens"], t["tees"], t["pins"], t["outline"]) == (18, 18, 18, 18, 1)
    assert ni.tier(t) == "B"


def test_geofabrik_state_file_completes_the_state(tmp_path, monkeypatch):
    monkeypatch.setattr(ni, "STATES", ["IA", "MO"])
    got = []

    def download(url, path):
        got.append(url)
        if "missouri" in url:
            raise OSError("404")
        open(path, "w").write("pbf")

    def tags_filter(pbf, osm):
        open(osm, "w").write(osm_xml())
    left = ni.geofabrik(["IA", "MO"], str(tmp_path / "raw"), download=download, tags_filter=tags_filter,
                        sleep=lambda s: None)
    assert left == ["MO"]
    assert "https://download.geofabrik.de/north-america/us/iowa-latest.osm.pbf" in got
    assert (tmp_path / "raw" / "cells" / "s_IA.json").exists()
    assert not list((tmp_path / "raw").rglob("*.pbf")) and not list((tmp_path / "raw").rglob("*.osm"))
    n = len(got)
    ni.geofabrik(["IA"], str(tmp_path / "raw"), download=download, tags_filter=tags_filter, sleep=lambda s: None)
    assert len(got) == n                                       # a state already on disk is not downloaded again
    sts = set()
    els, have = ni.load_cells(str(tmp_path / "raw"), sts)
    assert sts == {"IA"} and not have
    for f in ("OUT_GZ", "OUT_READY", "LIB_INDEX"):
        monkeypatch.setattr(ni, f, str(tmp_path / f))
    monkeypatch.setattr(ni, "state_locator", lambda shapes: ia)
    rows = ni.merge(str(tmp_path / "raw"), [], shapes={})
    assert any(r["name"] == "Test Hollow Golf Course" for r in rows)
    ready = json.load(open(tmp_path / "OUT_READY"))
    assert ready["coverage"]["IA"]["complete"] and ready["coverage"]["IA"]["source"] == "geofabrik"
    assert "IA" not in ready["partial_states"] and "MO" in ready["missing_states"]


def test_geofabrik_names_and_shards():
    assert ni.geofabrik_url("DC").endswith("/us/district-of-columbia-latest.osm.pbf")
    assert ni.geofabrik_url("NY").endswith("/us/new-york-latest.osm.pbf")
    shards = [ni.shard_states(ni.STATES, i, 6) for i in range(6)]
    assert sorted(s for sh in shards for s in sh) == sorted(ni.STATES)
    load = [sum(ni.GEOFABRIK_MB.get(s, 100) for s in sh) for sh in shards]
    assert max(load) < 1.6 * min(load)                         # balanced by download size, not state count
    assert "CA" in shards[0]                                   # biggest first


def test_fetch_goes_straight_to_quarters_when_some_are_on_disk(tmp_path, monkeypatch):
    monkeypatch.setitem(ni.STATE_BBOX, "IA", (40.2, -91.8, 40.8, -91.2))     # one 1-degree cell
    d = tmp_path / "cells"
    d.mkdir()
    q0 = ni.split4((40.0, -92.0, 41.0, -91.0))[0]
    (d / ni.cell_name(q0)).write_text(json.dumps({"cell": list(q0), "elements": []}))
    calls = []

    def post(url, q, timeout):
        calls.append(q)
        return {"elements": []}
    left = ni.fetch(["IA"], str(tmp_path), budget_min=5, mirrors=FakeMirrors(post), sleep=lambda s: None)
    assert left == [] and len(calls) == 3                      # the three missing quarters, not the parent again
    assert not any("(40.0000,-92.0000,41.0000,-91.0000)" in q for q in calls)
    assert (d / ni.cell_name((40.0, -92.0, 41.0, -91.0))).exists()
