"""NAIP acquisition-year selection: which NAIP year should a course package show (and detect on)?

  python3 course_data/imagery/naip_years.py --bbox S,W,N,E --osm course_data/packages/<slug>/raw/osm.geojson \
      [--out naip_years.json]          # GitHub Actions (Planetary Computer): list + score every NAIP year
  python3 course_data/imagery/naip_years.py --local course_data/vision_any/<slug>/raw --osm ...   # offline:
      score the per-year rasters already fetched for vision_any (naip_<year>.tif, R,G,B,NIR)

Why: packages used to take the LATEST NAIP year (fetch_imagery.fetch_naip). In Iowa that is the 2023-09 flight,
a drought year: fairways and greens are straw-brown, the page is hard to read and every turf detector is starved.
At Wakonda the 2023 flight caught the course mid-renovation: the greens of holes 5, 9, 15 and 17 (two of the four
par 3s) are bare soil, so the app drew those greens' outlines on dirt.

Each year's acquisitions are read over the course box at SCORE_RES metres (decimated COG reads, a few MB per
year) and measured on the turf the course's OSM map names (golf=fairway / green / tee; the whole vegetated box
when OSM has no turf):
  turf_ndvi     median NDVI (NIR - R) / (NIR + R) over the OSM turf: the greenness signal
  turf_exg      median excess green 2G - R - B over the same turf: how green the page LOOKS
  bare_turf     share of turf pixels with NDVI < BARE_NDVI (drought-brown, dormant or bare)
  greens_bare   share of OSM greens that are not visible as turf (green_visibility: NDVI far below the course's
                other greens, or below 0) - construction, a dead green, a green that did not exist yet
  cloud         share of turf pixels bright in R, G and B with low NDVI (cloud, glare)
  haze          dark-object level: 2nd percentile of the blue band over the box (haze lifts the shadows)
  coverage      share of the course box the year's acquisitions cover (< MIN_COVER: not eligible)
  date          leaf-on window LEAF_ON (May 1 - Sep 30); a dormant-season flight pays LEAF_OFF_PEN
  gsd           0.3 m beats 0.6 m; 1 m years are only eligible when no <= 0.6 m year covers the course
score = turf_ndvi + EXG_W turf_exg - 0.6 bare_turf - 1.0 greens_bare - cloud - haze penalty - leaf-off penalty
        + resolution bonus - AGE_PEN x years older than the newest year (OSM, tees and bunkers describe the course
        as it is now; old flights predate renovations, so an old year has to be clearly greener to win).
The chosen year + a one-line reason go into georef.json["imagery"]["selection"] (fetch_imagery.py) and from there
into package.json["imagery"]["selection"] (platform/package.py imagery_ref).

green_visibility(holes, img_dir) is the per-hole check the package build runs on whichever imagery it ships:
a hole whose green is not visible is flagged (confidence flags -> the app's "check" badge).
"""
import argparse
import datetime as dt
import glob
import json
import math
import os
import re
import sys

import numpy as np

SCORE_RES = 1.2                  # metres for scoring reads; greens are 400-800 m2 -> 300+ px each
BARE_NDVI = 0.15
GREEN_REL_DROP = 0.12            # a green this far below the median green NDVI of the same flight is not turf
LEAF_ON = ((5, 1), (9, 30))
LEAF_OFF_PEN = 0.5               # dormant-season flights only win when no leaf-on year covers the course
AGE_PEN = 0.015                  # per year older than the newest covering year (renovations, storms: Ellis 2020 derecho)
FINE_GSD = 0.6                   # with a year at <= 0.6 m covering the course, 1 m years are not eligible
EXG_W = 0.001
HAZE_FREE, HAZE_SCALE = 35.0, 400.0
GSD_BONUS = {0.3: 0.03, 0.6: 0.0, 1.0: -0.04}
MIN_COVER = 0.995
TURF_TAGS = ("fairway", "green", "tee")


