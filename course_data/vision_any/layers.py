"""Any-course hazard layers: trees (lidar canopy), long grass / native (NAIP classifier), water and creek
corridors, OB-ish structures, on one UTM grid per course.

Inputs (all free, fetched on Actions by fetch_any.py into course_data/vision_any/<slug>/raw/):
  hag.tif          USGS 3DEP lidar height above ground (Planetary Computer '3dep-lidar-hag')
  lidar_class.tif  3DEP point classification (6 = building, 9 = water, 3-5 = vegetation)
  dtm.tif          3DEP bare earth (creek channels, ravines)
  chm_meta.tif     Meta 1 m global canopy height (fallback where there is no lidar)
  naip_<year>.tif  NAIP R,G,B,NIR at 0.6 m (latest 2 years)
plus the course's osm.geojson (fairway / green / tee / bunker / water / rough / streams / buildings).
If raw/ has no NAIP, the imagery team's course_data/imagery/<slug>/naip_{rgb,nir}.tif is used.

    S = Stack.load("spirit_hollow", "course_data/spirit_hollow")
    trees, how = tree_mask(S)               # bool, 1 m grid
    native_p = NativeModel.default().predict(S, fc)   # P(native) on the 1 m grid
    water = water_mask(S, fc)
"""
import glob
import json
import math
import os
import sys

import cv2
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
YD = 0.9144
RES = 1.0                          # analysis grid, metres
TREE_HAG_M = 2.5                   # canopy threshold (industry standard 2-3 m)


def log(*a):
    print(*a, flush=True)


