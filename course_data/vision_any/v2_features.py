"""Per-cell (1 m) features for the v2 long-grass / tree-edge model, any course.

    S = load_stack(slug)                    # layers.Stack + raw2/ (multi-year NAIP 1 m, lidar_v2 point stats)
    F = Features(S, osm_m, canopy)          # F.get(name) -> (H, W) float32; F.names; F.matrix(idx)

Every spectral / texture value is expressed relative to the course's OWN mown turf (OSM fairway + green +
tee, eroded 2 m, away from canopy): (x - median) / IQR per NAIP year, so the model learns "how unlike this
course's mown grass" rather than absolute colours that change with state, season and sensor.

Groups (names):
  latest year  n0_*  : ndvi/nir/brightness/chroma/exg at 1 and 3 m, NIR std 3/7/15, GLCM contrast and
                       homogeneity of NIR (offset 1 m, 7 m window), LBP (P=8, R=1) uniformity + entropy
  multi-year   my_*  : mean / std / min / max over all NAIP years of ndvi, nir, chroma, NIR texture and
                       GLCM contrast; my_persist = share of years whose anomaly (dark NIR, straw, rough,
                       low NDVI vs mown turf) is >= 2 robust units: unmown every year = native; my_nyears
  lidar        li_*  : canopy height (max HAG, 3 m max), HAG mean/std, share of returns 0.05-0.3 / 0.3-1.5
                       / 1.5-4 m, multi-return share, ground share, point density (course-relative),
                       intensity (all, ground; course-relative), smoothed 3x3 and 7x7; low-veg HAG (v1)
  terrain            : slope, relz25 (local relief), from lidar ground (lidar_v2 dtm1) or raw/dtm.tif
  context      d_*   : distance (m, capped) to OSM fairway, green, tee, bunker, water, mown turf; signed
                       distance to the lidar canopy edge (+ outside), canopy area of the clump
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layers as L                                           # noqa: E402

LIDAR_BANDS = ["hag_max", "hag_mean", "hag_std", "n_all", "n_vlow", "n_low", "n_mid", "n_ground", "n_multi",
               "int_mean", "int_ground", "dtm1"]


def load_stack(slug, course_dir=None):
    import rasterio
    from rasterio.warp import reproject, Resampling
    S = L.Stack.load(slug, course_dir)
    raw2 = os.path.join(HERE, slug, "raw2")
    S.naip_v1 = list(S.naip)
    S.lidar2 = {}
    S.meta2 = json.load(open(os.path.join(raw2, "meta2.json"))) if os.path.exists(os.path.join(raw2, "meta2.json")) else {}

    def rd(path, band, resampling="average"):
        out = np.full((S.H, S.W), np.nan, np.float32)
        with rasterio.open(path) as src:
            a = src.read(band).astype(np.float32)
            nd = src.nodata
            if nd is not None and np.isfinite(nd):
                a[a == nd] = np.nan
            reproject(a, out, src_transform=src.transform, src_crs=src.crs, dst_transform=S.transform,
                      dst_crs=S.crs, resampling=getattr(Resampling, resampling), src_nodata=np.nan, dst_nodata=np.nan)
        return out
    years = []
    for p in sorted(glob.glob(os.path.join(raw2, "naip_*.tif")), reverse=True):
        yr = int(os.path.basename(p)[5:9])
        b = np.stack([rd(p, i) for i in (1, 2, 3, 4)], -1) / 255.0
        b[(b.sum(-1) == 0)] = np.nan
        years.append((yr, b.astype(np.float32)))
        S.src[f"naip2_{yr}"] = os.path.relpath(p, L.ROOT)
    have = {y for y, _ in years}
    for y, b in S.naip_v1:                                   # v1's 0.6 m years if raw2 lacks them
        if y not in have:
            years.append((y, b))
    S.naip = sorted(years, key=lambda t: -t[0])
    p = os.path.join(raw2, "lidar_v2.tif")
    if os.path.exists(p):
        for i, nm in enumerate(LIDAR_BANDS, 1):
            S.lidar2[nm] = rd(p, i, "bilinear" if nm in ("dtm1",) else "nearest")
        S.src["lidar_v2"] = "3DEP point cloud (EPT/PDAL) per-1 m return statistics: " + ", ".join(
            u["name"] for u in S.meta2.get("lidar_v2", {}).get("used", []))
    L.log(f"[v2 stack] {slug}: naip years {[y for y, _ in S.naip]}, lidar_v2 {'yes' if S.lidar2 else 'no'}")
    return S


# --------------------------------------------------------------------------- helpers
def robust_norm(x, ref):
    v = x[ref & np.isfinite(x)]
    if v.size < 100:
        v = x[np.isfinite(x)]
    if v.size == 0:
        return x
    med = np.median(v)
    iqr = np.percentile(v, 75) - np.percentile(v, 25)
    return (x - med) / (iqr + 1e-4)


def local_std(x, w):
    m1 = ndimage.uniform_filter(x, w)
    return np.sqrt(np.maximum(ndimage.uniform_filter(x * x, w) - m1 * m1, 0))


def glcm_local(q, w=7):
    """Local GLCM contrast and homogeneity of a quantised image q (float levels), offsets (0,1) and (1,0),
    averaged over a w x w window (exact GLCM statistics of the window's co-occurrence pairs)."""
    dx = np.zeros_like(q)
    dy = np.zeros_like(q)
    dx[:, :-1] = q[:, 1:] - q[:, :-1]
    dy[:-1] = q[1:] - q[:-1]
    con = 0.5 * (ndimage.uniform_filter(dx * dx, w) + ndimage.uniform_filter(dy * dy, w))
    hom = 0.5 * (ndimage.uniform_filter(1 / (1 + dx * dx), w) + ndimage.uniform_filter(1 / (1 + dy * dy), w))
    return con, hom


def lbp_local(x, w=7):
    """LBP (P=8, R=1, rotation-invariant uniform: codes 0..9) -> share of uniform 'flat/edge' codes and the
    local code entropy in a w x w window."""
    from skimage.feature import local_binary_pattern
    v = np.nan_to_num(x)
    lo, hi = np.percentile(v, 1), np.percentile(v, 99)
    u8 = np.clip((v - lo) / (hi - lo + 1e-6) * 255, 0, 255).astype(np.uint8)
    code = local_binary_pattern(u8, 8, 1, method="uniform").astype(np.int8)
    ent = np.zeros(x.shape, np.float32)
    for c in range(10):
        p = ndimage.uniform_filter((code == c).astype(np.float32), w)
        ent -= p * np.log(p + 1e-6)
    nonuni = ndimage.uniform_filter((code == 9).astype(np.float32), w)
    return ent, nonuni


def year_maps(b):
    r, g, bl, n = (np.nan_to_num(b[..., i]) for i in range(4))
    br = (r + g + bl) / 3
    return dict(ndvi=(n - r) / (n + r + 1e-3), nir=n, br=br, chroma=(r - bl) / (r + bl + 1e-3),
                exg=(2 * g - r - bl) / (r + g + bl + 1e-3))


ANOM = (("ndvi", -1), ("nir", -1), ("chroma", +1), ("tex", +1))


class Features:
    def __init__(self, S, osm_m, canopy, canopy_h=None):
        self.S, self.names, self._f = S, [], []
        ref = ndimage.binary_erosion(osm_m["mown"], L.disk(2))
        if ref.sum() < 500:
            ref = osm_m["mown"]
        ref = ref & ~ndimage.binary_dilation(canopy, L.disk(3))
        self.ref = ref
        self._naip(ref)
        self._lidar(ref, canopy, canopy_h)
        self._terrain()
        self._context(osm_m, canopy)

    def add(self, name, x):
        self.names.append(name)
        self._f.append(np.asarray(x, np.float32))

    def get(self, name):
        return self._f[self.names.index(name)]

    def matrix(self, idx, names=None):
        """Rows for flat cell indices idx -> (len(idx), F)."""
        cols = [self.names.index(n) for n in (names or self.names)]
        return np.stack([self._f[c].ravel()[idx] for c in cols], 1)

    # ---------------------------------------------------------------- NAIP
    def _naip(self, ref):
        S = self.S
        per = {k: [] for k in ("ndvi", "nir", "chroma", "tex", "con")}
        anoms = []
        for yi, (yr, b) in enumerate(S.naip):
            m = year_maps(b)
            valid = np.isfinite(b).all(-1)
            s3 = {k: robust_norm(ndimage.gaussian_filter(v, 1.5), ref) for k, v in m.items()}
            tex = robust_norm(local_std(m["nir"], 7), ref)
            nq = robust_norm(ndimage.gaussian_filter(m["nir"], 0.5), ref)
            con, hom = glcm_local(np.round(np.clip(nq, -8, 8) * 2), 7)
            con = robust_norm(con, ref)
            for k in per:
                v = dict(tex=tex, con=con).get(k, s3.get(k))
                per[k].append(np.where(valid, v, np.nan))
            an = np.mean([s * np.where(valid, dict(tex=tex).get(k, s3.get(k)), np.nan) for k, s in ANOM], 0)
            anoms.append(an)
            if yi == 0:                                        # full set for the latest year
                for k, v in m.items():
                    self.add(f"n0_{k}_s1", robust_norm(ndimage.gaussian_filter(v, 0.7), ref))
                    self.add(f"n0_{k}_s3", s3[k])
                for w in (3, 7, 15):
                    self.add(f"n0_std_nir_{w}", robust_norm(local_std(m["nir"], w), ref))
                self.add("n0_std_ndvi_7", robust_norm(local_std(m["ndvi"], 7), ref))
                self.add("n0_glcm_con", con)
                self.add("n0_glcm_hom", robust_norm(hom, ref))
                ent, nonuni = lbp_local(m["nir"], 7)
                self.add("n0_lbp_ent", robust_norm(ent, ref))
                self.add("n0_lbp_nonuni", robust_norm(nonuni, ref))
                self.add("n0_anom", an)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            for k, v in per.items():
                a = np.stack(v)
                self.add(f"my_{k}_mean", np.nanmean(a, 0))
                self.add(f"my_{k}_min", np.nanmin(a, 0))
                self.add(f"my_{k}_max", np.nanmax(a, 0))
                self.add(f"my_{k}_std", np.nanstd(a, 0) if len(v) > 1 else np.full(a.shape[1:], np.nan, np.float32))
            A = np.stack(anoms)
            self.add("my_anom_mean", np.nanmean(A, 0))
            self.add("my_anom_min", np.nanmin(A, 0))
            self.add("my_persist", np.nanmean(A >= 2.0, 0))
            self.add("my_persist_sm", ndimage.uniform_filter(np.nan_to_num(np.nanmean(A >= 2.0, 0)), 5))
        self.add("my_nyears", np.full(A.shape[1:], len(anoms), np.float32))

    # ---------------------------------------------------------------- lidar
    def _lidar(self, ref, canopy, canopy_h):
        S = self.S
        h = S.layers.get("hag")
        if h is not None and np.isfinite(h).mean() > 0.6:
            hh = np.nan_to_num(h)
            self.add("li_hag", hh)
            self.add("li_hag_max3", ndimage.maximum_filter(hh, 3))
            low = np.clip(hh, 0, L.TREE_HAG_M)
            self.add("li_hag_low_s1", ndimage.gaussian_filter(low, 1.0))
            self.add("li_hag_low_s3", ndimage.gaussian_filter(low, 3.0))
            self.add("li_hag_low_std5", local_std(low, 5))
        else:
            for n in ("li_hag", "li_hag_max3", "li_hag_low_s1", "li_hag_low_s3", "li_hag_low_std5"):
                self.add(n, np.full((S.H, S.W), np.nan, np.float32))
        Z = S.lidar2
        nan = np.full((S.H, S.W), np.nan, np.float32)
        if Z and np.isfinite(Z["n_all"]).mean() > 0.5:
            cov = np.isfinite(Z["n_all"])
            for w in (3, 7):
                tot = ndimage.uniform_filter(np.nan_to_num(Z["n_all"]), w)
                for k in ("n_vlow", "n_low", "n_mid", "n_multi", "n_ground"):
                    fr = ndimage.uniform_filter(np.nan_to_num(Z[k]), w) / np.maximum(tot, 1e-3)
                    self.add(f"li_{k[2:]}_frac{w}", np.where(cov & (tot > 0.2), fr, np.nan))
                self.add(f"li_density{w}", np.where(cov, robust_norm(tot, ref), np.nan))
            self.add("li_hagstd3", ndimage.uniform_filter(np.nan_to_num(Z["hag_std"]), 3))
            self.add("li_hagmean3", ndimage.uniform_filter(np.nan_to_num(np.clip(Z["hag_mean"], 0, 30)), 3))
            for k in ("int_mean", "int_ground"):
                v = Z[k].copy()
                f = np.isfinite(v)
                if f.mean() > 0.3:
                    # fill empty cells from neighbours, then course-relative
                    _, (iy, ix) = ndimage.distance_transform_edt(~f, return_indices=True)
                    v = ndimage.uniform_filter(v[iy, ix], 3)
                    self.add(f"li_{k}", np.where(cov, robust_norm(v, ref), np.nan))
                else:
                    self.add(f"li_{k}", nan)
        else:
            for w in (3, 7):
                for k in ("vlow", "low", "mid", "multi", "ground"):
                    self.add(f"li_{k}_frac{w}", nan)
                self.add(f"li_density{w}", nan)
            for n in ("li_hagstd3", "li_hagmean3", "li_int_mean", "li_int_ground"):
                self.add(n, nan)

    def _terrain(self):
        S = self.S
        d = None
        if S.lidar2 and np.isfinite(S.lidar2.get("dtm1", np.array([np.nan]))).mean() > 0.6:
            d = S.lidar2["dtm1"]
        elif S.layers.get("dtm") is not None and np.isfinite(S.layers["dtm"]).mean() > 0.8:
            d = S.layers["dtm"]
        if d is not None:
            f = np.isfinite(d)
            _, (iy, ix) = ndimage.distance_transform_edt(~f, return_indices=True)
            dd = d[iy, ix]
            ds = ndimage.gaussian_filter(dd, 1.5)
            gy, gx = np.gradient(ds, S.res)
            self.add("slope", np.degrees(np.arctan(np.hypot(gx, gy))))
            self.add("relz25", ds - ndimage.gaussian_filter(dd, 25))
            self.add("relz8", ds - ndimage.gaussian_filter(dd, 8))
        else:
            for n in ("slope", "relz25", "relz8"):
                self.add(n, np.full((S.H, S.W), np.nan, np.float32))

    # ---------------------------------------------------------------- context
    def _context(self, osm_m, canopy):
        S = self.S
        for k, cap in (("fairway", 120), ("green", 200), ("tee", 200), ("bunker", 100), ("water", 150), ("mown", 120)):
            m = osm_m[k]
            self.add(f"d_{k}", np.minimum(ndimage.distance_transform_edt(~m) * S.res, cap) if m.any()
                     else np.full((S.H, S.W), cap, np.float32))
        out = ndimage.distance_transform_edt(~canopy) * S.res
        inn = ndimage.distance_transform_edt(canopy) * S.res
        self.add("d_canopy", np.clip(np.where(canopy, -inn, out), -30, 60))
        lab, n = ndimage.label(canopy)
        if n:
            sz = ndimage.sum(np.ones_like(canopy, np.float32), lab, np.arange(1, n + 1))
            area = np.r_[0, sz][lab]
            # area of the nearest clump (log m2)
            _, (iy, ix) = ndimage.distance_transform_edt(~canopy, return_indices=True)
            self.add("canopy_clump_log", np.log1p(area[iy, ix]))
            self.add("canopy_frac15", ndimage.uniform_filter(canopy.astype(np.float32), 15))
        else:
            self.add("canopy_clump_log", np.zeros((S.H, S.W), np.float32))
            self.add("canopy_frac15", np.zeros((S.H, S.W), np.float32))


NO_DIST = ("d_fairway", "d_green", "d_tee", "d_bunker", "d_water", "d_mown")
