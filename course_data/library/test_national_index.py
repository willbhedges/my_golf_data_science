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


def test_build_state_counts_and_tier():
    rows = ni.build_state("IA", ni.slim_elements(course_json()))
    by = {r["name"]: r for r in rows}
    t = by["Test Hollow Golf Course"]
    assert (t["osm_holes"], t["greens"], t["tees"], t["fairways"], t["pins"], t["outline"]) == (18, 18, 18, 18, 18, 1)
    assert t["holes"] == 18 and t["city"] == "Testville"
    assert ni.tier(t) == "B"
    assert ni.tier(dict(t, card="oga")) == "A"
    n = by["Node Only Golf Club"]
    assert n["outline"] == 0 and ni.tier(n) == "D"
    assert ni.tier(dict(t, osm_holes=12)) == "C"


def test_hole_refs():
    assert ni.hole_ref("Hole 07") == "7"
    assert ni.hole_ref("Red 3") == "red3"
    assert ni.hole_ref("x-y") is None


def test_tiles_cover_bbox():
    for st in ("MO", "AK", "DC", "TX"):
        ts = ni.tiles(st)
        s, w, n, e = ni.STATE_BBOX[st]
        area = sum((t[2] - t[0]) * (t[3] - t[1]) for t in ts)
        assert abs(area - (n - s) * (e - w)) < 1e-6
        assert len(ts) <= 90


class FakeMirrors(ni.Mirrors):
    def __init__(self, answer):
        super().__init__(0, post=answer)


def test_fetch_is_incremental_and_splits(tmp_path, monkeypatch):
    monkeypatch.setattr(ni.time, "sleep", lambda s: None)
    monkeypatch.setitem(ni.STATE_BBOX, "IA", (40.0, -91.5, 41.0, -90.5))     # one 1-degree tile
    monkeypatch.setattr(ni, "tile_deg", lambda st: 1.0)
    calls = []

    def post(url, q, timeout):
        calls.append(q)
        big = "(40.0000,-91.5000,41.0000,-90.5000)" in q
        if big:
            raise TimeoutError("too slow")               # the whole tile fails on every mirror -> split in four
        if "(40.0000,-91.5000,40.5000,-91.0000)" in q:
            return course_json()
        return {"elements": [{"type": "area", "id": 1}]}
    res = ni.fetch(["IA"], str(tmp_path), budget_min=5, mirrors=FakeMirrors(post))
    assert res == {"IA": []}
    d = tmp_path / "IA"
    assert len(list(d.glob("t_*.json"))) == 5                  # four quarters + the parent's split marker
    st = json.load(open(d / "_status.json"))
    assert st["complete"]
    n_calls = len(calls)
    ni.fetch(["IA"], str(tmp_path), budget_min=5, mirrors=FakeMirrors(post))
    assert len(calls) == n_calls                               # nothing fetched twice
    els, status = ni.load_state_tiles(str(d))
    assert status["complete"]
    assert any(e["g"].get("name") == "Test Hollow Golf Course" for e in els)


def test_mirror_without_area_is_not_an_answer(tmp_path, monkeypatch):
    monkeypatch.setattr(ni.time, "sleep", lambda s: None)
    seen = []

    def post(url, q, timeout):
        seen.append(url)
        if url == ni.OVERPASS[0]:
            return {"elements": []}                           # no area element: this mirror has no areas
        return course_json()
    js, url = FakeMirrors(post).ask("q", 10)
    assert url == ni.OVERPASS[1] and len(seen) == 2


def test_failed_tile_leaves_state_partial_and_merge_says_so(tmp_path, monkeypatch):
    monkeypatch.setattr(ni.time, "sleep", lambda s: None)
    monkeypatch.setitem(ni.STATE_BBOX, "IA", (40.0, -91.5, 40.4, -90.7))
    monkeypatch.setattr(ni, "tile_deg", lambda st: 0.4)

    def post(url, q, timeout):
        if "-91.5000" in q:
            return course_json()
        raise TimeoutError("down")
    res = ni.fetch(["IA"], str(tmp_path / "raw"), budget_min=5, mirrors=FakeMirrors(post))
    assert res["IA"]                                            # the east tile (and its quarters) failed
    for f in ("OUT_GZ", "OUT_READY", "LIB_INDEX"):
        monkeypatch.setattr(ni, f, str(tmp_path / f))
    rows = ni.merge(str(tmp_path / "raw"), [])
    assert any(r["name"] == "Test Hollow Golf Course" for r in rows)
    ready = json.load(open(tmp_path / "OUT_READY"))
    assert "IA" in ready["partial_states"] and "MO" in ready["missing_states"]
    doc = json.load(gzip.open(tmp_path / "OUT_GZ", "rt"))
    assert doc["schema"] == "us_courses/2" and "fairways" in doc["fields"]


def test_oga_card_and_readme_block(tmp_path, monkeypatch):
    rows = ni.build_state("IA", ni.slim_elements(course_json()))
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