# =========================================================================== stack
class Stack:
    """Every layer resampled to one 1 m UTM grid (north-up)."""

    def __init__(self):
        self.layers = {}
        self.naip = []                 # [(year, float32 (H, W, 4) 0..1)]
        self.src = {}

    @classmethod
    def load(cls, slug, course_dir=None, res=RES, cache=None):
        """cache: a directory for an .npz of the resampled stack (or $VISION_ANY_CACHE)."""
        import pickle
        cache = cache or os.environ.get("VISION_ANY_CACHE")
        cp = None
        if cache:
            raw = os.path.join(HERE, slug, "raw")
            stamp = max([os.path.getmtime(p) for p in glob.glob(os.path.join(raw, "*"))] or [0])
            cp = os.path.join(cache, f"stack_{slug}_{res:g}_{int(stamp)}.pkl")
            if os.path.exists(cp):
                with open(cp, "rb") as fh:
                    S = pickle.load(fh)
                log(f"[stack] {slug}: cached {cp}")
                return S
        S = cls._load(slug, course_dir, res)
        if cp:
            os.makedirs(cache, exist_ok=True)
            for a in ("_fwd", "_inv"):
                S.__dict__.pop(a, None)
            with open(cp, "wb") as fh:
                pickle.dump(S, fh, protocol=4)
        return S

    @classmethod
    def _load(cls, slug, course_dir=None, res=RES):
        import rasterio
        from affine import Affine
        S = cls()
        S.slug = slug
        S.dir = os.path.join(HERE, slug)
        raw = os.path.join(S.dir, "raw")
        S.course_dir = course_dir or os.path.join(ROOT, "course_data", slug)
        mp = os.path.join(raw, "meta.json")
        S.meta = json.load(open(mp)) if os.path.exists(mp) else {}
        if S.meta.get("grid"):
            g = S.meta["grid"]
            x0, y0, x1, y1 = g["bounds"]
            S.crs = g["crs"]
        else:                                                   # no fetch yet: same grid rule as fetch_any
            sys.path.insert(0, HERE)
            import fetch_any as FA
            gg = FA.Grid(FA.bbox_from_course_dir(S.course_dir)[0], 120.0, 1.0)
            x0, y0, x1, y1, S.crs = gg.x0, gg.y0, gg.x1, gg.y1, gg.crs
        S.res = res
        S.W, S.H = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
        S.transform = Affine(res, 0, x0, 0, -res, y1)
        S.bounds = (x0, y0, x1, y1)

        def rd(path, band=1, resampling="bilinear", scale=1.0, nodata_vals=()):
            from rasterio.warp import reproject, Resampling
            out = np.full((S.H, S.W), np.nan, np.float32)
            with rasterio.open(path) as src:
                a = src.read(band).astype(np.float32)
                for v in nodata_vals:
                    a[a == v] = np.nan
                if src.nodata is not None and np.isfinite(src.nodata):
                    a[a == src.nodata] = np.nan
                reproject(a, out, src_transform=src.transform, src_crs=src.crs, dst_transform=S.transform,
                          dst_crs=S.crs, resampling=getattr(Resampling, resampling), src_nodata=np.nan,
                          dst_nodata=np.nan)
            return out * scale

        p = os.path.join(raw, "hag.tif")
        if os.path.exists(p):
            a = rd(p, scale=0.25, nodata_vals=(255,))
            if np.isfinite(a).mean() > 0.5:
                S.layers["hag"] = a
                lid = S.meta.get("lidar", {}).get("hag", {}).get("items") or []
                ept = S.meta.get("ept", {}).get("used") or []
                S.src["hag"] = ("3DEP lidar HAG, Planetary Computer: " + ", ".join(sorted({i["id"].split("-hag")[0] for i in lid}))
                                if lid else "3DEP lidar point cloud (EPT/PDAL): " + ", ".join(c["name"] for c in ept))
        p = os.path.join(raw, "chm_meta.tif")
        if os.path.exists(p):
            S.layers["chm_meta"] = rd(p, nodata_vals=(255,))
            S.src["chm_meta"] = "Meta/WRI 1 m canopy height"
        p = os.path.join(raw, "lidar_class.tif")
        if os.path.exists(p) and "hag" in S.layers:
            S.layers["lclass"] = rd(p, resampling="nearest", nodata_vals=(0,))
            S.src["lclass"] = "3DEP lidar classification"
        for p in (os.path.join(raw, "dtm.tif"), os.path.join(ROOT, "course_data", "imagery", slug, "dem.tif")):
            if os.path.exists(p) and np.isfinite(rd(p)).mean() > 0.5:
                S.layers["dtm"] = rd(p)
                S.src["dtm"] = os.path.relpath(p, ROOT)
                break
        for p in sorted(glob.glob(os.path.join(raw, "naip_*.tif")), reverse=True):
            yr = int(os.path.basename(p)[5:9])
            bands = np.stack([rd(p, b, "average") for b in (1, 2, 3, 4)], -1) / 255.0
            S.naip.append((yr, bands))
            S.src[f"naip_{yr}"] = os.path.relpath(p, ROOT)
        if not S.naip:
            idir = os.path.join(ROOT, "course_data", "imagery", slug)
            if os.path.exists(os.path.join(idir, "naip_rgb.tif")) and os.path.exists(os.path.join(idir, "naip_nir.tif")):
                gj = json.load(open(os.path.join(idir, "georef.json")))
                yr = int(gj["imagery"]["year"])
                rgb = [rd(os.path.join(idir, "naip_rgb.tif"), b, "average", nodata_vals=(0,)) for b in (1, 2, 3)]
                nir = rd(os.path.join(idir, "naip_nir.tif"), 1, "average", nodata_vals=(0,))
                S.naip.append((yr, np.stack(rgb + [nir], -1) / 255.0))
                S.src[f"naip_{yr}"] = os.path.relpath(idir, ROOT) + " (imagery team)"
        log(f"[stack] {slug}: {S.W}x{S.H} @ {res} m, layers {list(S.layers)}, naip {[y for y, _ in S.naip]}")
        return S

    # ---- coordinates
    def ll_to_rc(self, ll):
        """[lon, lat] -> fractional (col, row) on the grid (pixel-corner convention)."""
        from pyproj import Transformer
        if not hasattr(self, "_fwd"):
            self._fwd = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
            self._inv = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)
        ll = np.atleast_2d(np.asarray(ll, float))
        x, y = self._fwd.transform(ll[:, 0], ll[:, 1])
        c, r = ~self.transform * (np.asarray(x), np.asarray(y))
        return np.c_[c, r]

    def xy_to_ll(self, xy):
        self.ll_to_rc([[0, 0]])
        lon, lat = self._inv.transform(xy[:, 0], xy[:, 1])
        return np.c_[lon, lat]

    def sample(self, arr, ll):
        """Nearest-cell values of a grid array at [lon, lat] points (False/NaN outside)."""
        rc = self.ll_to_rc(ll)
        c, r = np.floor(rc[:, 0]).astype(int), np.floor(rc[:, 1]).astype(int)
        ok = (c >= 0) & (c < self.W) & (r >= 0) & (r < self.H)
        out = np.zeros(len(rc), arr.dtype) if arr.dtype == bool else np.full(len(rc), np.nan, np.float32)
        out[ok] = arr[r[ok], c[ok]]
        return out

    def rasterize(self, geoms, value=1):
        """Shapely geometries (WGS84) -> bool mask on the grid."""
        m = np.zeros((self.H, self.W), np.uint8)
        polys, lines = [], []
        for g in geoms:
            for p in getattr(g, "geoms", [g]):
                if p.geom_type == "Polygon":
                    polys.append(p)
                elif p.geom_type == "LineString":
                    lines.append(p)
        for p in polys:
            ext = np.round(self.ll_to_rc(np.asarray(p.exterior.coords)) * 8).astype(np.int32)
            cv2.fillPoly(m, [ext], 1, shift=3)
            for ring in p.interiors:
                cv2.fillPoly(m, [np.round(self.ll_to_rc(np.asarray(ring.coords)) * 8).astype(np.int32)], 0, shift=3)
        for ln in lines:
            pts = np.round(self.ll_to_rc(np.asarray(ln.coords)) * 8).astype(np.int32)
            cv2.polylines(m, [pts], False, 1, 1, shift=3)
        return m > 0


