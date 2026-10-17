"""S0 resolve: a US course name + state -> the OSM leisure=golf_course, its boundary and bbox.

  python course_data/platform/resolve.py "Spirit Hollow" IA [--town Burlington] [--osm relation/13353211]

Network (Overpass + Nominatim) is only reachable from GitHub Actions; the ranking / disambiguation
logic (`rank`, `choose`) is pure and unit-tested offline.

Search order
  1. --osm given: that element.
  2. Overpass: nwr[leisure=golf_course][name~<core name>, case-insensitive] inside the state's
     ISO3166-2 area (US-IA). The core name drops generic words (golf, course, club, country, ...), so
     "Mozingo Lake" finds "Mozingo Lake Golf Course".
  3. Nothing: retry with each distinctive word of the name (longest first).
  4. Nothing: Nominatim "<name>, <state>, USA"; golf_course hits are taken directly, other hits
     (a town, a park) are searched for the nearest leisure=golf_course within 4 km.
  5. Nothing and the request gives "near" (lat,lon): every leisure=golf_course within 4 km of it; an unnamed
     one within 3 km scores as a match.
Every candidate gets its town (addr:city, else a Nominatim reverse lookup) and the number of
golf=hole ways inside it (Overpass map_to_area + out count).

Disambiguation (`choose`): candidates are scored on name similarity, town match, area vs node, and
mapped holes. One clear winner -> status "ok"; several near-equal ones -> status "ambiguous" with the
candidate list (name, town, holes, OSM id) so the golfer can pick (`town` or `osm` in the request).
"""
import argparse
import difflib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import platform_common as pc  # noqa: E402

AMBIGUOUS_MARGIN = 0.12        # second-best score this close to the best -> ask the golfer


# ----------------------------------------------------------------------------- pure logic
def name_similarity(want, got):
    """0..1 similarity of the core names (generic golf words removed): mostly whole-word overlap
    (a word matches with >= 0.85 character similarity, so typos still count), plus a little of the
    character-level ratio."""
    a, b = pc.core_name(want), pc.core_name(got or "")
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ta, tb = a.split(), b.split()

    def hits(xs, ys):
        return sum(1 for x in xs if max(difflib.SequenceMatcher(None, x, y).ratio() for y in ys) >= 0.85)
    recall, precision = hits(ta, tb) / len(ta), hits(tb, ta) / len(tb)
    seq = difflib.SequenceMatcher(None, a, b).ratio()
    return round(0.75 * (0.7 * recall + 0.3 * precision) + 0.25 * seq, 4)


def candidate(el, holes=None, town=None):
    """Overpass element (out tags center bb) -> candidate dict."""
    t = el.get("tags", {})
    b = el.get("bounds")
    c = el.get("center") or ({"lat": el["lat"], "lon": el["lon"]} if "lat" in el else None)
    if c is None and b:                                  # `out tags center bb` may omit center on relations
        c = {"lat": (b["minlat"] + b["maxlat"]) / 2, "lon": (b["minlon"] + b["maxlon"]) / 2}
    town = town or t.get("addr:city") or t.get("is_in:city") or t.get("addr:town") or t.get("addr:village")
    return dict(name=t.get("name"), osm=dict(type=el["type"], id=el["id"]), town=town,
                holes=holes, center=[c["lon"], c["lat"]] if c else None,
                bbox=[b["minlon"], b["minlat"], b["maxlon"], b["maxlat"]] if b else None,
                website=t.get("website") or t.get("contact:website") or t.get("url"),
                tags={k: v for k, v in t.items() if k.startswith(("addr:", "name", "operator", "access",
                                                                    "golf:", "holes", "par"))})


def _near(near):
    if not near:
        return None
    if isinstance(near, str):
        lat, lon = (float(v) for v in near.split(","))
        return lat, lon
    return float(near[0]), float(near[1])


