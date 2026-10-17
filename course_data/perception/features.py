"""Derived per-pixel layers from a stack (1 m grid): spectral indices, terrain, lidar structure, line filters.

Everything here is blind (imagery + lidar only). Arrays are float32 (H, W); NaN where the source has no data.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def ndvi(st):
    n = st.naip()
    r, nir = n[0], n[3]
    return (nir - r) / np.maximum(nir + r, 1.0)


def brightness(st):
    n = st.naip()
    return (n[0] + n[1] + n[2]) / 3.0


def slope_pct(z, res=1.0, sigma=1.0):
    zz = np.where(np.isfinite(z), z, np.nanmedian(z) if np.isfinite(z).any() else 0.0)
    zs = ndi.gaussian_filter(zz, sigma / res)
    gy, gx = np.gradient(zs, res)
    s = 100.0 * np.hypot(gx, gy)
    s[~np.isfinite(z)] = np.nan
    return s.astype(np.float32)


def tophat(z, radius_m=15, res=1.0):
    """Height above the morphological opening (raised pads / greens stand out)."""
    zz = np.where(np.isfinite(z), z, np.nanmedian(z) if np.isfinite(z).any() else 0.0)
    r = max(1, int(radius_m / res))
    # grey opening with a square footprint is fast and close enough to a disk at this scale
    op = ndi.grey_opening(ndi.gaussian_filter(zz, 1.0), size=(2 * r + 1, 2 * r + 1))
    t = zz - op
    t[~np.isfinite(z)] = np.nan
    return t.astype(np.float32)


def local_mean(a, size):
    v = np.isfinite(a)
    num = ndi.uniform_filter(np.where(v, a, 0.0).astype(np.float32), size)
    den = ndi.uniform_filter(v.astype(np.float32), size)
    return num / np.maximum(den, 1e-6)


def local_std(a, size):
    m = local_mean(a, size)
    m2 = local_mean(np.where(np.isfinite(a), a * a, np.nan), size)
    return np.sqrt(np.maximum(m2 - m * m, 0))


def line_filter(img, sigmas=(1.0, 1.5, 2.0), black_ridges=False):
    """Ridge (thin bright line) response, 0-1-ish: Sato tubeness over 2-4 m wide lines."""
    from skimage.filters import sato
    x = np.nan_to_num(img.astype(np.float32), nan=float(np.nanmedian(img)) if np.isfinite(img).any() else 0.0)
    return sato(x, sigmas=list(sigmas), black_ridges=black_ridges).astype(np.float32)


class Layers:
    """Lazily computed layers for one stack (cached)."""

    def __init__(self, st):
        self.st = st
        self._c = {}

    def get(self, name):
        if name not in self._c:
            self._c[name] = getattr(self, "_" + name)()
        return self._c[name]

    def __getitem__(self, k):
        return self.get(k)

    def _ndvi(self):
        return ndvi(self.st)

    def _bright(self):
        return brightness(self.st)

    def _hag(self):
        return self.st.hag()

    def _dtm(self):
        return self.st.dtm()

    def _slope(self):
        return slope_pct(self.get("dtm"), self.st.res)

    def _tophat(self):
        return tophat(self.get("dtm"), 15, self.st.res)

    def _inten(self):
        return self.st.inten()

    def _valid(self):
        return self.st.valid()

    def _lidar(self):
        return self.st.has_lidar()

    def _tall(self):
        """Tree / building heights: HAG >= 2.5 m (lidar), else a dark-green textured NAIP proxy."""
        h = self.get("hag")
        if self.get("lidar"):
            return np.nan_to_num(h, nan=0.0) >= 2.5
        nd = self.get("ndvi")
        tex = local_std(self.get("bright"), 5)
        return (nd > 0.25) & (self.get("bright") < 90) & (tex > 9)

    def _paved(self):
        """Non-vegetated, low, flat-ish surfaces (paths, roads, parking, roofs filtered by HAG)."""
        nd = self.get("ndvi")
        h = np.nan_to_num(self.get("hag"), nan=0.0)
        low = h < 1.0 if self.get("lidar") else ~self.get("tall")
        return (nd < 0.12) & low & self.get("valid")

    def _line_paved(self):
        """Thin non-vegetated lines: Sato ridges of (-NDVI) at 1-2 px."""
        nd = np.nan_to_num(self.get("ndvi"), nan=0.0)
        return line_filter(-nd, (1.0, 1.5))

    def _line_bright(self):
        return line_filter(self.get("bright") / 255.0, (1.0, 1.5))

    def _nd_contrast(self):
        """NDVI of the 11 px surround minus the pixel (a path is less green than the grass beside it)."""
        nd = self.get("ndvi")
        return (local_mean(nd, 11) - nd).astype(np.float32)

    def _br_contrast(self):
        b = self.get("bright")
        return (b - local_mean(b, 11)).astype(np.float32)

    def _paved_width(self):
        """Distance (m) from a paved pixel to the nearest non-paved pixel, x2 = local width."""
        return (2.0 * ndi.distance_transform_edt(self.get("paved")) * self.st.res).astype(np.float32)

    def _paved_width_max(self):
        return ndi.maximum_filter(self.get("paved_width"), size=7)


PATH_FEATURES = ("ndvi", "bright", "nir", "r", "g", "b", "hag", "inten", "slope", "nd_contrast", "br_contrast",
                 "line_paved", "line_bright", "paved_width_max", "seg_green", "seg_tee", "seg_fairway", "seg_bunker",
                 "cls_ground", "cls_building", "ndvi_mean11", "bright_std5")


def path_feature_stack(L):
    """(n_features, H, W) float32 for the cart-path / road pixel classifier."""
    st = L.st
    n = st.naip()
    cls = st.cls()
    nd = L["ndvi"]
    out = {
        "ndvi": nd, "bright": L["bright"], "nir": n[3], "r": n[0], "g": n[1], "b": n[2],
        "hag": L["hag"], "inten": L["inten"], "slope": L["slope"], "nd_contrast": L["nd_contrast"],
        "br_contrast": L["br_contrast"], "line_paved": L["line_paved"], "line_bright": L["line_bright"],
        "paved_width_max": L["paved_width_max"], "seg_green": st.seg("green"), "seg_tee": st.seg("tee"),
        "seg_fairway": st.seg("fairway"), "seg_bunker": st.seg("bunker"),
        "cls_ground": ndi.uniform_filter((cls == 2).astype(np.float32), 3),
        "cls_building": ndi.uniform_filter((cls == 6).astype(np.float32), 3),
        "ndvi_mean11": local_mean(nd, 11), "bright_std5": local_std(L["bright"], 5),
    }
    return np.stack([np.asarray(out[k], np.float32) for k in PATH_FEATURES])
