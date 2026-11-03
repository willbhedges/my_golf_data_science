"""Offline tests: course resolution and disambiguation, with Overpass / Nominatim faked."""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import platform_common as pc  # noqa: E402
import resolve as rs  # noqa: E402


def el(typ, oid, name, lat, lon, **tags):
    d = 0.006
    return dict(type=typ, id=oid, tags=dict(leisure="golf_course", name=name, **tags),
                center=dict(lat=lat, lon=lon),
                bounds=dict(minlat=lat - d, minlon=lon - d, maxlat=lat + d, maxlon=lon + d))


def test_names():
    assert pc.core_name("The Spirit Hollow Golf Course") == "spirit hollow"
    assert pc.core_name("Mozingo Lake Golf Course") == "mozingo lake"
    assert pc.slugify("Mozingo Lake Golf Course") == "mozingo_lake"
    assert pc.name_regex("Mozingo Lake") == "mozingo[ '-]*lake"
    assert pc.state_code("Iowa") == "IA" and pc.state_code("us-mo") == "MO" and pc.state_code("ia") == "IA"
    with pytest.raises(ValueError):
        pc.state_code("Narnia")


def test_similarity():
    assert rs.name_similarity("Spirit Hollow", "Spirit Hollow Golf Course") == 1.0
    assert rs.name_similarity("Mozingo Lake", "Mozingo Lake Recreation Park Golf") > 0.6
    assert rs.name_similarity("Spirit Hollow", "Sunset Hills") < 0.5


def test_unique_match():
    cands = [rs.candidate(el("relation", 13353211, "Spirit Hollow Golf Course", 40.76, -91.144), holes=18,
                          town="Burlington")]
    status, best, _ = rs.choose(cands, "Spirit Hollow")
    assert status == "ok" and best["osm"]["id"] == 13353211


def test_ambiguous_then_town_disambiguates():
    cands = [rs.candidate(el("way", 1, "Country Club of Lincoln", 40.8, -96.7), holes=18, town="Lincoln"),
             rs.candidate(el("way", 2, "Country Club of Lincoln", 41.6, -93.6), holes=18, town="Des Moines")]
    status, best, ranked = rs.choose([dict(c) for c in cands], "Country Club of Lincoln")
    assert status == "ambiguous" and best is None and len(ranked) == 2
    status, best, _ = rs.choose([dict(c) for c in cands], "Country Club of Lincoln", town="Des Moines")
    assert status == "ok" and best["osm"]["id"] == 2
    status, best, _ = rs.choose([dict(c) for c in cands], "Country Club of Lincoln", osm="way/1")
    assert status == "ok" and best["osm"]["id"] == 1


def test_area_beats_node_and_same_place_is_not_ambiguous():
    a = rs.candidate(el("way", 10, "Mozingo Lake Golf Course", 40.3576, -94.7663), holes=18)
    n = rs.candidate(dict(type="node", id=11, tags=dict(leisure="golf_course", name="Mozingo Lake Golf Course"),
                          lat=40.3580, lon=-94.7660))
    status, best, _ = rs.choose([n, a], "Mozingo Lake")
    assert status == "ok" and best["osm"]["type"] == "way"


def test_not_found():
    c = [rs.candidate(el("way", 3, "Sunset Hills", 41.0, -93.0))]
    assert rs.choose(c, "Spirit Hollow")[0] == "not_found"
    assert rs.choose([], "Spirit Hollow")[0] == "not_found"


def test_resolve_end_to_end_with_fakes(monkeypatch):
    ring = [[-91.152, 40.753], [-91.136, 40.753], [-91.136, 40.768], [-91.152, 40.768], [-91.152, 40.753]]
    calls = []

    def fake_overpass(q, **kw):
        calls.append(q)
        if "out count" in q:
            return dict(elements=[dict(type="count", tags=dict(ways="18"))])
        if "out body geom" in q:
            return dict(elements=[dict(type="way", id=99, tags=dict(leisure="golf_course", name="Spirit Hollow Golf Course"),
                                       geometry=[dict(lon=x, lat=y) for x, y in ring])])
        if 'ISO3166-2"="US-IA"' in q and "spirit" in q.lower():
            return dict(elements=[el("way", 99, "Spirit Hollow Golf Course", 40.7605, -91.144)])
        return dict(elements=[])
    monkeypatch.setattr(pc, "overpass", fake_overpass)
    monkeypatch.setattr(pc, "nominatim", lambda path, **p: dict(address=dict(city="Burlington")))
    res = rs.resolve("Spirit Hollow", "Iowa")
    assert res["status"] == "ok" and res["osm"] == dict(type="way", id=99)
    assert res["town"] == "Burlington" and res["holes_mapped"] == 18 and res["state"] == "IA"
    assert res["boundary"]["type"] == "Polygon"
    assert res["bbox"] == [-91.152, 40.753, -91.136, 40.768]
    assert res["slug"] == "spirit_hollow"