# ----------------------------------------------------------------------------- turf masks
def turf_polygons(fc):
    """OSM golf=fairway / green / tee (Multi)Polygons of a GeoJSON FeatureCollection -> {tag: [geoms]} (WGS84)."""
    from shapely.geometry import shape
    out = {k: [] for k in TURF_TAGS}
    for f in (fc or {}).get("features", []):
        tag = (f.get("properties") or {}).get("golf")
        g = f.get("geometry") or {}
        if tag in out and g.get("type") in ("Polygon", "MultiPolygon"):
            try:
                geom = shape(g)
            except Exception:                                    # noqa: BLE001
                continue
            if not geom.is_valid:
                geom = geom.buffer(0)
            if not geom.is_empty:
                out[tag].append(geom)
    return out


def rasterize_ll(geoms, crs, transform, shape, labels=False):
    """WGS84 geometries -> bool mask (or int labels 1..n, 0 = none) on a raster grid."""
    from pyproj import Transformer
    from rasterio.features import rasterize
    from shapely.ops import transform as stx
    if not geoms:
        return np.zeros(shape, np.int32 if labels else bool)
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    gs = [stx(tr.transform, g) for g in geoms]
    if labels:
        return rasterize([(g, i + 1) for i, g in enumerate(gs)], out_shape=shape, transform=transform, dtype="int32")
    return rasterize(gs, out_shape=shape, transform=transform).astype(bool)


def ndvi_of(red, nir):
    red, nir = red.astype(np.float32), nir.astype(np.float32)
    return (nir - red) / np.maximum(nir + red, 1.0)


# ----------------------------------------------------------------------------- greens
def green_ndvi(ndvi, labels, n, valid=None, min_px=12):
    """Median NDVI of each labelled green 1..n (None when it has fewer than min_px valid pixels)."""
    out = []
    for i in range(1, n + 1):
        m = labels == i
        if valid is not None:
            m &= valid
        out.append(float(np.median(ndvi[m])) if m.sum() >= min_px else None)
    return out


def bare_greens(meds):
    """Which greens are not visible as turf: NDVI GREEN_REL_DROP below the median of the flight's greens, or
    below 0 (soil, water, shadow) while the course's greens are vegetated. -> [bool or None per green]."""
    vals = [v for v in meds if v is not None]
    if len(vals) < 3:
        return [None] * len(meds)
    med = float(np.median(vals))
    return [None if v is None else bool(v < med - GREEN_REL_DROP or (v < 0.0 < med - 0.05)) for v in meds]


def green_visibility(holes, img_dir):
    """Per hole of a package ({ref: hole with green_polygon_ll}) on the package imagery (img_dir with
    georef.json, naip_rgb.tif + naip_nir.tif) -> {ref: {ndvi, course_median, visible}} or {} when the imagery
    has no NIR band / is missing."""
    import rasterio
    from shapely.geometry import Polygon
    g = json.load(open(os.path.join(img_dir, "georef.json"))) if img_dir and os.path.exists(
        os.path.join(img_dir, "georef.json")) else {}
    files = (g.get("imagery") or {}).get("files") or {}
    if not files.get("rgb") or not files.get("nir"):
        return {}
    pr, pn = os.path.join(img_dir, files["rgb"]), os.path.join(img_dir, files["nir"])
    if not (os.path.exists(pr) and os.path.exists(pn)):
        return {}
    refs = [k for k, h in holes.items() if h.get("green_polygon_ll") and len(h["green_polygon_ll"]) >= 3]
    if not refs:
        return {}
    geoms = []
    for k in refs:
        p = Polygon(holes[k]["green_polygon_ll"])
        geoms.append(p if p.is_valid else p.buffer(0))
    with rasterio.open(pr) as sr, rasterio.open(pn) as sn:
        red, nir = sr.read(1), sn.read(1)
        lab = rasterize_ll(geoms, sr.crs, sr.transform, red.shape, labels=True)
    valid = (red > 0) | (nir > 0)
    meds = green_ndvi(ndvi_of(red, nir), lab, len(refs), valid)
    bare = bare_greens(meds)
    vals = [v for v in meds if v is not None]
    cm = round(float(np.median(vals)), 3) if vals else None
    return {k: dict(ndvi=None if v is None else round(v, 3), course_median=cm,
                    visible=None if b is None else (not b)) for k, v, b in zip(refs, meds, bare)}