# =========================================================================== OSM
PENAL_OSM = {"water"}


def osm_layers(fc):
    """{class: [shapely geoms]} from an osm.geojson FeatureCollection."""
    from shapely.geometry import shape
    out = {k: [] for k in ("fairway", "green", "tee", "bunker", "water", "rough", "stream", "river", "building",
                           "residential", "road", "course", "woods", "native", "trees_pt")}
    for f in fc["features"]:
        p, g = f["properties"], f.get("geometry")
        if not g:
            continue
        try:
            s = shape(g)
        except Exception:                                    # noqa: BLE001
            continue
        poly = s.geom_type in ("Polygon", "MultiPolygon")
        golf, nat, lu = p.get("golf"), p.get("natural"), p.get("landuse")
        if golf in ("fairway", "green", "tee", "rough") and poly:
            out[golf].append(s)
        elif golf == "bunker" or (nat == "sand" and poly):
            out["bunker"].append(s)
        elif poly and (golf in ("water_hazard", "lateral_water_hazard") or nat == "water"
                       or lu in ("reservoir", "basin") or p.get("water")):
            out["water"].append(s)
        elif p.get("waterway") in ("stream", "ditch", "drain", "canal") and not poly:
            out["stream"].append(s)
        elif p.get("waterway") == "river" and not poly:
            out["river"].append(s)
        elif p.get("building") and poly:
            out["building"].append(s)
        elif lu in ("residential", "commercial", "industrial", "retail") and poly:
            out["residential"].append(s)
        elif p.get("highway") in ("motorway", "trunk", "primary", "secondary", "tertiary", "residential",
                                  "unclassified") and not poly:
            out["road"].append(s)
        elif p.get("leisure") == "golf_course" and poly:
            out["course"].append(s)
        elif poly and (nat in ("wood", "tree_row") or lu == "forest"):
            out["woods"].append(s)
        elif poly and (nat in ("grassland", "scrub", "heath", "wetland") or lu == "meadow"
                       or golf in ("native", "natural_area")):
            out["native"].append(s)
        elif nat == "tree" and s.geom_type == "Point":
            out["trees_pt"].append(s)
    return out


def osm_masks(S, fc):
    L = osm_layers(fc)
    M = {k: S.rasterize(v) if v and k not in ("trees_pt",) else np.zeros((S.H, S.W), bool) for k, v in L.items()}
    M["mown"] = M["fairway"] | M["green"] | M["tee"]
    return M, L


# =========================================================================== trees
def disk(r):
    r = int(round(r))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


