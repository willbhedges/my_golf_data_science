"""Fetch a golf course's geometry from OpenStreetMap (+ optional NAIP imagery).

  python course_data/fetch_course.py --name "Spirit Hollow Golf Course" --near 40.745,-91.15 \
      --out course_data/spirit_hollow

Writes into --out:
  osm.geojson         every golf-relevant OSM feature in the course bbox (+ a pad), with an
                      "inside_course" flag and the raw OSM tags as properties
  osm_raw.json        the raw Overpass response (for re-processing without the network)
  summary.json        counts per golf tag / land cover tag, the hole list (ref, par, handicap,
                      centre-line node count and length), tees, greens, NAIP status
  naip_rgbn.tif       latest NAIP 4-band (R,G,B,NIR) clip of the course bbox, native resolution
  naip_preview.png    an RGB preview (+ .pgw world file, in the GeoTIFF's CRS)

The OSM part needs only `requests` + `numpy`. NAIP needs `pystac-client planetary-computer
rasterio` and is skipped (with the reason recorded in summary.json) if they're missing or the
Planetary Computer is unreachable. Overpass and the Planetary Computer are blocked from the
Claude sandbox, so this runs on GitHub Actions (.github/workflows/course_fetch.yml).
"""
import argparse
import json
import math
import os
import re
import sys
import time
from collections import Counter

import requests

OVERPASS = ["https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"]
UA = {"User-Agent": "my_golf_data_science course-fetch spike (github.com/willbhedges)"}
YD = 0.9144
LINEAR_KEYS = ("highway", "barrier", "waterway", "railway", "power")
LINEAR_GOLF = ("hole", "cartpath", "path")


# ----------------------------------------------------------------------------- Overpass
def overpass(query, tries=3):
    last = None
    for attempt in range(tries):
        for url in OVERPASS:
            try:
                r = requests.post(url, data={"data": query}, headers=UA, timeout=180)
                if r.status_code == 200:
                    return r.json()
                last = f"{url}: HTTP {r.status_code} {r.text[:200]}"
            except Exception as e:                      # noqa: BLE001
                last = f"{url}: {e!r}"
            print("overpass failed:", last, file=sys.stderr)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"all Overpass endpoints failed: {last}")


def geocode(q):
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": q, "format": "json", "limit": 1}, headers=UA, timeout=60)
    r.raise_for_status()
    js = r.json()
    return (float(js[0]["lat"]), float(js[0]["lon"])) if js else None


def name_regex(name):
    core = re.sub(r"\b(golf|course|club|country|gc|cc|links|the)\b", " ", name, flags=re.I)
    core = " ".join(core.split()) or name
    return re.escape(core).replace("\\ ", "[ -]?")


def find_course(name, near, radius_m):
    rx = name_regex(name)
    lat, lon = near
    q = f"""[out:json][timeout:90];
    nwr["leisure"="golf_course"]["name"~"{rx}",i](around:{radius_m},{lat},{lon});
    out tags center geom;"""
    els = overpass(q)["elements"]
    if not els:                                         # unnamed / differently named: nearest course
        q = f"""[out:json][timeout:90];
        nwr["leisure"="golf_course"](around:{radius_m},{lat},{lon});
        out tags center geom;"""
        els = overpass(q)["elements"]
    if not els:
        return None, []

    for e in els:
        if not e.get("center"):
            b = bounds_of(e)
            e["center"] = dict(lat=(b["minlat"] + b["maxlat"]) / 2, lon=(b["minlon"] + b["maxlon"]) / 2)

    def dist(e):
        c = e["center"]
        return math.hypot(c["lat"] - lat, (c["lon"] - lon) * math.cos(math.radians(lat)))
    els.sort(key=lambda e: (e["type"] == "node", dist(e)))   # prefer areas, then closest
    return els[0], els


def bounds_of(el):
    """Bounding box of an Overpass element (relations don't always carry `bounds`)."""
    if el.get("bounds"):
        return el["bounds"]
    pts = [p for p in el.get("geometry", []) if p]
    for m in el.get("members", []):
        pts += [p for p in m.get("geometry", []) if p]
    if not pts and "lat" in el:
        pts = [el]
    return dict(minlat=min(p["lat"] for p in pts), minlon=min(p["lon"] for p in pts),
                maxlat=max(p["lat"] for p in pts), maxlon=max(p["lon"] for p in pts))