# ----------------------------------------------------------------------------- metrics + score
def metrics(rgbn, valid, turf, green_labels, n_greens):
    """rgbn (4, H, W), valid / turf bool (H, W), green_labels int (H, W) with n_greens greens -> scoring metrics."""
    r, g, b, n = (rgbn[i].astype(np.float32) for i in range(4))
    ndvi = ndvi_of(r, n)
    use = turf & valid
    fallback = use.sum() < 200
    if fallback:
        use = valid & (ndvi > 0.0)
    t = ndvi[use]
    exg = (2 * g - r - b)[use]
    bright = (r > 200) & (g > 200) & (b > 200) & (ndvi < 0.1)
    gm = (green_labels > 0) & valid
    meds = green_ndvi(ndvi, green_labels, n_greens, valid, min_px=8)
    bare = bare_greens(meds)
    known = [x for x in bare if x is not None]
    return dict(
        turf_ndvi=round(float(np.median(t)), 4) if t.size else None,
        turf_exg=round(float(np.median(exg)), 1) if exg.size else None,
        green_ndvi=round(float(np.median(ndvi[gm])), 4) if gm.sum() >= 30 else None,
        bare_turf=round(float((t < BARE_NDVI).mean()), 4) if t.size else None,
        greens_bare=round(sum(known) / len(known), 4) if known else 0.0,
        greens_bare_n=int(sum(known)), greens_n=len(known),
        cloud=round(float(bright[use].mean()), 4) if use.any() else None,
        haze=round(float(np.percentile(b[valid], 2)), 1) if valid.any() else None,
        turf_rgb=[round(float(np.median(c)), 1) for c in np.stack([r, g, b])[:, use]] if use.any() else None,
        turf_px=int(use.sum()), turf_source="box (no OSM turf)" if fallback else "osm")


def leaf_on(date):
    d = dt.date.fromisoformat(str(date)[:10])
    (m0, d0), (m1, d1) = LEAF_ON
    return dt.date(d.year, m0, d0) <= d <= dt.date(d.year, m1, d1)


def score(c, newest):
    """Candidate (metrics + year, dates, coverage, gsd_m, has_nir) -> (score or None, [notes])."""
    if c.get("coverage", 1.0) < MIN_COVER:
        return None, [f"covers {100 * c.get('coverage', 0):.0f}% of the course"]
    if not c.get("has_nir") or c.get("turf_ndvi") is None:
        return None, ["no NIR band" if not c.get("error") else "read failed"]
    notes = []
    s = float(c["turf_ndvi"]) + EXG_W * float(c.get("turf_exg") or 0.0)
    s -= 0.6 * float(c.get("bare_turf") or 0.0)
    s -= 1.0 * float(c.get("greens_bare") or 0.0)
    s -= 1.0 * float(c.get("cloud") or 0.0)
    hz = c.get("haze")
    if hz is not None and hz > HAZE_FREE:
        s -= (hz - HAZE_FREE) / HAZE_SCALE
        if hz > 60:
            notes.append(f"hazy (blue floor {hz:.0f})")
    dates = c.get("dates") or []
    if dates and not all(leaf_on(d) for d in dates):
        s -= LEAF_OFF_PEN
        notes.append("leaf-off flight")
    gsd = c.get("gsd_m")
    if gsd:
        s += GSD_BONUS[min(GSD_BONUS, key=lambda k: abs(k - float(gsd)))]
    s -= AGE_PEN * max(0, int(newest) - int(c["year"]))
    if (c.get("greens_bare_n") or 0) > 0:
        notes.append(f"{c['greens_bare_n']} of {c['greens_n']} greens not visible as turf")
    if (c.get("bare_turf") or 0) > 0.3:
        notes.append(f"{100 * c['bare_turf']:.0f}% of the turf brown / bare")
    if (c.get("cloud") or 0) > 0.02:
        notes.append(f"cloud / glare on {100 * c['cloud']:.0f}% of the turf")
    return round(s, 4), notes