def score(c, want, town=None, osm=None, near=None):
    s = name_similarity(want, c["name"])
    nr = _near(near)
    if nr and c.get("center"):
        d = pc.haversine_m(nr[0], nr[1], c["center"][1], c["center"][0]) / 1000
        s += 0.3 if d < 15 else (-0.3 if d > 60 else 0.0)
    if osm and f"{c['osm']['type']}/{c['osm']['id']}" == osm:
        s += 10
    if town and c.get("town") and pc.core_name(town) == pc.core_name(c["town"]):
        s += 0.5
    elif town and c.get("town"):
        s -= 0.2
    if nr and c.get("center") and not c.get("name"):
        # an UNNAMED golf course at the request's coordinates is the course (OSM often maps the polygon with no
        # name): name similarity is 0, so without this it never passes the 0.35 bar
        d = pc.haversine_m(nr[0], nr[1], c["center"][1], c["center"][0]) / 1000
        s += 0.4 if d < 3 else 0.0
    if c["osm"]["type"] == "node":
        s -= 0.15                                   # no boundary: worse than an area with the same name
    h = c.get("holes")
    if h:
        s += 0.1 if h >= 9 else 0.03
    return round(s, 4)


def rank(cands, want, town=None, osm=None, near=None):
    for c in cands:
        c["score"] = score(c, want, town, osm, near)
    return sorted(cands, key=lambda c: -c["score"])


def choose(cands, want, town=None, osm=None, near=None):
    """-> (status, best | None, ranked). status: ok | ambiguous | not_found."""
    ranked = rank(cands, want, town, osm, near)
    ranked = [c for c in ranked if c["score"] > 0.35]
    if not ranked:
        return "not_found", None, ranked
    best = ranked[0]
    if len(ranked) > 1 and not osm:
        second = ranked[1]
        # two different places with near-equal claims (e.g. "Country Club" in two towns)
        same_place = (best.get("center") and second.get("center") and
                      pc.haversine_m(best["center"][1], best["center"][0],
                                     second["center"][1], second["center"][0]) < 400)
        if best["score"] - second["score"] < AMBIGUOUS_MARGIN and not same_place:
            return "ambiguous", None, ranked
    return "ok", best, ranked


# ----------------------------------------------------------------------------- network
def _search_overpass(rx, iso):
    q = f"""[out:json][timeout:120];
    area["ISO3166-2"="{iso}"]["admin_level"="4"]->.st;
    nwr["leisure"="golf_course"]["name"~"{rx}",i](area.st);
    out tags center bb;"""
    return pc.overpass(q).get("elements", [])


def _around(lat, lon, radius=4000):
    q = f"""[out:json][timeout:90];
    nwr["leisure"="golf_course"](around:{radius},{lat},{lon});
    out tags center bb;"""
    return pc.overpass(q).get("elements", [])


def hole_counts(els):
    """{(type, id): number of golf=hole ways inside each area} (one Overpass call)."""
    parts, keys = [], []
    for i, e in enumerate(els):
        if e["type"] == "node":
            continue
        parts.append(f'{e["type"][:3] if e["type"] == "relation" else "way"}({e["id"]});map_to_area->.a{i};'
                     f'way["golf"="hole"](area.a{i});out count;')
        keys.append((e["type"], e["id"]))
    if not parts:
        return {}
    res = pc.overpass("[out:json][timeout:120];\n" + "\n".join(parts)).get("elements", [])
    out = {}
    for k, r in zip(keys, [r for r in res if r.get("type") == "count"]):
        out[k] = int(r.get("tags", {}).get("ways", 0))
    return out


def reverse_town(lat, lon):
    js = pc.nominatim("reverse", lat=lat, lon=lon, zoom=12, addressdetails=1)
    a = (js or {}).get("address", {})
    town = a.get("city") or a.get("town") or a.get("village") or a.get("hamlet")
    if not town:                                         # rural course: nearest named place instead of the county
        js2 = pc.nominatim("reverse", lat=lat, lon=lon, zoom=10, addressdetails=1)
        a2 = (js2 or {}).get("address", {})
        town = a2.get("city") or a2.get("town") or a2.get("village") or a.get("county")
    return town