def test_resolve_falls_back_to_words_then_nominatim(monkeypatch):
    seen = []

    def fake_overpass(q, **kw):
        seen.append(q)
        if "around:" in q:
            return dict(elements=[el("way", 7, "Mozingo Lake Golf Course", 40.3576, -94.7663)])
        if "out count" in q:
            return dict(elements=[dict(type="count", tags=dict(ways="18"))])
        if "out body geom" in q:
            return dict(elements=[])
        return dict(elements=[])

    def fake_nom(path, **p):
        if path == "search":
            return [dict(category="place", type="town", lat="40.346", lon="-94.872")]
        return dict(address=dict(city="Maryville"))
    monkeypatch.setattr(pc, "overpass", fake_overpass)
    monkeypatch.setattr(pc, "nominatim", fake_nom)
    res = rs.resolve("Mozingo Lake Recreation Park", "MO")
    assert res["status"] == "ok" and res["osm"]["id"] == 7
    assert any("mozingo" in q for q in seen) and any("recreation" in q for q in seen)
    assert res["boundary"] is None and res["bbox"][0] < -94.7663 < res["bbox"][2]


def test_unnamed_course_at_near_is_found(monkeypatch):
    """No named OSM golf_course (Pine Dunes TX): the request's near point finds the unnamed polygon."""
    def fake_overpass(q):
        if "around:" in q:
            return {"elements": [{"type": "way", "id": 7, "tags": {"leisure": "golf_course"},
                                  "center": {"lat": 31.98, "lon": -95.54},
                                  "bounds": {"minlat": 31.97, "minlon": -95.55, "maxlat": 31.99, "maxlon": -95.53}}]}
        return {"elements": []}
    monkeypatch.setattr(rs.pc, "overpass", fake_overpass)
    monkeypatch.setattr(rs.pc, "nominatim", lambda *a, **k: [])
    els = rs.search("Pine Dunes Resort", "TX", near="31.9778,-95.5389")
    assert [e["id"] for e in els] == [7]
    c = rs.candidate(els[0])
    status, best, _ = rs.choose([c], "Pine Dunes Resort", near="31.9778,-95.5389")
    assert status == "ok" and best["osm"]["id"] == 7
    status, _, _ = rs.choose([rs.candidate(els[0])], "Pine Dunes Resort")
    assert status == "not_found"


def test_named_match_beats_unnamed_near():
    near = "38.1230,-92.7180"
    un = dict(name=None, town="Osage Beach", holes=0, osm=dict(type="way", id=1), center=[-92.688, 38.1248])
    oaks = dict(name="The Oaks", town="Camden County", holes=0, osm=dict(type="relation", id=2), center=[-92.696, 38.1335])
    status, best, _ = rs.choose([un, oaks], "The Oaks at Margaritaville Lake Resort", "Osage Beach", near=near)
    assert status == "ok" and best["osm"]["id"] == 2
    syc = dict(name="Sycamore Creek Golf Club", town="Osage Beach", holes=0, osm=dict(type="way", id=3),
               center=[-92.6775, 38.1312])
    status, best, _ = rs.choose([syc, oaks], "The Oaks at Margaritaville Lake Resort", "Osage Beach", near=near)
    assert best is not None and best["osm"]["id"] == 2


def test_from_near_box_and_outline():
    c = rs.from_near("Pine Dunes Resort & Golf Club", "TX", "31.9778,-95.5389", 1000)
    assert c["status"] == "ok" and c["osm"] == {"type": "none", "id": 0} and c["boundary"] is None
    assert abs((c["bbox"][3] - c["bbox"][1]) * 111320 - 2000) < 5
    ring = [[-95.54, 31.97], [-95.53, 31.97], [-95.53, 31.98]]
    c = rs.from_near("X", "TX", "31.975,-95.535", boundary_ll=ring)
    assert c["boundary"]["type"] == "Polygon" and c["bbox"] == [-95.54, 31.97, -95.53, 31.98]