def select(cands, current_year=None):
    """[candidate] -> (chosen, reason, candidates newest first). Equal scores (to 0.001) go to the newer year."""
    cover = [c for c in cands if c.get("coverage", 1.0) >= MIN_COVER]
    newest = max((c["year"] for c in (cover or cands)), default=0)
    fine = any(c.get("has_nir") and float(c.get("gsd_m") or 1.0) <= FINE_GSD for c in cover)
    for c in cands:
        c["score"], c["notes"] = score(c, newest)
        if fine and c["score"] is not None and float(c.get("gsd_m") or 1.0) > FINE_GSD:
            c["score"], c["notes"] = None, c["notes"] + [f"{c.get('gsd_m')} m: too coarse for the page "
                                                         f"(a {FINE_GSD} m year covers the course)"]
    elig = [c for c in cands if c["score"] is not None]
    out = sorted(cands, key=lambda c: -c["year"])
    if not elig:
        return None, "no NAIP year with an NIR band covers the course", out
    best = max(elig, key=lambda c: (round(c["score"], 3), c["year"]))
    latest = max(elig, key=lambda c: c["year"])
    if best is latest:
        reason = (f"{best['year']} ({', '.join(best.get('dates') or [])}) is the newest NAIP year covering the "
                  f"course and also scores best (turf NDVI {best['turf_ndvi']:.2f}"
                  + (f"; {'; '.join(best['notes'])}" if best["notes"] else "") + ")")
    else:
        reason = (f"{best['year']} ({', '.join(best.get('dates') or [])}): greenest leaf-on year on the course's "
                  f"turf (NDVI {best['turf_ndvi']:.2f} vs {latest['turf_ndvi']:.2f}, "
                  f"{100 * (best.get('bare_turf') or 0):.0f}% vs {100 * (latest.get('bare_turf') or 0):.0f}% brown) "
                  f"over the newest year {latest['year']} ({'; '.join(latest['notes']) or 'less green'})")
    if current_year and int(current_year) != best["year"]:
        reason += f"; replaces {current_year}"
    return best, reason, out


def record(chosen, reason, cands):
    """The block stored as georef.json imagery.selection -> package.json imagery.selection."""
    keep = ("year", "dates", "gsd_m", "coverage", "turf_ndvi", "turf_exg", "green_ndvi", "bare_turf", "greens_bare",
            "greens_bare_n", "cloud", "haze", "turf_rgb", "score", "notes", "turf_source", "error")
    return dict(schema="naip_years/1", method="best-scoring leaf-on NAIP year on the OSM turf "
                                              "(course_data/imagery/naip_years.py)",
                chosen=chosen["year"] if chosen else None, reason=reason,
                candidates=[{k: c.get(k) for k in keep if c.get(k) is not None} for c in cands])


def _score_array(arr, crs, transform, polys, extra):
    valid = arr[:3].astype(np.int32).sum(0) > 0
    turf = np.zeros(arr.shape[1:], bool)
    for tag in TURF_TAGS:
        turf |= rasterize_ll(polys[tag], crs, transform, arr.shape[1:])
    lab = rasterize_ll(polys["green"], crs, transform, arr.shape[1:], labels=True)
    c = dict(extra, has_nir=arr.shape[0] >= 4)
    if c["has_nir"]:
        c.update(metrics(arr, valid, turf, lab, len(polys["green"])))
    return c


