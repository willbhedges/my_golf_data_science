"""Q3: tee-pad candidates from the USGS 3DEP 1 m bare-earth DEM, for holes whose card set has no OSM box.

    python3 course_data/tees/lidar_pads.py [slug ...]     # validate against the OSM boxes that exist
                                                          # -> course_data/tees/lidar_pads_validation.json

A tee pad is a levelled, slightly raised platform with banked sides. On the 1 m DEM (Gaussian sigma 1 m):
  flat     slope < FLAT_PCT (5 %)
  raised   white top-hat z - opening(z, disk 15 m) > 0.05 m (a plane, even a steep one, gives 0; a pad
           narrower than the 30 m disk stands out by its fill height)
  pad      a connected flat+raised component of 30-2,000 m2 whose mean top-hat >= 0.10 m and whose 1-4 m
           outer ring is >= 30 % bank (slope > 10 %)
Greens are flat and raised too, so components within 25 yds of an OSM green centroid are dropped; the
caller keeps only pads near a hole's first leg (place_tee.assign_tees_to_holes, as for OSM boxes), and
place_tee.place_course_sets uses them only where a set has no OSM box within 10 yds (cost +6 yds).

Thresholds were set on Spirit Hollow's 103 OSM boxes (precision / recall within 10 yds are in
lidar_pads_validation.json; Veenker and Mozingo Lake are the held-out check). Precision counts a pad
that matches no OSM box as false, although some are real unmapped tees, so it is a lower bound.
Public-domain data (USGS 3DEP); CPU seconds per course.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import place_tee as pt  # noqa: E402

FLAT_PCT = 5.0
TOPHAT_MIN_M = 0.05
TOPHAT_MEAN_M = 0.10
TOPHAT_RADIUS_M = 15
BANK_PCT = 10.0
BANK_FRAC = 0.30
AREA_M2 = (30.0, 2000.0)
GREEN_CLEAR_YD = 25.0
MATCH_YD = 10.0


def pad_mask(z, res_m=1.0):
    """(pad pixels, slope %, top-hat m) for a DEM array (metres, square pixels of res_m)."""
    from scipy import ndimage as ndi
    zz = np.where(np.isfinite(z), z, np.nanmedian(z))
    zs = ndi.gaussian_filter(zz, 1.0 / res_m)
    gy, gx = np.gradient(zs, res_m)
    slope = np.hypot(gx, gy) * 100.0
    r = max(1, int(round(TOPHAT_RADIUS_M / res_m)))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (xx ** 2 + yy ** 2) <= r * r
    tophat = zs - ndi.grey_opening(zs, footprint=disk)
    m = (slope < FLAT_PCT) & (tophat > TOPHAT_MIN_M) & np.isfinite(z)
    m = ndi.binary_opening(m, iterations=1)
    return m, slope, tophat


def components(z, res_m=1.0):
    """Pad components in pixel space: [{rows, cols, area_m2, tophat_m, slope_pct, bank_frac}]."""
    from scipy import ndimage as ndi
    m, slope, tophat = pad_mask(z, res_m)
    lab, n = ndi.label(m)
    out = []
    px = res_m * res_m
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        if sl is None:
            continue
        r0, c0 = max(sl[0].start - 5, 0), max(sl[1].start - 5, 0)
        r1, c1 = sl[0].stop + 5, sl[1].stop + 5
        sub = lab[r0:r1, c0:c1] == i
        area = float(sub.sum()) * px
        if not AREA_M2[0] <= area <= AREA_M2[1]:
            continue
        th = float(tophat[r0:r1, c0:c1][sub].mean())
        if th < TOPHAT_MEAN_M:
            continue
        ring = ndi.binary_dilation(sub, iterations=4) & ~ndi.binary_dilation(sub, iterations=1)
        bank = float((slope[r0:r1, c0:c1][ring] > BANK_PCT).mean()) if ring.any() else 0.0
        if bank < BANK_FRAC:
            continue
        rr, cc = np.nonzero(sub)
        out.append(dict(rows=rr + r0, cols=cc + c0, area_m2=round(area, 1), tophat_m=round(th, 3),
                        slope_pct=round(float(slope[r0:r1, c0:c1][sub].mean()), 2), bank_frac=round(bank, 3)))
    return out


def _hull(points):
    """Convex hull (monotone chain) of (x, y) points, counter-clockwise, not closed."""
    pts = sorted(set(map(tuple, points)))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def detect_pads(dem_path, greens=(), lines=None):
    """Tee-pad candidates from a DEM GeoTIFF: [{id: 'lidar:<n>', coords: [(lat, lon), ...] (convex hull),
    centroid: (lat, lon), source: 'lidar', area_m2, tophat_m, slope_pct, bank_frac}]. With `lines`
    ({ref: [(lat, lon), ...]}) only pads near some hole's first leg are kept (assign_tees_to_holes)."""
    import rasterio
    from pyproj import Transformer
    with rasterio.open(dem_path) as src:
        z = src.read(1).astype(np.float64)
        if src.nodata is not None and np.isfinite(src.nodata):
            z[z == src.nodata] = np.nan
        T, crs = src.transform, src.crs
    res = abs(T.a)
    if crs is None or crs.is_geographic or res > 2.0:
        # not a ~1 m lidar DEM in metres (e.g. Pine Dunes TX: 3DEP only has the 1/3" ~10 m DEM, in degrees):
        # res would be read as metres and the 15 m top-hat disk would be ~160 000 px wide (MemoryError)
        return []
    inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    gc = [pt.centroid_ll(g["coords"]) for g in greens if len(g["coords"]) >= 3]
    pads = []
    for comp in components(z, res):
        cx, ry = comp["cols"] + 0.5, comp["rows"] + 0.5
        xs, ys = T.c + T.a * cx + T.b * ry, T.f + T.d * cx + T.e * ry
        hull = _hull(np.c_[xs, ys])
        lon, lat = inv.transform([p[0] for p in hull], [p[1] for p in hull])
        cl = inv.transform(float(np.mean(xs)), float(np.mean(ys)))
        c = (cl[1], cl[0])
        if gc and min(pt.haversine_yd(c, g) for g in gc) <= GREEN_CLEAR_YD:
            continue
        pads.append(dict(id=f"lidar:{len(pads)}", coords=list(zip(lat, lon)), centroid=c, source="lidar",
                         **{k: comp[k] for k in ("area_m2", "tophat_m", "slope_pct", "bank_frac")}))
    if lines:
        keep = {id(p) for ts in pt.assign_tees_to_holes(lines, pads).values() for p in ts}
        pads = [p for p in pads if id(p) in keep]
    return pads