def test_closed_course(monkeypatch):
    """Deer Creek GC (Overland Park KS) closed in 2022; OSM keeps it as relation 4253531 'Former Deer Creek Golf Club'
    with no holes: resolve says "closed" instead of letting the build fail with "no holes built" after 3 retries."""
    former = rs.candidate(el("relation", 4253531, "Former Deer Creek Golf Club", 38.884, -94.672), holes=0,
                          town="Overland Park")
    assert "Former Deer Creek" in rs.closed_reason(former)
    assert rs.closed_reason(former, "Former Deer Creek") is None          # the golfer typed the marker
    tagged = rs.candidate(el("way", 1, "Sunset Links", 39.0, -94.6, end_date="2019-10"))
    assert "end_date=2019-10" in rs.closed_reason(tagged)
    for name in ("Old Kinderhook Golf Club", "Old Warson Country Club", "Formerly Known Links"):
        assert rs.closed_reason(rs.candidate(el("way", 2, name, 38.0, -92.7))) is None
    assert rs.closed_reason(rs.candidate(el("way", 3, "Elm Ridge", 38.0, -92.7, disused="no"))) is None
    monkeypatch.setattr(rs, "search", lambda *a, **k: [el("relation", 4253531, "Former Deer Creek Golf Club",
                                                           38.884, -94.672)])
    monkeypatch.setattr(rs, "hole_counts", lambda els: {})
    monkeypatch.setattr(rs, "boundary", lambda *a: pytest.fail("a closed course must not fetch its boundary"))
    res = rs.resolve("Deer Creek Golf Club", "KS", town="Overland Park", with_towns=False)
    assert res["status"] == "closed" and "4253531" in res["closed"] and "bbox" not in res


def test_partial_name_in_another_town_is_not_a_candidate():
    """Longview Lake GC (Lee's Summit MO) rev 1: the word fallback "lake" matched three other MO courses and resolve
    said "ambiguous" between them; a partial match in another town is another course -> not_found."""
    cands = [rs.candidate(el("way", 385067034, "Mozingo Lake Golf Course", 40.35, -94.82), holes=18, town="Maryville"),
             rs.candidate(el("way", 393080132, "Lake Valley Golf Club", 38.0, -92.7), holes=18, town="Camdenton"),
             rs.candidate(el("way", 389825787, "Meadow Lake Acres Country Club", 38.7, -92.0), holes=18,
                          town="New Bloomfield")]
    status, best, _ = rs.choose([dict(c) for c in cands], "Longview Lake Golf Course", town="Lee's Summit")
    assert status == "not_found" and best is None
    # the full name in another town (OSM's addr:city is the post town) still resolves
    arb = rs.candidate(el("way", 9, "Fred Arbanas Golf Course", 38.91, -94.47), holes=18, town="Kansas City")
    status, best, _ = rs.choose([arb], "Fred Arbanas Golf Course", town="Lee's Summit")
    assert status == "ok" and best["osm"]["id"] == 9


def test_address_geocodes_to_near(monkeypatch):
    """Kokopelli GC (Marion IL) is not in OSM by name: a request "address" becomes resolve's `near` point."""
    import fetch_package as fp
    monkeypatch.setattr(pc, "nominatim", lambda path, **k: [dict(lat="37.7531", lon="-88.9702", display_name="x")])
    assert fp.geocode_address("1401 Champions Dr, Marion, IL 62959") == "37.753100,-88.970200"
    monkeypatch.setattr(pc, "nominatim", lambda path, **k: None)
    assert fp.geocode_address("nowhere") is None


