"""Class probability raster -> WGS84 polygons (GeoJSON) for green / tee / fairway / bunker / water.

Each connected component of argmax == class (after a 1-px opening and hole filling) with area >= MIN_AREA_M2
becomes one feature: {"class", "src", "p" (mean class probability over the component), "area_m2"}.
Water: the U-Net water class is NOT polygonised (on our courses it marks the whole course interior); water
comes from the NAIP NIR rule model.nir_water (`src` "segment:nir").
"""
from __future__ import annotations

import numpy as np

from model import CLASSES

MIN_AREA_M2 = {"green": 80.0, "tee": 25.0, "fairway": 250.0, "bunker": 12.0, "water": 150.0}
SIMPLIFY_M = 0.6


def _components(mask, prob, res_m, min_area, transform, to_ll, cls, src):
    import rasterio.features
    from scipy import ndimage as ndi
    from shapely.geometry import mapping, shape
    from shapely.ops import transform as stransform
    m = ndi.binary_opening(mask, iterations=1)
    m = ndi.binary_fill_holes(m) if cls in ("green", "tee", "bunker") else m
    lab, n = ndi.label(m)
    if n == 0:
        return []
    px_area = res_m * res_m
    areas = ndi.sum(np.ones_like(lab, np.float32), lab, index=np.arange(1, n + 1)) * px_area
    pm = ndi.mean(prob, lab, index=np.arange(1, n + 1)) if prob is not None else np.ones(n)
    keep = np.zeros(n + 1, bool)
    keep[1:] = areas >= min_area
    lab = np.where(keep[lab], lab, 0).astype(np.int32)
    out = []
    for geom, v in rasterio.features.shapes(lab, mask=lab > 0, transform=transform):
        v = int(v)
        g = shape(geom).buffer(0).simplify(SIMPLIFY_M, preserve_topology=True)
        if g.is_empty or g.area < min_area * 0.5:
            continue
        gll = stransform(to_ll, g)
        out.append({"type": "Feature", "geometry": mapping(gll),
                    "properties": {"class": cls, "src": src, "p": round(float(pm[v - 1]), 3),
                                   "area_m2": round(float(g.area), 1)}})
    return out


def polygonize(probs, transform, crs, src="segment:unet", water=None, valid=None):
    """probs (6, H, W) float -> list of GeoJSON features in WGS84 (lon, lat). water = (mask, score) from model.nir_water."""
    from pyproj import Transformer
    tr = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    res = abs(transform.a)
    am = probs.argmax(0)
    if valid is not None:
        am = np.where(valid, am, 0)
    feats = []
    for ci, cls in enumerate(CLASSES):
        if cls in ("background", "water"):
            continue
        feats += _components(am == ci, probs[ci], res, MIN_AREA_M2[cls], transform, tr.transform, cls, src)
    if water is not None:
        feats += _components(water[0], water[1], res, MIN_AREA_M2["water"], transform, tr.transform, "water",
                             "segment:nir")
    return feats