def tree_mask(S, osm=None, hag_min=TREE_HAG_M, min_area_m2=30.0):
    """Canopy mask: lidar HAG > hag_min, minus buildings, cleaned. Returns (mask, how, height)."""
    how = []
    h = S.layers.get("hag")
    if h is not None and np.isfinite(h).mean() > 0.6:
        hh = h.copy()
        how.append("3DEP lidar HAG > %.1f m" % hag_min)
        if "chm_meta" in S.layers:                             # fill lidar gaps with the Meta CHM
            gap = ~np.isfinite(hh)
            hh[gap] = S.layers["chm_meta"][gap]
            if gap.mean() > 0.001:
                how.append(f"Meta CHM in {gap.mean():.1%} lidar gaps")
    elif "chm_meta" in S.layers:
        hh = S.layers["chm_meta"].copy()
        how.append("Meta 1 m canopy height > %.1f m (no lidar)" % hag_min)
    else:
        hh = None
    if hh is not None:
        hh = np.nan_to_num(hh, nan=0.0)
        # median 3x3 kills single-cell spikes (poles, wires, noise) before thresholding
        hm = ndimage.median_filter(hh, 3)
        m = hm > hag_min
        bld = np.zeros_like(m)
        if "lclass" in S.layers:
            bld |= S.layers["lclass"] == 6
        if osm is not None:
            bld |= osm.get("building", np.zeros_like(m))
        if S.naip:                                             # tall but not green = a structure
            nd = ndvi(S.naip[0][1])
            bld |= (hm > hag_min) & (ndimage.uniform_filter(nd, 5) < 0.05)
        bld = ndimage.binary_dilation(bld, disk(2))
        m &= ~bld
        height = hm
    else:
        m, height = ndvi_tree_fallback(S), None
        how.append("NAIP NDVI + texture fallback (no canopy height)")
    m = ndimage.binary_opening(m, disk(1))
    m = ndimage.binary_closing(m, disk(2))
    m = fill_small_holes(m, 60)
    m = remove_small(m, min_area_m2 / S.res ** 2)
    return m, "; ".join(how), height


def ndvi(b):
    return (b[..., 3] - b[..., 0]) / (b[..., 3] + b[..., 0] + 1e-3)


def ndvi_tree_fallback(S):
    """Dark, high-NDVI, rough-textured vegetation (no height data)."""
    b = S.naip[0][1]
    nd = ndvi(b)
    br = b[..., :3].mean(-1)
    w = 5
    m1 = ndimage.uniform_filter(b[..., 3], w)
    tex = np.sqrt(np.maximum(ndimage.uniform_filter(b[..., 3] ** 2, w) - m1 ** 2, 0))
    ref = br[nd > np.percentile(nd, 50)]
    return (nd > 0.3) & (br < np.percentile(ref, 35)) & (tex > np.percentile(tex, 60))


def fill_small_holes(m, max_px):
    lab, n = ndimage.label(~m)
    if n == 0:
        return m
    sz = ndimage.sum(np.ones_like(m), lab, range(1, n + 1))
    small = np.zeros(n + 1, bool)
    small[1:] = sz <= max_px
    return m | small[lab]