def test_exact_name_beats_resort_sub_courses():
    """us60: Arcadia Bluffs / Forest Dunes came back "ambiguous" between the course and its resort siblings."""
    cands = [rs.candidate(el("way", 293247442, "Arcadia Bluffs Golf Club", 44.50, -86.23), holes=18, town="Arcadia"),
             rs.candidate(el("way", 693998226, "Arcadia Bluffs - South Course", 44.47, -86.21), holes=18,
                          town="Arcadia")]
    status, best, _ = rs.choose(cands, "Arcadia Bluffs Golf Club", town="Arcadia")
    assert status == "ok" and best["osm"]["id"] == 293247442
    cands = [rs.candidate(el("way", 1536953640, "Forest Dunes Course", 44.50, -84.53), holes=18),
             rs.candidate(el("way", 1536953639, "Forest Dunes - The Loop Course", 44.51, -84.50), holes=18),
             rs.candidate(el("way", 623889475, "Forest Dunes Golf Resort", 44.52, -84.52), holes=46)]
    status, best, _ = rs.choose(cands, "Forest Dunes Golf Club")
    assert status == "ok" and best["osm"]["id"] == 1536953640
    # a golfer who names the sub-course gets it; two different exact-name places stay ambiguous
    status, best, _ = rs.choose([dict(c) for c in cands], "Forest Dunes The Loop")
    assert status == "ok" and best["osm"]["id"] == 1536953639
    two = [rs.candidate(el("way", 1, "Country Club of Lincoln", 40.8, -96.7), holes=18),
           rs.candidate(el("way", 2, "Country Club of Lincoln", 41.6, -93.6), holes=18)]
    assert rs.choose(two, "Country Club of Lincoln")[0] == "ambiguous"


def test_words_in_any_order_then_node_takes_enclosing_site(monkeypatch):
    """"Kapalua Plantation" is OSM "The Plantation Course at Kapalua"; a course mapped as a node inside a
    multi-course site's polygon (Bethpage Black) gets the site's boundary."""
    ring = [[-73.47, 40.73], [-73.43, 40.73], [-73.43, 40.76], [-73.47, 40.76], [-73.47, 40.73]]
    seen = []

    def fake_overpass(q, **kw):
        seen.append(q)
        if "is_in(" in q:
            return dict(elements=[el("relation", 555, "Bethpage State Park", 40.745, -73.45)])
        if "out count" in q:
            return dict(elements=[dict(type="count", tags=dict(ways="90"))])
        if "out body geom" in q and "relation(555)" in q:
            return dict(elements=[dict(type="way", id=555, tags=dict(leisure="golf_course"),
                                       geometry=[dict(lon=x, lat=y) for x, y in ring])])
        if '["name"~"bethpage",i]["name"~"black",i]' in q:
            return dict(elements=[dict(type="node", id=2854158382, lat=40.744, lon=-73.454,
                                       tags=dict(leisure="golf_course", name="Black Course at Bethpage"))])
        return dict(elements=[])
    monkeypatch.setattr(pc, "overpass", fake_overpass)
    monkeypatch.setattr(pc, "nominatim", lambda path, **p: dict(address=dict(city="Farmingdale")))
    res = rs.resolve("Bethpage Black Course", "NY")
    assert res["status"] == "ok" and res["osm"] == dict(type="node", id=2854158382)
    assert res["site"]["id"] == 555 and res["boundary"]["type"] == "Polygon"
    assert res["bbox"] == [-73.47, 40.73, -73.43, 40.76]


def test_overpass_partial_remark_is_a_failure(monkeypatch):
    """A 200 answer with a runtime remark (0 elements) made resolve say "not_found": the next mirror is asked."""
    import types
    answers = [dict(elements=[], remark="runtime error: Query timed out in \"query\" at line 3 after 120 seconds."),
               dict(elements=[dict(type="way", id=1)])]
    calls = []

    def post(url, **kw):
        calls.append(url)
        js = answers[min(len(calls) - 1, 1)]
        return types.SimpleNamespace(status_code=200, json=lambda: js, text="")
    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace(post=post))
    assert pc.overpass("q", tries=1)["elements"] == [dict(type="way", id=1)]
    assert len(calls) == 2
    assert pc.overpass_remark_problem(dict(remark="note: nothing")) is None


