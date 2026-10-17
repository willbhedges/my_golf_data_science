"""Tee-set localizer v2: every card tee set on every hole -> a point on the ground + an uncertainty.

    python3 course_data/tees/eval_localize.py      # before / after on the truth courses (eval_localize.md)

Used by platform/package.py as an optional S2 stage (request "tee_localizer": "v2", or env
TEE_LOCALIZER=v2); the default S2 (tees/place_tee.place_course_sets) stays the fallback, and is used
whenever this module raises.

1. Candidates (pads where a tee set can stand), merged across sources:
     osm       golf=tee polygons / nodes                                     prior p 0.97
     segment   NAIP segment-model tee polygons (course_data/segment/<slug>/segment.geojson, p)  p * 0.85
     scene     perception tee-complex boxes (course_scene/1 scene.json, p)                       p * 0.85
     lidar     lidar_pads.detect_pads (flat, raised, banked 3DEP pads)                           0.60
     texture   texture_pads below: flat + levelled 3DEP pixel AND mown NAIP texture (low NIR
               variance, green), bounded by a bank or cut; catches pads lidar_pads misses
               because they are not raised (flat ground, pads cut into a slope)              0.40
   Candidates whose footprints overlap or whose centroids are within MERGE_YD are one pad;
   p_real = 1 - prod(1 - p_source) (independent evidence), geometry from the best source.
   Each hole takes the candidates beside its first leg (place_tee.assign_tees_to_holes rule) plus,
   at a cost, other holes' pads (shared complexes) within BORROW_ERR_YD of the card yardage.

2. Where on a pad: the point on the axis through the pad centroid parallel to the first leg at the
   card yardage, clamped to the pad's inner extent (markers stand inside the box, not on its edge).
   Yardage is measured the USGA way (place_tee.LineOfPlay: to the green centre along the line of
   play, through the dog-leg turning points; the green centre is the OSM green centroid).

3. Assignment (all sets of one hole jointly, back to front by card yardage), a chain model:
     unary    |measured - (card + b)| beyond the pad's extent (yds) + centre_w |centroid - (card + b)|
              + prior_yd * -ln p_real + off_w per yd beyond off_free_yd off the first leg (+4 borrowed)
              walk-back along the hole line (no pad): walkback
     pairwise order (a longer set never in front of a shorter one, 2 yds slack) ORDER;
              the 'difference trick' 0.25 * min(|e_i - e_j|, 10) (gaps between sets match the card);
              two sets on one pad that is shorter than 0.6 x their card gap: SHARE (multi-box complexes)
     b        optional per-hole measuring bias (our hole line / green centroid vs the card's measuring line):
              a grid +-bias_max with a N(0, bias_sd) prior, all sets move together. OFF by default
              (bias_max 0): on the train courses it raised the OSM-hidden p90 (11 -> 14 yds) and on Spirit
              Hollow the median (9.8 -> 13.6 yds) - the extents of real boxes already absorb the bias.
   Weights (walkback 20, prior 4, offset 0.2/yd beyond 30, centre 0.05) were chosen on the generalize train
   split only (OSM tees hidden, eval_localize.py C2); Spirit Hollow / Mozingo / the test split were not used.
   MAP: exact min-sum DP per bias value. Uncertainty: the same chain with weights exp(-cost / T)
   (sum-product, marginalised over b): p_assign = P(the chosen pad), sigma_yd = sqrt(E|x - x_MAP|^2
   + within-pad and source variance), split into along / across the first leg.

Output: tee_positions-shaped dict (place_tee.place_course_sets format, so geometry/build_holes and
platform/package.py take it unchanged) with extra keys per set: sigma_yd, sigma_along_yd, sigma_lat_yd,
p_assign, bias_yd, sources, alternatives (top 3 pads with probability).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE] if HERE not in sys.path else []
import place_tee as pt  # noqa: E402

VERSION = "tees/localize v2"
SOURCE_P = {"osm": 0.97, "lidar": 0.60, "texture": 0.40}
SEGMENT_SCALE = 0.85
SOURCE_SD = {"osm": 2.0, "segment": 4.0, "scene": 4.0, "lidar": 4.0, "texture": 5.0, "walkback": 15.0}
SOURCE_RANK = ["osm", "segment", "scene", "lidar", "texture"]

PARAMS = dict(
    merge_yd=7.0,          # candidates closer than this are one pad
    prior_yd=4.0,          # cost per unit of -ln p_real
    centre_w=0.05,         # pull toward the pad centroid (markers sit mid-box)
    inner_yd=0.0,          # clamp the point this far inside the pad's extent
    snap_yd=0.0,           # an unshared pad whose centroid is within snap_yd of the card: the centroid
    off_free_yd=30.0, off_w=0.2, max_offset_yd=130.0, max_behind_yd=150.0,
    max_err_yd=25.0, borrow_err_yd=10.0, borrow_cost=4.0,
    walkback=20.0, order=100.0, order_tol=2.0, gap_w=0.25, gap_cap=10.0, share=2.0,
    bias_sd=3.0, bias_max=0.0, bias_step=2.0, temp=3.0,
)


# ----------------------------------------------------------------------------- candidate sources
def osm_candidates(tees):
    return [dict(id=t.get("id"), coords=list(t["coords"]), source="osm", p=SOURCE_P["osm"]) for t in tees]


def segment_candidates(fc_or_path, min_p=0.3):
    """Tee polygons of a segment-model FeatureCollection (class 'tee' or golf=tee) -> candidates."""
    fc = json.load(open(fc_or_path)) if isinstance(fc_or_path, str) else fc_or_path
    out = []
    for i, f in enumerate((fc or {}).get("features", [])):
        p = f.get("properties") or {}
        if (p.get("class") or p.get("golf")) != "tee" or f["geometry"]["type"] != "Polygon":
            continue
        q = float(p.get("p", 0.7))
        if q < min_p:
            continue
        ring = [(c[1], c[0]) for c in f["geometry"]["coordinates"][0]]
        out.append(dict(id=f"segment:{i}", coords=ring, source="segment", p=SEGMENT_SCALE * q))
    return out


def scene_candidates(scene_or_path, min_p=0.3):
    """Perception scene (course_scene/1) tee-complex boxes -> candidates."""
    sc = json.load(open(scene_or_path)) if isinstance(scene_or_path, str) else scene_or_path
    out = []
    for tc in (sc or {}).get("tee_complexes", []):
        for b in tc.get("boxes", []):
            q = float(b.get("p", tc.get("p", 0.6)))
            if q < min_p or not b.get("polygon"):
                continue
            out.append(dict(id=f"scene:{b.get('id')}", coords=[(c[1], c[0]) for c in b["polygon"]], source="scene",
                            p=SEGMENT_SCALE * q))
    return out


def lidar_candidates(pads):
    return [dict(id=p["id"], coords=list(p["coords"]), source="lidar", p=SOURCE_P["lidar"]) for p in pads]


def texture_pads(dem_path, nir_path=None, rgb_path=None, greens=(), lines=None, flat_pct=3.0, bank_pct=8.0,
                 bank_frac=0.2, area_m2=(40.0, 1500.0), green_clear_yd=25.0):
    """Tee-pad candidates from 3DEP flatness + NAIP mown texture (no 'raised' requirement, unlike
    lidar_pads): pixels with slope < flat_pct on a 1 m DEM (Gaussian 1 m), a small Laplacian (levelled,
    not a gentle dome), NAIP NDVI > 0.15 and a low 3 m NIR standard deviation (mown turf, not rough or
    trees); components of area_m2 whose 1-4 m outer ring is >= bank_frac bank (slope > bank_pct). Greens
    are dropped (green_clear_yd); with `lines` only pads beside some hole's first leg are kept.
    -> [{id: 'texture:<n>', coords [(lat, lon)] hull, centroid, source: 'texture', area_m2}]"""
    import rasterio
    from pyproj import Transformer
    from rasterio.warp import Resampling, reproject
    from scipy import ndimage as ndi
    import lidar_pads as lp
    with rasterio.open(dem_path) as src:
        z = src.read(1).astype(np.float64)
        if src.nodata is not None and np.isfinite(src.nodata):
            z[z == src.nodata] = np.nan
        T, crs, shape = src.transform, src.crs, z.shape
    res = abs(T.a)
    zz = np.where(np.isfinite(z), z, np.nanmedian(z))
    zs = ndi.gaussian_filter(zz, 1.0 / res)
    gy, gx = np.gradient(zs, res)
    slope = np.hypot(gx, gy) * 100.0
    lap = np.abs(ndi.laplace(ndi.gaussian_filter(zz, 1.5 / res))) / (res * res)
    m = (slope < flat_pct) & (lap < 0.02) & np.isfinite(z)

    def band(path, b):
        dst = np.full(shape, np.nan, np.float32)
        with rasterio.open(path) as s:
            reproject(s.read(b).astype(np.float32), dst, src_transform=s.transform, src_crs=s.crs,
                      dst_transform=T, dst_crs=crs, resampling=Resampling.average)
        return dst
    if nir_path and os.path.exists(nir_path):
        nir = band(nir_path, 1)
        with rasterio.open(nir_path) as s:      # 3 m std at native resolution, then averaged onto the DEM grid
            raw = s.read(1).astype(np.float32)
            k = max(1, int(round(3.0 / abs(s.transform.a))))
            mu = ndi.uniform_filter(raw, k)
            sd = np.sqrt(np.maximum(ndi.uniform_filter(raw * raw, k) - mu * mu, 0))
            sdd = np.full(shape, np.nan, np.float32)
            reproject(sd, sdd, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=crs,
                      resampling=Resampling.average)
        ok = np.isfinite(sdd)
        thr = np.nanpercentile(sdd[ok], 40) if ok.any() else np.inf
        mown = ok & (sdd <= thr)
        if rgb_path and os.path.exists(rgb_path):
            red = band(rgb_path, 1)
            ndvi = (nir - red) / np.maximum(nir + red, 1.0)
            mown &= np.nan_to_num(ndvi, nan=0.0) > 0.15
        m &= mown
    m = ndi.binary_opening(m, iterations=1)
    lab, _ = ndi.label(m)
    inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    gc = [pt.centroid_ll(g["coords"]) for g in greens if len(g["coords"]) >= 3]
    pads = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        if sl is None:
            continue
        r0, c0 = max(sl[0].start - 5, 0), max(sl[1].start - 5, 0)
        r1, c1 = sl[0].stop + 5, sl[1].stop + 5
        sub = lab[r0:r1, c0:c1] == i
        area = float(sub.sum()) * res * res
        if not area_m2[0] <= area <= area_m2[1]:
            continue
        ring = ndi.binary_dilation(sub, iterations=4) & ~ndi.binary_dilation(sub, iterations=1)
        bank = float((slope[r0:r1, c0:c1][ring] > bank_pct).mean()) if ring.any() else 0.0
        if bank < bank_frac:
            continue
        rr, cc = np.nonzero(sub)
        cx, ry = cc + c0 + 0.5, rr + r0 + 0.5
        xs, ys = T.c + T.a * cx + T.b * ry, T.f + T.d * cx + T.e * ry
        hull = lp._hull(np.c_[xs, ys])
        lon, lat = inv.transform([p[0] for p in hull], [p[1] for p in hull])
        cl = inv.transform(float(np.mean(xs)), float(np.mean(ys)))
        c = (cl[1], cl[0])
        if gc and min(pt.haversine_yd(c, g) for g in gc) <= green_clear_yd:
            continue
        pads.append(dict(id=f"texture:{len(pads)}", coords=list(zip(lat, lon)), centroid=c, source="texture",
                         p=SOURCE_P["texture"], area_m2=round(area, 1), bank_frac=round(bank, 3)))
    if lines:
        keep = {id(p) for ts in pt.assign_tees_to_holes(lines, pads).values() for p in ts}
        pads = [p for p in pads if id(p) in keep]
    return pads


# ----------------------------------------------------------------------------- merging
def _ring_xy(fr, coords):
    ring = [fr.fwd(*p) for p in coords]
    if len(ring) > 1 and ring[0] == ring[-1]:
        ring = ring[:-1]
    return ring


def merge_candidates(cands, merge_yd=PARAMS["merge_yd"]):
    """One pad per physical pad: union-find on centroid distance <= merge_yd or footprint overlap
    (a centroid inside the other's ring). p_real = 1 - prod(1 - p); geometry from the best-ranked source."""
    cands = [c for c in cands if c.get("coords")]
    if not cands:
        return []
    lat0 = sum(p[0] for c in cands for p in c["coords"]) / sum(len(c["coords"]) for c in cands)
    lon0 = sum(p[1] for c in cands for p in c["coords"]) / sum(len(c["coords"]) for c in cands)
    fr = pt.Frame(lat0, lon0)
    rings = [_ring_xy(fr, c["coords"]) for c in cands]
    cents = [pt.polygon_centroid(r) for r in rings]
    par = list(range(len(cands)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    C = np.array(cents)
    for i in range(len(cands)):
        d = np.hypot(C[:, 0] - C[i, 0], C[:, 1] - C[i, 1])
        for j in np.nonzero(d <= max(merge_yd, 0) + 30)[0]:
            if j <= i:
                continue
            if cands[i]["source"] == cands[j]["source"] == "osm":
                continue                            # mapped boxes are never merged with each other
            if d[j] <= merge_yd or (len(rings[j]) >= 3 and pt._point_in_ring(cents[i], rings[j])) or \
                    (len(rings[i]) >= 3 and pt._point_in_ring(cents[j], rings[i])):
                par[find(i)] = find(j)
    groups = {}
    for i in range(len(cands)):
        groups.setdefault(find(i), []).append(i)
    out = []
    for g in groups.values():
        g.sort(key=lambda i: (SOURCE_RANK.index(cands[i]["source"]) if cands[i]["source"] in SOURCE_RANK else 9,
                              -cands[i].get("p", 0)))
        best = cands[g[0]]
        q = 1.0
        by_src = {}
        for i in g:
            s = cands[i]["source"]
            by_src[s] = max(by_src.get(s, 0.0), float(cands[i].get("p", 0.5)))
        for v in by_src.values():
            q *= 1.0 - min(v, 0.995)
        out.append(dict(id=best.get("id"), coords=best["coords"], source=best["source"], p=1.0 - q,
                        sources=sorted(by_src), members=[cands[i].get("id") for i in g]))
    return out


# ----------------------------------------------------------------------------- one hole
def _hole_cands(fr, lop, cands, P, borrowed=False):
    out = []
    for t in cands:
        ring = _ring_xy(fr, t["coords"])
        c = pt.polygon_centroid(ring)
        along, off = lop.first_leg_coords(c)
        if abs(off) > P["max_offset_yd"] or along > 0.5 * lop.length or along < -P["max_behind_yd"]:
            continue
        m = pt._tee_metrics(lop, ring, c)
        ext = m["d_back"] - m["d_front"]
        inner = min(P["inner_yd"], ext / 4.0)
        out.append(dict(tee_id=t.get("id"), centroid_xy=c, offset_yd=off, along_yd=along, source=t["source"],
                        sources=t.get("sources") or [t["source"]], p=float(t.get("p", 0.5)), borrowed=borrowed,
                        lo=m["d_front"] + inner, hi=m["d_back"] - inner, ext=ext, **m))
    return out


def _unary(c, t, P):
    p = min(max(t, c["lo"]), c["hi"])
    err = abs(t - p)
    cost = err + P["centre_w"] * abs(c["d_centroid"] - t) + P["prior_yd"] * -math.log(max(c["p"], 1e-3)) \
        + P["off_w"] * max(0.0, abs(c["offset_yd"]) - P["off_free_yd"]) + (P["borrow_cost"] if c["borrowed"] else 0.0)
    return p, t - p, err, cost


def localize_hole(line, green, own, borrow=(), yardages=None, params=None):
    """{set: result} for one hole (module docstring 2-3). own / borrow = merged candidates
    ({id, coords [(lat, lon)], source, p, sources})."""
    P = dict(PARAMS, **(params or {}))
    fr, lop = pt._hole_frame(line, green)
    cands = _hole_cands(fr, lop, own, P) + _hole_cands(fr, lop, borrow, P, borrowed=True)
    names = sorted((n for n, y in (yardages or {}).items() if y), key=lambda n: -float(yardages[n]))
    if not names:
        return {}
    biases = np.arange(-P["bias_max"], P["bias_max"] + 1e-9, P["bias_step"])
    WB = -1

    def options(y, b):
        t = y + b
        opts = []
        for i, c in enumerate(cands):
            p, e, err, cost = _unary(c, t, P)
            if err > (P["borrow_err_yd"] if c["borrowed"] else P["max_err_yd"]):
                continue
            opts.append((i, p, e, err, cost))
        opts.append((WB, y, 0.0, None, P["walkback"]))      # walk-back: no bias (no evidence)
        return opts

    def pair(a, o, ya, yb):
        ia, pa, ea = a[0], a[1], a[2]
        ib, pb, eb = o[0], o[1], o[2]
        c = 0.0 if pa + P["order_tol"] >= pb else P["order"]
        if ia != WB and ib != WB:
            c += P["gap_w"] * min(abs(ea - eb), P["gap_cap"])
            if ia == ib and cands[ia]["ext"] < 0.6 * (ya - yb):
                c += P["share"]
        return c

    T = P["temp"]
    per_b = []
    for b in biases:
        prior = 0.5 * T * (b / P["bias_sd"]) ** 2
        opts = [options(float(yardages[n]), b) for n in names]
        ys = [float(yardages[n]) for n in names]
        # min-sum (MAP) and sum-product (marginals) forward passes
        best = [np.array([o[4] for o in opts[0]])]
        arg = [None]
        logf = [-np.array([o[4] for o in opts[0]]) / T]
        for i in range(1, len(names)):
            M = np.array([[pair(a, o, ys[i - 1], ys[i]) for o in opts[i]] for a in opts[i - 1]])
            u = np.array([o[4] for o in opts[i]])
            tot = best[-1][:, None] + M + u[None, :]
            arg.append(np.argmin(tot, axis=0))
            best.append(np.min(tot, axis=0))
            lf = logf[-1][:, None] - (M + u[None, :]) / T
            mx = lf.max(axis=0)
            logf.append(mx + np.log(np.exp(lf - mx).sum(axis=0)))
        # backward (sum-product)
        logb = [None] * len(names)
        logb[-1] = np.zeros(len(opts[-1]))
        for i in range(len(names) - 2, -1, -1):
            M = np.array([[pair(a, o, ys[i], ys[i + 1]) for o in opts[i + 1]] for a in opts[i]])
            u = np.array([o[4] for o in opts[i + 1]])
            lb = -(M + u[None, :]) / T + logb[i + 1][None, :]
            mx = lb.max(axis=1)
            logb[i] = mx + np.log(np.exp(lb - mx[:, None]).sum(axis=1))
        lz = logf[-1].max() + math.log(np.exp(logf[-1] - logf[-1].max()).sum()) - prior / T
        j = int(np.argmin(best[-1]))
        path = [j]
        for i in range(len(names) - 1, 0, -1):
            j = int(arg[i][j])
            path.append(j)
        path = path[::-1]
        per_b.append(dict(b=float(b), opts=opts, map_cost=float(best[-1].min()) + prior, path=path, lz=lz,
                          marg=[logf[i] + logb[i] for i in range(len(names))]))
    top = min(per_b, key=lambda r: r["map_cost"])
    lzs = np.array([r["lz"] for r in per_b])
    wb = np.exp(lzs - lzs.max())
    wb /= wb.sum()

    out = {}
    for si, n in enumerate(names):
        y = float(yardages[n])
        o = top["opts"][si][top["path"][si]]
        q_xy = _point(fr, lop, cands, o, y)
        # marginal over (bias, option) -> positions
        pos, w, ids = [], [], []
        for r, wr in zip(per_b, wb):
            lm = r["marg"][si]
            pm = np.exp(lm - lm.max())
            pm /= pm.sum()
            for oo, pp in zip(r["opts"][si], pm):
                if wr * pp < 1e-4:
                    continue
                pos.append(_point(fr, lop, cands, oo, y))
                w.append(wr * pp)
                ids.append(oo[0])
        w = np.array(w) / max(sum(w), 1e-12)
        pos = np.array(pos)
        d = pos - np.array(q_xy)
        u0 = np.array(lop.u0)
        nrm = np.array([u0[1], -u0[0]])
        var_al = float(np.sum(w * (d @ u0) ** 2))
        var_la = float(np.sum(w * (d @ nrm) ** 2))
        if o[0] == WB:
            src = "walkback"
            within = 0.0
        else:
            c = cands[o[0]]
            src = c["source"]
            within = min(c["ext"] / 4.0, 5.0)
        s0 = SOURCE_SD.get(src, 5.0)
        var_al += within ** 2 + s0 ** 2 / 2
        var_la += s0 ** 2 / 2
        p_assign = float(sum(wi for wi, ii in zip(w, ids) if ii == o[0]))
        alt = {}
        for wi, ii in zip(w, ids):
            key = "walkback" if ii == WB else str(cands[ii]["tee_id"])
            alt[key] = alt.get(key, 0.0) + float(wi)
        lat, lon = fr.inv(*q_xy)
        if o[0] == WB:
            near = min((abs(y - min(max(y, c["d_front"]), c["d_back"])) for c in cands), default=None)
            r = dict(lat=lat, lon=lon, method="walkback", tee_id=None, confidence="low",
                     error_yd=None if near is None else round(near, 1), dist_yd=round(lop.dist_to_green(q_xy), 1),
                     d_centroid=None, d_front=None, d_back=None, line_length_yd=round(lop.length, 1), source="hole_line")
        else:
            c = cands[o[0]]
            if src == "osm":
                method = "tee_centroid" if abs(c["d_centroid"] - (y + top["b"])) <= 3.0 else "tee_axis"
            else:
                method = "lidar_pad" if src == "lidar" else f"{src}_pad"
            conf = "high" if (o[3] or 0) <= 5 and p_assign >= 0.6 and src == "osm" else \
                "medium" if (o[3] or 0) <= 15 and p_assign >= 0.3 else "low"
            r = dict(lat=lat, lon=lon, method=method, tee_id=c["tee_id"], confidence=conf, error_yd=round(o[3], 1),
                     dist_yd=round(lop.dist_to_green(q_xy), 1), d_centroid=round(c["d_centroid"], 1),
                     d_front=round(c["d_front"], 1), d_back=round(c["d_back"], 1), source=src,
                     sources=c["sources"], p_real=round(c["p"], 3))
            if c["borrowed"]:
                r["borrowed"] = True
        r.update(sigma_along_yd=round(math.sqrt(var_al), 1), sigma_lat_yd=round(math.sqrt(var_la), 1),
                 sigma_yd=round(math.sqrt(var_al + var_la), 1), p_assign=round(p_assign, 3),
                 bias_yd=round(top["b"], 1), bias_mean_yd=round(float(np.sum(wb * np.array([q["b"] for q in per_b]))), 1),
                 alternatives=[dict(tee_id=k, p=round(v, 3)) for k, v in sorted(alt.items(), key=lambda kv: -kv[1])[:3]],
                 localizer=VERSION)
        out[n] = r
    tol = P["order_tol"]
    if P["snap_yd"] > 0:
        for i, n in enumerate(names):
            r = out[n]
            o = top["opts"][i][top["path"][i]]
            if o[0] == WB or sum(1 for m in out.values() if m["tee_id"] == r["tee_id"]) > 1:
                continue
            c = cands[o[0]]
            if abs(c["d_centroid"] - float(yardages[n])) <= P["snap_yd"]:
                r["lat"], r["lon"] = fr.inv(*c["centroid_xy"])
                r["dist_yd"] = round(lop.dist_to_green(c["centroid_xy"]), 1)
                if r["source"] == "osm":
                    r["method"] = "tee_centroid"
    for i, n in enumerate(names):
        r = out[n]
        r["order_ok"] = all(out[m]["dist_yd"] + tol >= r["dist_yd"] for m in names[:i]) and \
            all(r["dist_yd"] + tol >= out[m]["dist_yd"] for m in names[i + 1:])
        r["shared_with"] = sorted(m for m, o in out.items() if m != n and r["tee_id"] is not None and o["tee_id"] == r["tee_id"])
    return out


def _point(fr, lop, cands, o, y):
    i, p = o[0], o[1]
    if i == -1:
        return lop.point_at_distance(y)
    c = cands[i]
    return pt._point_on_axis(lop, c["centroid_xy"], p, c["d_front"], c["d_back"])


# ----------------------------------------------------------------------------- course
def localize_course(lines, greens, yardages, cands, params=None, borrow=True):
    """lines {ref: [(lat, lon)]}, greens OSM rings, yardages {ref: {set: yards}}, cands = merged candidates
    (merge_candidates) -> {ref: {green, tees: {set: {...}}}} (place_tee.place_course_sets shape)."""
    by_hole = pt.assign_tees_to_holes(lines, cands, max_offset_yd=45.0)
    out = {}
    for ref, line in lines.items():
        yds = {n: y for n, y in (yardages.get(ref) or {}).items() if y}
        if not yds:
            continue
        g = pt.green_for_line(line, list(greens)) if greens else None
        own = by_hole.get(ref, [])
        mine = {id(t) for t in own}
        others = [t for t in cands if id(t) not in mine] if borrow else []
        res = localize_hole(line, g, own, others, yds, params)
        out[ref] = dict(green=dict(lat=g[0], lon=g[1]) if g else None,
                        sets_without_box=[n for n, r in res.items() if r["method"] == "walkback"], tees=res)
    return out


def gather(osm_tees=(), segment=None, scene=None, pads=(), texture=(), use=("osm", "segment", "scene", "lidar", "texture")):
    """All candidate sources -> merged pads. segment / scene: path or loaded dict (or None)."""
    c = []
    if "osm" in use:
        c += osm_candidates(osm_tees)
    if "segment" in use and segment:
        c += segment_candidates(segment)
    if "scene" in use and scene:
        c += scene_candidates(scene)
    if "lidar" in use:
        c += lidar_candidates(pads)
    if "texture" in use:
        c += [dict(t, p=t.get("p", SOURCE_P["texture"])) for t in texture]
    return merge_candidates(c)


def positions(lines, greens, yardages, cands, params=None):
    """platform/package.py entry point: tee_positions-shaped dict."""
    return dict(schema="tees/positions", method=VERSION + " (joint chain + bias, merged OSM / segment / scene / "
                "lidar / texture pads)", holes=localize_course(lines, greens, yardages, cands, params))