def fetch_features(bbox):
    s, w, n, e = bbox
    b = f"{s},{w},{n},{e}"
    q = f"""[out:json][timeout:180];
    (
      nwr["golf"]({b});
      nwr["leisure"~"golf_course|pitch|park"]({b});
      nwr["natural"]({b});
      nwr["landuse"]({b});
      nwr["water"]({b});
      way["waterway"]({b});
      way["highway"]({b});
      way["building"]({b});
      way["barrier"]({b});
      way["railway"]({b});
    );
    out body geom;"""
    return overpass(q)


# ----------------------------------------------------------------------------- GeoJSON
def _ll(geom):
    return [[p["lon"], p["lat"]] for p in geom if p]


def _join_rings(segments):
    """Stitch open way segments of a multipolygon into closed rings."""
    segs = [s[:] for s in segments if len(s) >= 2]
    rings = []
    while segs:
        ring = segs.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]
                elif s[-1] == ring[-1]:
                    ring += s[::-1][1:]
                elif s[-1] == ring[0]:
                    ring = s[:-1] + ring
                elif s[0] == ring[0]:
                    ring = s[::-1][:-1] + ring
                else:
                    continue
                segs.pop(i)
                changed = True
                break
        if len(ring) >= 4 and ring[0] == ring[-1]:
            rings.append(ring)
    return rings


def is_area(tags, coords):
    if len(coords) < 4 or coords[0] != coords[-1]:
        return False
    if tags.get("area") == "yes":
        return True
    if tags.get("golf") in LINEAR_GOLF:
        return False
    if any(k in tags for k in LINEAR_KEYS) and "building" not in tags:
        return tags.get("area") == "yes" or tags.get("highway") == "pedestrian"
    if tags.get("natural") in ("tree_row", "coastline", "cliff"):
        return False
    return True


def to_geojson(elements):
    feats = []
    for el in elements:
        tags = el.get("tags", {})
        props = {"osm_type": el["type"], "osm_id": el["id"], **tags}
        if el["type"] == "node":
            geom = {"type": "Point", "coordinates": [el["lon"], el["lat"]]}
        elif el["type"] == "way":
            c = _ll(el.get("geometry", []))
            if len(c) < 2:
                continue
            geom = ({"type": "Polygon", "coordinates": [c]} if is_area(tags, c)
                    else {"type": "LineString", "coordinates": c})
        elif el["type"] == "relation" and tags.get("type") in ("multipolygon", "boundary"):
            outer = [_ll(m.get("geometry", [])) for m in el.get("members", [])
                     if m["type"] == "way" and m.get("role", "outer") in ("outer", "")]
            inner = [_ll(m.get("geometry", [])) for m in el.get("members", [])
                     if m["type"] == "way" and m.get("role") == "inner"]
            outer, inner = _join_rings(outer), _join_rings(inner)
            if not outer:
                continue
            # attach each inner ring to the outer ring containing its first vertex
            polys = [[o] for o in outer]
            for r in inner:
                for p in polys:
                    if point_in_ring(r[0], p[0]):
                        p.append(r)
                        break
            geom = {"type": "MultiPolygon", "coordinates": polys}
        else:
            continue
        feats.append({"type": "Feature", "properties": props, "geometry": geom})
    return {"type": "FeatureCollection", "features": feats}


def point_in_ring(pt, ring):
    x, y = pt
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-300) + x1:
            inside = not inside
    return inside