# ----------------------------------------------------------------------------- local rasters (offline)
def score_local(raw_dir, fc):
    """vision_any/<slug>/raw (naip_<year>.tif R,G,B,NIR + meta.json) -> candidates."""
    import rasterio
    mp = os.path.join(raw_dir, "meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    info = {y["year"]: y for y in (meta.get("naip") or {}).get("years", [])}
    polys = turf_polygons(fc)
    out = []
    for p in sorted(glob.glob(os.path.join(raw_dir, "naip_*.tif"))):
        m = re.search(r"naip_(\d{4})\.tif$", p)
        if not m:
            continue
        yr = int(m.group(1))
        with rasterio.open(p) as src:
            arr, crs, tr = src.read(), src.crs, src.transform
        i = info.get(yr) or {}
        out.append(_score_array(arr, crs, tr, polys, dict(year=yr, dates=i.get("acquired") or [], gsd_m=i.get("gsd_m"),
                                                          coverage=float((arr[:3].sum(0) > 0).mean()))))
    return out


# ----------------------------------------------------------------------------- Planetary Computer (Actions)
def list_years(bbox_snwe):
    """Every NAIP acquisition over the box, grouped by year -> [{year, items, dates, coverage, gsd_m}]."""
    from shapely.geometry import box, shape
    from shapely.ops import unary_union
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fetch_imagery import stac_client
    s, w, n, e = bbox_snwe
    items = list(stac_client().search(collections=["naip"], bbox=[w, s, e, n]).items())
    aoi = box(w, s, e, n)
    years = []
    for yr in sorted({it.datetime.year for it in items}):
        its = [it for it in items if it.datetime.year == yr]
        cov = unary_union([shape(it.geometry) for it in its]).intersection(aoi).area / aoi.area
        years.append(dict(year=yr, items=its, dates=sorted({it.datetime.date().isoformat() for it in its}),
                          coverage=round(cov, 4), gsd_m=its[0].properties.get("gsd")))
    return years


def read_year(its, bbox_snwe, res=SCORE_RES):
    """Mosaic one year's items over the box at `res` metres -> (arr (bands, H, W) uint8, crs, transform)."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject, transform_bounds
    s, w, n, e = bbox_snwe
    with rasterio.open(its[0].assets["image"].href) as s0:
        crs, nb = s0.crs, min(s0.count, 4)
    x0, y0, x1, y1 = transform_bounds("EPSG:4326", crs, w, s, e, n, densify_pts=21)
    W, H = int(math.ceil((x1 - x0) / res)), int(math.ceil((y1 - y0) / res))
    tr = rasterio.transform.from_origin(x0, y1, res, res)
    out = np.zeros((nb, H, W), np.uint8)
    for it in its:
        with rasterio.open(it.assets["image"].href) as src:
            for b in range(min(nb, src.count)):
                dst = np.zeros((H, W), np.uint8)
                reproject(rasterio.band(src, b + 1), dst, src_nodata=0, dst_transform=tr, dst_crs=crs, dst_nodata=0,
                          resampling=Resampling.average)
                out[b] = np.where(dst > 0, dst, out[b])
    return out, crs, tr


def score_remote(bbox_snwe, fc, log=print):
    polys = turf_polygons(fc)
    cands = []
    for y in list_years(bbox_snwe):
        extra = dict(year=y["year"], dates=y["dates"], coverage=y["coverage"], gsd_m=y["gsd_m"],
                     items=[it.id for it in y["items"]])
        try:
            arr, crs, tr = read_year(y["items"], bbox_snwe)
            c = _score_array(arr, crs, tr, polys, extra)
        except Exception as ex:                                  # noqa: BLE001
            c = dict(extra, has_nir=False, error=repr(ex)[:300])
        log(f"  NAIP {c['year']} {c['dates']} cover {c['coverage']:.3f} gsd {c.get('gsd_m')}: turf NDVI "
            f"{c.get('turf_ndvi')} exg {c.get('turf_exg')} bare {c.get('bare_turf')} greens bare "
            f"{c.get('greens_bare_n')}/{c.get('greens_n')} haze {c.get('haze')} {c.get('error', '')}")
        cands.append(c)
    return cands


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bbox", help="S,W,N,E (WGS84)")
    ap.add_argument("--local", help="dir with naip_<year>.tif (vision_any raw)")
    ap.add_argument("--osm", help="osm.geojson with golf=fairway / green / tee")
    ap.add_argument("--current", type=int, help="the year the package ships now (for the reason line)")
    ap.add_argument("--out")
    a = ap.parse_args()
    fc = json.load(open(a.osm)) if a.osm else None
    cands = score_local(a.local, fc) if a.local else score_remote(tuple(map(float, a.bbox.split(","))), fc)
    chosen, reason, cands = select(cands, a.current)
    rec = record(chosen, reason, cands)
    print(json.dumps(rec, indent=1))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(rec, fh, indent=1)


if __name__ == "__main__":
    main()
