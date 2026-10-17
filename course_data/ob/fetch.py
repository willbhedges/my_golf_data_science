"""OB evidence layers for a course package (network: GitHub Actions only, .github/workflows/ob.yml).

  python course_data/ob/fetch.py <slug> [<slug> ...] [--pad 400] [--refetch]

Reads course_data/packages/<slug>/package.json (bbox, state) and writes course_data/ob/<slug>/:
  raw/osm.geojson          OSM buildings, landuse, highways, railways, barriers, golf=out_of_bounds and the course
                           outline in the package bbox + pad (Overpass; (c) OpenStreetMap contributors, ODbL 1.0)
  raw/ms_buildings.geojson Microsoft Global ML Building Footprints clipped to the same box (ODbL 1.0)
  raw/parcels.geojson      county / state parcels where a free source covers the state (sources.PARCEL_SOURCES):
                           Iowa: the statewide Iowa_Parcels_2017 FeatureServer (Iowa HSEMD; public, 2017 vintage)
  sources.json             what was fetched, counts, licences, errors (missing sources are recorded, not fatal)

Every source is optional: the inference (infer.py) uses whatever exists.
"""
import argparse
import csv
import gzip
import io
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
UA = {"User-Agent": "my_golf_data_science ob-inference (github.com/willbhedges/my_golf_data_science)"}

MS_LINKS = "https://minedbuildings.z5.web.core.windows.net/global-buildings/dataset-links.csv"
MS_LICENCE = "Microsoft Global ML Building Footprints, ODbL 1.0 (https://github.com/microsoft/GlobalMLBuildingFootprints)"
OSM_LICENCE = "(c) OpenStreetMap contributors, ODbL 1.0"

# Free parcel services by state. Each: ArcGIS FeatureServer layer URL, licence note. Probed services that were not
# usable are listed in PARCEL_NOTES (and in sources.json) so the next engineer does not search again.
PARCEL_SOURCES = {
    "IA": dict(url="https://services3.arcgis.com/kd9gaiUExYqUbnoq/ArcGIS/rest/services/Iowa_Parcels_2017/FeatureServer/0",
               name="Iowa_Parcels_2017 (Iowa HSEMD statewide parcels, all 99 counties, updated to 2017-11-02)",
               licence="public ArcGIS Online service by the State of Iowa (HSEMD); deprecated, no licence text "
                       "beyond the service's copyrightText (recorded at fetch time); attribution: Iowa HSEMD / "
                       "county assessors"),
}
PARCEL_NOTES = {
    "IA": "Iowa has no maintained free statewide parcel layer (geodata.iowa.gov lists none; Regrid sells one). "
          "The 2017 HSEMD statewide service is used; county portals (iowagisdata.org, Beacon) need accounts.",
    "MO": "Missouri has no free statewide parcel layer (MSDIS has none; gis.mo.gov FMDC covers state-owned land "
          "only). Nodaway County (Mozingo Lake) publishes no open parcel service: buildings + OSM only.",
}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def pad_bbox(bbox, m):
    w, s, e, n = bbox
    dlat = m / 111320.0
    dlon = dlat / math.cos(math.radians((s + n) / 2))
    return [w - dlon, s - dlat, e + dlon, n + dlat]