def validate(pads, osm_tees, match_yd=MATCH_YD):
    """Precision / recall of pads against the OSM boxes (centroids within match_yd)."""
    oc = [pt.centroid_ll(t["coords"]) for t in osm_tees if t["coords"]]
    pc_ = [p["centroid"] for p in pads]
    tp = sum(1 for p in pc_ if oc and min(pt.haversine_yd(p, c) for c in oc) <= match_yd)
    hit = sum(1 for c in oc if pc_ and min(pt.haversine_yd(p, c) for p in pc_) <= match_yd)
    return dict(pads=len(pc_), osm_boxes=len(oc), precision=round(tp / max(len(pc_), 1), 3),
                recall=round(hit / max(len(oc), 1), 3), match_yd=match_yd)


def main():
    import eval_tees as E
    slugs = sys.argv[1:] or list(E.COURSES)
    out = {}
    for slug in slugs:
        c = E.COURSES[slug]
        dem = os.path.join(ROOT, c["dem"])
        if not os.path.exists(dem):
            out[slug] = "no DEM"
            continue
        lines, tees, greens = E.load_osm(os.path.join(ROOT, c["osm"]))
        pads = detect_pads(dem, greens=greens, lines=lines)
        near = [t for ts in pt.assign_tees_to_holes(lines, tees).values() for t in ts]
        out[slug] = dict(validate(pads, near), role="tuned" if slug == "spirit_hollow" else "held out")
        print(slug, out[slug], flush=True)
    path = os.path.join(HERE, "lidar_pads_validation.json")
    json.dump(dict(doc="lidar_pads.detect_pads vs the OSM golf=tee boxes near each hole's first leg; a pad "
                       "matches when the centroids are within match_yd", params=dict(
                           FLAT_PCT=FLAT_PCT, TOPHAT_MIN_M=TOPHAT_MIN_M, TOPHAT_MEAN_M=TOPHAT_MEAN_M,
                           TOPHAT_RADIUS_M=TOPHAT_RADIUS_M, BANK_PCT=BANK_PCT, BANK_FRAC=BANK_FRAC, AREA_M2=AREA_M2,
                           GREEN_CLEAR_YD=GREEN_CLEAR_YD), courses=out), open(path, "w"), indent=1)
    print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
