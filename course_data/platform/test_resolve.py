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