# ----------------------------------------------------------------------------- quadkeys (MS tiles are zoom 9)
def quadkey(lon, lat, z):
    lat = max(min(lat, 85.05112878), -85.05112878)
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    s = math.sin(math.radians(lat))
    y = int((0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n)
    x, y = min(max(x, 0), n - 1), min(max(y, 0), n - 1)
    q = ""
    for i in range(z, 0, -1):
        d, m = 0, 1 << (i - 1)
        d += 1 if x & m else 0
        d += 2 if y & m else 0
        q += str(d)
    return q


def quadkeys_for(bbox, z=9):
    w, s, e, n = bbox
    return sorted({quadkey(x, y, z) for x in (w, e) for y in (s, n)})


# ----------------------------------------------------------------------------- sources
def _get(url, **kw):
    import requests
    last = None
    for i in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=kw.pop("timeout", 120), **kw)
            if r.status_code == 200:
                return r
            last = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:                       # noqa: BLE001
            last = repr(e)
        log(f"  GET {url[:120]} failed ({last}); retry {i + 1}")
        time.sleep(10 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def fetch_osm(bbox):
    sys.path.insert(0, CD)
    import fetch_course as fcm
    w, s, e, n = bbox
    b = f"{s},{w},{n},{e}"
    q = f"""[out:json][timeout:180];
    (
      nwr["building"]({b});
      nwr["landuse"]({b});
      way["highway"]({b});
      way["railway"]({b});
      way["barrier"]({b});
      nwr["golf"="out_of_bounds"]({b});
      nwr["leisure"="golf_course"]({b});
      nwr["boundary"="protected_area"]({b});
    );
    out body geom;"""
    data = fcm.overpass(q)
    return fcm.to_geojson(data["elements"])


def _inside(coords, bbox):
    w, s, e, n = bbox
    for x, y in coords:
        if w <= x <= e and s <= y <= n:
            return True
    return False


def fetch_ms_buildings(bbox):
    r = _get(MS_LINKS)
    rows = list(csv.DictReader(io.StringIO(r.text)))
    want = set(quadkeys_for(bbox))
    urls = [row["Url"] for row in rows if row.get("Location") == "UnitedStates" and row.get("QuadKey") in want]
    feats = []
    for u in urls:
        raw = _get(u, timeout=300).content
        try:
            txt = gzip.decompress(raw).decode()
        except OSError:
            txt = raw.decode()
        for line in txt.splitlines():
            if not line.strip():
                continue
            f = json.loads(line)
            g = f.get("geometry") or {}
            if g.get("type") != "Polygon" or not _inside(g["coordinates"][0], bbox):
                continue
            feats.append(dict(type="Feature", geometry=g,
                              properties=dict(src="ms_buildings", height=(f.get("properties") or {}).get("height"))))
    return dict(type="FeatureCollection", features=feats), dict(quadkeys=sorted(want), files=urls)


def fetch_parcels(state, bbox):
    src = PARCEL_SOURCES.get(state)
    if not src:
        return None, dict(status="no free source", note=PARCEL_NOTES.get(state, "no statewide source known"))
    meta = {}
    try:
        meta = _get(src["url"] + "?f=pjson").json()
    except Exception as e:                           # noqa: BLE001
        meta = dict(error=repr(e))
    feats, off = [], 0
    w, s, e, n = bbox
    while True:
        r = _get(src["url"] + "/query", params=dict(
            geometry=f"{w},{s},{e},{n}", geometryType="esriGeometryEnvelope", inSR=4326, outSR=4326,
            spatialRel="esriSpatialRelIntersects", outFields="*", returnGeometry="true", f="geojson",
            resultOffset=off, resultRecordCount=1000))
        fc = r.json()
        got = fc.get("features") or []
        for f in got:
            f["properties"] = dict(f.get("properties") or {}, src="parcels:" + state)
        feats += got
        if len(got) < 1000 and not fc.get("exceededTransferLimit") and not (fc.get("properties") or {}).get("exceededTransferLimit"):
            break
        off += len(got)
        if not got or off > 20000:
            break
    info = dict(status="ok", name=src["name"], url=src["url"], licence=src["licence"], n=len(feats),
                copyright=meta.get("copyrightText"), description=str(meta.get("description") or "")[:600],
                note=PARCEL_NOTES.get(state))
    return dict(type="FeatureCollection", features=feats), info


def probe_missouri():
    """Record what MSDIS offers (so the 'no free MO parcels' note stays verified)."""
    out = {}
    for u in ("https://msdisweb.missouri.edu/arcgis/rest/services?f=pjson",
              "https://gis.mo.gov/arcgis/rest/services?f=pjson"):
        try:
            j = _get(u, timeout=60).json()
            names = [s.get("name") for s in j.get("services", [])] + list(j.get("folders", []))
            out[u] = [x for x in names if x and "parcel" in x.lower()] or f"{len(names)} services/folders, none named *parcel*"
        except Exception as e:                       # noqa: BLE001
            out[u] = f"error: {e!r}"[:200]
    return out


# ----------------------------------------------------------------------------- driver
def fetch(slug, pad_m=400.0, refetch=False):
    pkg = json.load(open(os.path.join(CD, "packages", slug, "package.json")))
    c = pkg["course"]
    bbox = pad_bbox(c["bbox"], pad_m)
    state = (c.get("state") or (pkg.get("request") or {}).get("state") or "").upper()[:2]
    out = os.path.join(HERE, slug)
    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    sp = os.path.join(out, "sources.json")
    srcs = json.load(open(sp)) if os.path.exists(sp) and not refetch else {}
    srcs.update(slug=slug, state=state, bbox=[round(v, 6) for v in bbox], pad_m=pad_m)

    def step(key, fn, fname, licence):
        path = os.path.join(raw, fname)
        if os.path.exists(path) and not refetch and (srcs.get(key) or {}).get("status") == "ok":
            log(f"  {key}: kept {fname}")
            return
        try:
            fc, info = fn()
            if fc is not None:
                with open(path, "w") as fh:
                    json.dump(fc, fh, separators=(",", ":"))
                info = dict(info or {}, n=len(fc["features"]), file=os.path.relpath(path, ROOT))
            srcs[key] = dict(dict(status="ok", licence=licence), **(info or {}))
        except Exception as e:                       # noqa: BLE001
            srcs[key] = dict(status=f"failed: {type(e).__name__}: {str(e)[:300]}", licence=licence)
        srcs[key]["fetched"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        log(f"  {key}: {srcs[key].get('status')} n={srcs[key].get('n')}")

    step("osm", lambda: (fetch_osm(bbox), {}), "osm.geojson", OSM_LICENCE)
    step("ms_buildings", lambda: fetch_ms_buildings(bbox), "ms_buildings.geojson", MS_LICENCE)
    step("parcels", lambda: fetch_parcels(state, bbox), "parcels.geojson",
         (PARCEL_SOURCES.get(state) or {}).get("licence", "n/a"))
    if state == "MO" and "mo_probe" not in srcs:
        srcs["mo_probe"] = probe_missouri()
    with open(sp, "w") as fh:
        json.dump(srcs, fh, indent=1)
    return srcs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--pad", type=float, default=400.0)
    ap.add_argument("--refetch", action="store_true")
    a = ap.parse_args(argv)
    for s in a.slugs:
        log(f"== {s}")
        fetch(s, a.pad, a.refetch)


if __name__ == "__main__":
    main()