def remove_small(m, min_px):
    lab, n = ndimage.label(m)
    if n == 0:
        return m
    sz = ndimage.sum(np.ones_like(m), lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sz >= min_px
    return keep[lab]


# =========================================================================== native features
def _std(x, w):
    m1 = ndimage.uniform_filter(x, w)
    return np.sqrt(np.maximum(ndimage.uniform_filter(x * x, w) - m1 * m1, 0))


def features(S, osm_m, trees):
    """(H, W, F) float32 + names. Spectral features are normalised per course and per NAIP year against the
    course's own OSM-mapped mown turf (median / IQR inside fairways + greens + tees), so a model trained on
    one course and season transfers to another. Height features (lidar) are absolute metres."""
    F, names = [], []
    ref = ndimage.binary_erosion(osm_m["mown"], disk(2))
    if ref.sum() < 500:
        ref = osm_m["mown"]
    far_tree = ~ndimage.binary_dilation(trees, disk(3))
    for yi, (yr, b) in enumerate(S.naip[:2]):
        r, g, bl, n = (b[..., i] for i in range(4))
        br = (r + g + bl) / 3
        nd = (n - r) / (n + r + 1e-3)
        ndwi = (g - n) / (g + n + 1e-3)
        exg = (2 * g - r - bl) / (r + g + bl + 1e-3)
        chroma = (r - bl) / (r + bl + 1e-3)                 # tan / straw vs green
        base = dict(r=r, g=g, b=bl, nir=n, br=br, ndvi=nd, ndwi=ndwi, exg=exg, chroma=chroma)
        tag = f"y{yi}"
        for nm, x in base.items():
            x = np.nan_to_num(x)
            for s in (1.0, 3.0):
                v = ndimage.gaussian_filter(x, s)
                F.append(v)
                names.append(f"{tag}_{nm}_s{s:g}")
            F.append(ndimage.gaussian_filter(x, 8.0))
            names.append(f"{tag}_{nm}_s8")
        for nm, x in (("nir", n), ("br", br), ("ndvi", nd)):
            x = np.nan_to_num(x)
            for w in (3, 7, 15):
                F.append(_std(x, w))
                names.append(f"{tag}_std_{nm}_{w}")
        gm = np.hypot(ndimage.sobel(np.nan_to_num(br), 0), ndimage.sobel(np.nan_to_num(br), 1))
        F.append(ndimage.uniform_filter(gm, 5))
        names.append(f"{tag}_grad_br")
    # normalise spectral/texture features against mown turf
    for i in range(len(F)):
        v = F[i][ref & far_tree]
        if v.size < 100:
            v = F[i][ref]
        if v.size < 100:
            v = F[i].ravel()
        med = np.nanmedian(v)
        iqr = np.nanpercentile(v, 75) - np.nanpercentile(v, 25)
        F[i] = (F[i] - med) / (iqr + 1e-4)
    if len(S.naip) >= 2:                                     # year-to-year change (mown turf is stable)
        a0 = names.index("y0_ndvi_s3")
        a1 = names.index("y1_ndvi_s3")
        F.append(F[a0] - F[a1])
        names.append("dndvi")
        a0, a1 = names.index("y0_chroma_s3"), names.index("y1_chroma_s3")
        F.append(F[a0] - F[a1])
        names.append("dchroma")
    h = S.layers.get("hag")
    if h is not None and np.isfinite(h).mean() > 0.6:
        hh = np.clip(np.nan_to_num(h), 0, TREE_HAG_M)       # low-vegetation height only
        for s in (1.0, 3.0):
            F.append(ndimage.gaussian_filter(hh, s))
            names.append(f"hag_low_s{s:g}")
        F.append(_std(hh, 5))
        names.append("hag_low_std5")
    else:
        for nm in ("hag_low_s1", "hag_low_s3", "hag_low_std5"):
            F.append(np.full((S.H, S.W), np.nan, np.float32))
            names.append(nm)
    # distance to the nearest tree canopy and to mapped mown turf (context, in metres)
    F.append(np.minimum(ndimage.distance_transform_edt(~trees) * S.res, 60))
    names.append("d_trees")
    F.append(np.minimum(ndimage.distance_transform_edt(~osm_m["mown"]) * S.res, 80))
    names.append("d_mown")
    d = S.layers.get("dtm")
    if d is not None and np.isfinite(d).mean() > 0.8:
        dd = np.where(np.isfinite(d), d, np.nanmedian(d))
        ds = ndimage.gaussian_filter(dd, 1.5)
        gy, gx = np.gradient(ds, S.res)
        F.append(np.degrees(np.arctan(np.hypot(gx, gy))))
        names.append("slope")
        F.append(ds - ndimage.gaussian_filter(dd, 25))
        names.append("relz25")
    else:
        for nm in ("slope", "relz25"):
            F.append(np.full((S.H, S.W), np.nan, np.float32))
            names.append(nm)
    return np.stack(F, -1).astype(np.float32), names


# =========================================================================== water
def water_mask(S, fc_or_layers, osm_m, mown_p=None, trees=None):
    """OSM water polygons + NAIP open water (NDWI) next to them or to a stream + creek corridors: the
    channel of each OSM stream from the DTM (cells within 1.5 m of the local bed elevation, <= 12 m from the
    line) and its unmown banks. Returns (mask, parts)."""
    from shapely.geometry import shape
    L = fc_or_layers if isinstance(fc_or_layers, dict) else osm_layers(fc_or_layers)
    parts = {}
    w = osm_m["water"].copy()
    parts["osm"] = w.copy()
    if S.naip:
        b = S.naip[0][1]
        nd = ndimage.gaussian_filter(np.nan_to_num((b[..., 1] - b[..., 3]) / (b[..., 1] + b[..., 3] + 1e-3)), 1)
        open_w = (nd > 0.05) & (ndvi(b) < 0.05)
        # roofs, decks and shadows are also low-NIR: drop anything with height or a mapped building
        struct = osm_m["building"] | osm_m["residential"] & ~osm_m["water"]
        h = S.layers.get("hag")
        if h is not None:
            struct |= np.nan_to_num(h) > 1.0
        if "lclass" in S.layers:
            struct |= S.layers["lclass"] == 6
        open_w &= ~ndimage.binary_dilation(struct, disk(2))
        if "lclass" in S.layers:
            open_w |= S.layers["lclass"] == 9
        open_w = ndimage.binary_opening(open_w, disk(1))
        open_w = remove_small(open_w, 40)
        lines = S.rasterize(L["stream"] + L["river"]) if (L["stream"] or L["river"]) else np.zeros_like(w)
        near = ndimage.binary_dilation(w | lines, disk(6))
        lab, n = ndimage.label(open_w)
        hit = np.unique(lab[near & open_w])
        keep = np.isin(lab, hit[hit > 0])
        parts["ndwi"] = keep & ~w
        w |= keep
    if L["stream"] or L["river"]:
        lines = S.rasterize(L["stream"])
        river = S.rasterize(L["river"]) if L["river"] else np.zeros_like(lines)
        corr = ndimage.binary_dilation(lines, disk(2)) | ndimage.binary_dilation(river, disk(6))
        d = S.layers.get("dtm")
        if d is not None and np.isfinite(d).mean() > 0.8:
            dd = np.where(np.isfinite(d), d, np.nanmedian(d))
            bed = np.where(lines | river, dd, np.inf)
            # bed elevation of the nearest line cell, propagated outwards
            _, (iy, ix) = ndimage.distance_transform_edt(~(lines | river), return_indices=True)
            bed_near = dd[iy, ix]
            dist = ndimage.distance_transform_edt(~(lines | river)) * S.res
            chan = (dist <= 12) & (dd - bed_near <= 1.5)
            chan = ndimage.binary_opening(chan, disk(1))
            lab, n = ndimage.label(chan)
            hit = np.unique(lab[lines | river])
            chan = np.isin(lab, hit[hit > 0])
            corr |= chan
            parts["channel"] = chan
            del bed
        if mown_p is not None:                               # banks: unmown cells touching the channel
            unm = (mown_p < 0.5) & ~osm_m["mown"]
            dist = ndimage.distance_transform_edt(~corr) * S.res
            bank = unm & (dist <= 6)
            lab, n = ndimage.label(bank | corr)
            hit = np.unique(lab[corr])
            bank = np.isin(lab, hit[hit > 0]) & bank
            parts["banks"] = bank
            corr |= bank
        parts["streams"] = corr
        w |= corr
    w &= ~(osm_m["fairway"] | osm_m["green"] | osm_m["tee"] | osm_m["bunker"])
    return w, parts


# =========================================================================== polygons
def mask_to_polys(S, m, min_yd2=150, simplify_yd=2.0, smooth_px=0):
    """Bool grid mask -> list of shapely Polygons in WGS84 (holes kept)."""
    from shapely.geometry import Polygon
    from shapely.ops import transform as stransform
    mm = m.astype(np.uint8)
    if smooth_px:
        mm = cv2.morphologyEx(mm, cv2.MORPH_CLOSE, disk(smooth_px).astype(np.uint8))
    cnts, hier = cv2.findContours(mm, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    if hier is None:
        return out
    hier = hier[0]
    tr = S.transform
    min_m2 = min_yd2 * YD * YD

    def w(c):
        c = c[:, 0, :].astype(float)
        x, y = tr * (c[:, 0], c[:, 1])
        return np.c_[x, y]
    for i, c in enumerate(cnts):
        if hier[i][3] != -1 or len(c) < 3:
            continue
        holes = []
        j = hier[i][2]
        while j != -1:
            if len(cnts[j]) >= 3 and cv2.contourArea(cnts[j]) * S.res ** 2 >= min_m2:
                holes.append(w(cnts[j]))
            j = hier[j][0]
        p = Polygon(w(c), holes).buffer(0)
        if p.is_empty or p.area < min_m2:
            continue
        p = p.simplify(simplify_yd * YD, preserve_topology=True)
        S.ll_to_rc([[0, 0]])
        g = stransform(lambda x, y: S._inv.transform(x, y), p)
        for q in getattr(g, "geoms", [g]):
            if q.area > 0:
                out.append(q)
    return out