def search(name, state, osm=None, near=None):
    """Raw Overpass elements for the name in the state (see the module docstring for the order); with `near`
    (lat,lon of the course, e.g. from its street address) every leisure=golf_course within 4 km of it is a
    candidate too, named or not (step 5: the course is in OSM under another name, or unnamed)."""
    iso = "US-" + pc.state_code(state)
    if osm:
        typ, oid = osm.split("/")
        return pc.overpass(f"[out:json][timeout:60];{typ}({oid});out tags center bb;").get("elements", [])
    els = _search_overpass(pc.name_regex(name), iso)
    if els:
        return els
    for w in sorted(pc.core_name(name).split(), key=len, reverse=True):
        if len(w) >= 4:
            els = _search_overpass(pc.name_regex(w), iso)
            if els:
                return els
    st = pc.STATES[pc.state_code(state)]
    hits = pc.nominatim("search", q=f"{name}, {st}, USA", countrycodes="us", limit=10) or []
    out = []
    for h in hits:
        if h.get("category") == "leisure" and h.get("type") == "golf_course":
            typ = h["osm_type"]
            out += pc.overpass(f"[out:json][timeout:60];{typ}({h['osm_id']});out tags center bb;").get("elements", [])
    if not out and hits:
        out = _around(float(hits[0]["lat"]), float(hits[0]["lon"]))
    if not out and _near(near):
        out = _around(*_near(near))
    return out


def boundary(el_type, el_id):
    """GeoJSON geometry of the course area (Polygon / MultiPolygon), or None for a node."""
    import fetch_course as fc
    raw = pc.overpass(f"[out:json][timeout:90];{el_type}({el_id});out body geom;")
    els = raw.get("elements", [])
    if not els:
        return None, None
    feats = fc.to_geojson(els)["features"]
    geom = feats[0]["geometry"] if feats else None
    if geom and geom["type"] == "LineString":            # an unclosed way: treat as a ring
        c = geom["coordinates"]
        geom = {"type": "Polygon", "coordinates": [c + [c[0]]]}
    return geom, fc.bounds_of(els[0])


def resolve(name, state, town=None, osm=None, with_towns=True, near=None):
    """-> course dict (ARCHITECTURE 3.1 course.json + state, town, holes, boundary, candidates).
    status: ok | ambiguous | not_found. Only 'ok' carries boundary/bbox."""
    sc = pc.state_code(state)
    els = search(name, sc, osm, near)
    els = [e for e in els if e.get("tags", {}).get("leisure") == "golf_course" or osm]
    counts = hole_counts(els[:12]) if els else {}
    cands = []
    for e in els[:12]:
        c = candidate(e, counts.get((e["type"], e["id"])))
        if with_towns and not c["town"] and c["center"]:
            c["town"] = reverse_town(c["center"][1], c["center"][0])
        cands.append(c)
    status, best, ranked = choose(cands, name, town, osm, near)
    out = dict(schema="course/1", query=dict(name=name, state=sc, town=town, osm=osm, near=near), status=status,
               candidates=[{k: c.get(k) for k in ("name", "town", "holes", "osm", "center", "score")}
                           for c in ranked])
    if status != "ok":
        return out
    geom, b = boundary(best["osm"]["type"], best["osm"]["id"])
    if b is None and best.get("center"):
        lon, lat = best["center"]
        d = 800 / 111320.0
        b = dict(minlat=lat - d, maxlat=lat + d, minlon=lon - d / math.cos(math.radians(lat)),
                 maxlon=lon + d / math.cos(math.radians(lat)))
    if not best.get("center"):
        best["center"] = [(b["minlon"] + b["maxlon"]) / 2, (b["minlat"] + b["maxlat"]) / 2]
    if with_towns and not best.get("town"):
        best["town"] = reverse_town(best["center"][1], best["center"][0])
    out.update(name=best["name"], slug=pc.slugify(best["name"] or name), osm=best["osm"],
               center=best["center"], bbox=[b["minlon"], b["minlat"], b["maxlon"], b["maxlat"]],
               address=", ".join(x for x in (best.get("town"), sc) if x), town=best.get("town"), state=sc,
               holes_mapped=best.get("holes"), website=best.get("website"), tags=best.get("tags"),
               boundary=geom, boundary_note=None if geom else "course mapped as a point: bbox is 800 m around it")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("state")
    ap.add_argument("--town")
    ap.add_argument("--osm", help="force an element, e.g. relation/13353211")
    ap.add_argument("--near", help="lat,lon hint")
    ap.add_argument("--out")
    a = ap.parse_args()
    res = resolve(a.name, a.state, a.town, a.osm, near=a.near)
    if a.out:
        pc.write_json(a.out, res)
    print(json.dumps({k: v for k, v in res.items() if k != "boundary"}, indent=1))


if __name__ == "__main__":
    main()