def outer_rings(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []


def rep_point(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Point":
        return c
    pts = c if t == "LineString" else outer_rings(geom)[0][:-1]
    return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]


def length_yd(coords):
    tot = 0.0
    for (lo1, la1), (lo2, la2) in zip(coords, coords[1:]):
        k = math.cos(math.radians((la1 + la2) / 2))
        tot += math.hypot((lo2 - lo1) * k, la2 - la1) * 111320.0
    return tot / YD


# ----------------------------------------------------------------------------- summary
def summarise(fc, course_el, all_courses, course_rings):
    def inside(f):
        p = rep_point(f["geometry"])
        return any(point_in_ring(p, r) for r in course_rings) if course_rings else None

    for f in fc["features"]:
        f["properties"]["inside_course"] = inside(f)

    golf = Counter()
    golf_in = Counter()
    cover = Counter()
    for f in fc["features"]:
        p = f["properties"]
        if "golf" in p:
            golf[p["golf"]] += 1
            golf_in[p["golf"]] += bool(p["inside_course"])
        for k in ("natural", "landuse", "waterway", "water"):
            if k in p and p["inside_course"]:
                cover[f"{k}={p[k]}"] += 1

    holes = []
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") != "hole":
            continue
        g = f["geometry"]
        c = g["coordinates"] if g["type"] == "LineString" else outer_rings(g)[0] if g["type"] != "Point" else []
        holes.append(dict(ref=p.get("ref"), par=p.get("par"), handicap=p.get("handicap"),
                          dist=p.get("dist"), name=p.get("name"), geometry=g["type"],
                          nodes=len(c), length_yd=round(length_yd(c)) if g["type"] == "LineString" else None,
                          extra_tags={k: v for k, v in p.items() if re.match(r"(par|handicap|dist):", k)},
                          osm_id=p["osm_id"]))

    def refkey(h):
        try:
            return (0, int(h["ref"]))
        except (TypeError, ValueError):
            return (1, str(h["ref"]))
    holes.sort(key=refkey)
    refs = [h["ref"] for h in holes]
    tees = [dict(osm_id=f["properties"]["osm_id"], geometry=f["geometry"]["type"],
                 **{k: v for k, v in f["properties"].items()
                    if k in ("ref", "tee", "colour", "color", "name", "par", "dist", "description")})
            for f in fc["features"] if f["properties"].get("golf") == "tee"]
    ct = course_el.get("tags", {}) if course_el else {}
    return dict(
        course=dict(osm_type=course_el and course_el["type"], osm_id=course_el and course_el["id"],
                    name=ct.get("name"), tags=ct, center=course_el and course_el.get("center"),
                    bounds=course_el and course_el.get("bounds"),
                    other_candidates=[dict(type=e["type"], id=e["id"], name=e.get("tags", {}).get("name"))
                                      for e in all_courses[1:6]]),
        n_features=len(fc["features"]),
        golf_tag_counts=dict(golf.most_common()),
        golf_tag_counts_inside_course=dict(golf_in.most_common()),
        land_cover_inside_course=dict(cover.most_common()),
        holes=holes,
        hole_refs=refs,
        missing_hole_refs=[str(i) for i in range(1, 19) if str(i) not in [str(r) for r in refs]],
        holes_with_par=sum(1 for h in holes if h["par"]),
        holes_with_handicap=sum(1 for h in holes if h["handicap"]),
        hole_centrelines=sum(1 for h in holes if h["geometry"] == "LineString"),
        tees=dict(count=len(tees),
                  with_colour_or_ref=sum(1 for t in tees if any(k in t for k in ("ref", "tee", "colour", "color"))),
                  items=tees),
        greens=golf.get("green", 0),
        pins=golf.get("pin", 0),
    )


# ----------------------------------------------------------------------------- NAIP
def fetch_naip(bbox_wgs, out_dir, max_mb=38):
    import numpy as np
    import planetary_computer
    import pystac_client
    import rasterio
    from rasterio.merge import merge
    from rasterio.warp import transform_bounds

    s, w, n, e = bbox_wgs
    cat = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                                    modifier=planetary_computer.sign_inplace)
    items = list(cat.search(collections=["naip"], bbox=[w, s, e, n]).items())
    if not items:
        return dict(ok=False, reason="no NAIP items intersect the bbox")
    years = sorted({it.datetime.year for it in items})
    latest = [it for it in items if it.datetime.year == years[-1]]
    srcs = [rasterio.open(it.assets["image"].href) for it in latest]
    crs = srcs[0].crs
    srcs = [sr for sr in srcs if sr.crs == crs]
    bounds = transform_bounds("EPSG:4326", crs, w, s, e, n)
    arr, tr = merge(srcs, bounds=bounds)                      # native resolution
    res = abs(tr.a)
    path = os.path.join(out_dir, "naip_rgbn.tif")
    prof = dict(driver="GTiff", height=arr.shape[1], width=arr.shape[2], count=arr.shape[0],
                dtype=arr.dtype, crs=crs, transform=tr, tiled=True, blockxsize=512, blockysize=512,
                compress="deflate", predictor=2)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr)
    mb = os.path.getsize(path) / 1e6
    kind = f"{arr.shape[0]}-band deflate"
    if mb > max_mb:                                           # too big: RGB, JPEG-in-TIFF
        os.remove(path)
        path = os.path.join(out_dir, "naip_rgb.tif")
        prof.update(count=3, compress="jpeg", photometric="ycbcr", jpeg_quality=90)
        prof.pop("predictor")
        with rasterio.open(path, "w", **prof) as dst:
            dst.write(arr[:3])
        mb = os.path.getsize(path) / 1e6
        kind = "RGB JPEG-in-TIFF q90"

    # preview PNG + world file
    from PIL import Image
    rgb = np.moveaxis(arr[:3], 0, -1)
    img = Image.fromarray(rgb)
    k = max(1, math.ceil(max(img.size) / 2400))
    if k > 1:
        img = img.resize((img.width // k, img.height // k), Image.LANCZOS)
    img.save(os.path.join(out_dir, "naip_preview.png"), optimize=True)
    with open(os.path.join(out_dir, "naip_preview.pgw"), "w") as fh:
        fh.write("\n".join(str(v) for v in (tr.a * k, tr.d, tr.b, tr.e * k,
                                            tr.c + tr.a * k / 2, tr.f + tr.e * k / 2)) + "\n")
    it0 = latest[0]
    return dict(ok=True, file=os.path.basename(path), format=kind, size_mb=round(mb, 1),
                width=int(arr.shape[2]), height=int(arr.shape[1]), resolution_m=round(res, 3),
                crs=str(crs), years_available=years, year=years[-1],
                acquired=[it.datetime.date().isoformat() for it in latest],
                items=[it.id for it in latest], gsd=it0.properties.get("gsd"),
                preview_scale=k)


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="Spirit Hollow Golf Course")
    ap.add_argument("--near", default="40.745,-91.150",
                    help="approximate lat,lon (Spirit Hollow: 5592 Clubhouse Dr, ~4.5 mi S of Burlington IA)")
    ap.add_argument("--geocode", default="5592 Clubhouse Drive, Burlington, Iowa",
                    help="fallback address for Nominatim if nothing is found near --near")
    ap.add_argument("--radius", type=int, default=12000)
    ap.add_argument("--pad-m", type=float, default=120)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "spirit_hollow"))
    ap.add_argument("--no-naip", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    near = tuple(float(v) for v in a.near.split(","))
    course, cands = find_course(a.name, near, a.radius)
    if course is None and a.geocode:
        g = geocode(a.geocode)
        print("geocoded", a.geocode, "->", g)
        if g:
            course, cands = find_course(a.name, g, 3000)
    if course is None:
        raise SystemExit(f"no leisure=golf_course found for {a.name!r} near {near}")
    print("course:", course["type"], course["id"], course.get("tags", {}).get("name"), course.get("bounds"))

    bb = bounds_of(course)
    course["bounds"] = bb
    dlat = a.pad_m / 111320.0
    dlon = dlat / math.cos(math.radians(bb["minlat"]))
    bbox = (bb["minlat"] - dlat, bb["minlon"] - dlon, bb["maxlat"] + dlat, bb["maxlon"] + dlon)

    raw = fetch_features(bbox)
    with open(os.path.join(a.out, "osm_raw.json"), "w") as fh:
        json.dump(raw, fh)
    fc = to_geojson(raw["elements"])
    me = next((f for f in fc["features"] if f["properties"]["osm_type"] == course["type"]
               and f["properties"]["osm_id"] == course["id"]), None)
    rings = outer_rings(me["geometry"]) if me else []
    summary = summarise(fc, course, cands, rings)
    summary["bbox_wgs84_snwe"] = [round(v, 6) for v in bbox]
    summary["fetched_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    summary["osm_attribution"] = "© OpenStreetMap contributors, ODbL 1.0"
    with open(os.path.join(a.out, "osm.geojson"), "w") as fh:
        json.dump(fc, fh)

    if a.no_naip:
        summary["naip"] = dict(ok=False, reason="--no-naip")
    else:
        try:
            summary["naip"] = fetch_naip(bbox, a.out)
        except Exception as e:                                 # noqa: BLE001
            summary["naip"] = dict(ok=False, reason=repr(e)[:500])
    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("holes", "tees")}, indent=1))
    print("holes:", [(h["ref"], h["par"], h["nodes"], h["length_yd"]) for h in summary["holes"]])


if __name__ == "__main__":
    main()