def test_unnamed_course_picked_by_near_keeps_the_request_name(monkeypatch):
    """Queenstown Harbor (MD): OSM maps the 36-hole outline unnamed, so `near` picks it and course.json had
    name=None; fetch_imagery's `--name None` then crashed the package (" ".join on a None)."""
    def fake_overpass(q, **kw):
        if "around:" in q:
            return {"elements": [{"type": "way", "id": 7, "tags": {"leisure": "golf_course"},
                                  "center": {"lat": 38.985, "lon": -76.17},
                                  "bounds": {"minlat": 38.98, "minlon": -76.18, "maxlat": 38.99, "maxlon": -76.16}}]}
        if "out count" in q:
            return {"elements": [{"type": "count", "tags": {"ways": "36"}}]}
        if "out body geom" in q:
            return {"elements": []}
        return {"elements": []}
    monkeypatch.setattr(rs.pc, "overpass", fake_overpass)
    monkeypatch.setattr(rs.pc, "nominatim", lambda *a, **k: [])
    res = rs.resolve("Queenstown Harbor River Course", "MD", near="38.9850,-76.1700", with_towns=False)
    assert res["status"] == "ok" and res["osm"]["id"] == 7
    assert res["name"] == "Queenstown Harbor River Course" and res["osm_name"] is None
    assert res["slug"] == pc.slugify("Queenstown Harbor River Course")


def test_far_low_score_match_is_dropped_when_its_town_is_unknown(monkeypatch):
    """Queenstown Harbor River Course (MD), run 41655811379: the one-word fallback "river" found South River Golf
    Course 36 km away; Nominatim's reverse lookup 503'd so its town was None, the other-town filter let it through
    and it won with score 0.42 (9 holes, blocked at the publish gate). A far, low-score match is never the course:
    resolve falls back to the courses around `near` (the unnamed 36-hole outline)."""
    def fake_overpass(q, **kw):
        if "around:" in q:
            return {"elements": [{"type": "way", "id": 1067525665, "tags": {"leisure": "golf_course"},
                                  "center": {"lat": 38.98635, "lon": -76.17264},
                                  "bounds": {"minlat": 38.97, "minlon": -76.19, "maxlat": 39.0, "maxlon": -76.15}}]}
        if "out count" in q:
            return {"elements": [{"type": "count", "tags": {"ways": "0" if "61239088" in q else "36"}}]}
        if "out body geom" in q:
            return {"elements": []}
        if 'river"' in q.lower():
            return {"elements": [el("way", 61239088, "South River Golf Course", 38.92139, -76.57978)]}
        return {"elements": []}
    monkeypatch.setattr(rs.pc, "overpass", fake_overpass)
    monkeypatch.setattr(rs.pc, "nominatim", lambda *a, **k: None)       # search and reverse both down (503)
    res = rs.resolve("Queenstown Harbor River Course", "MD", town="Queenstown", near="38.9850,-76.1700")
    assert res["status"] == "ok" and res["osm"] == {"type": "way", "id": 1067525665}
    assert res["name"] == "Queenstown Harbor River Course" and res["holes_mapped"] == 36
    assert all(c["osm"]["id"] != 61239088 for c in res["candidates"])


def test_choose_never_returns_a_far_low_score_match():
    near = "38.9850,-76.1700"
    far = rs.candidate(el("way", 61239088, "South River Golf Course", 38.92139, -76.57978), holes=0, town=None)
    status, best, _ = rs.choose([dict(far)], "Queenstown Harbor River Course", town="Queenstown", near=near)
    assert status == "not_found" and best is None
    # no town in the request either: still dropped
    status, best, _ = rs.choose([dict(far)], "Queenstown Harbor River Course", near=near)
    assert status == "not_found"
    # the full name far from `near` (a wrong pin) still resolves: its score is high
    full = rs.candidate(el("way", 5, "Queenstown Harbor River Course", 38.6, -76.6), holes=18, town=None)
    status, best, _ = rs.choose([dict(full)], "Queenstown Harbor River Course", near=near)
    assert status == "ok" and best["osm"]["id"] == 5
    # a pinned osm id is the golfer's word
    status, best, _ = rs.choose([dict(far)], "Queenstown Harbor River Course", near=near, osm="way/61239088")
    assert status == "ok"


def test_fetch_imagery_command_never_holds_none(monkeypatch, tmp_path):
    import fetch_package as fp
    seen = []
    monkeypatch.setattr(fp.subprocess, "run", lambda cmd, **k: seen.append(cmd) or type("R", (), {"returncode": 0}))
    course = dict(name=None, slug="queenstown_harbor", bbox=[-76.18, 38.98, -76.16, 38.99])
    assert fp.fetch_imagery(course, str(tmp_path), year=None)
    cmd = seen[0]
    assert all(isinstance(x, str) for x in cmd)
    assert cmd[cmd.index("--name") + 1] == "queenstown_harbor" and cmd[cmd.index("--year") + 1] == "auto"
