"""Load / crop / save a perception stack (see fetch_stack.py for the layers) and map pixels <-> lon/lat."""
from __future__ import annotations

import json
import os

import numpy as np

SEG = ("green", "tee", "fairway", "bunker", "water")


def flat_coords(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Point":
        return [c]
    if t in ("LineString", "MultiPoint"):
        return list(c)
    if t in ("Polygon", "MultiLineString"):
        return [p for r in c for p in r]
    if t == "MultiPolygon":
        return [p for poly in c for r in poly for p in r]
    return []


class Stack:
    """Arrays on one north-up grid: pixel (row, col) centre = (y1 - (r + .5) res, x0 + (c + .5) res) in `crs`."""

    def __init__(self, arrays, meta, labels=None):
        self.a = arrays
        self.meta = meta
        self.labels = labels
        g = meta["grid"]
        self.crs = g["crs"]
        self.res = float(g["res_m"])
        self.x0, self.y1 = float(g["transform"][2]), float(g["transform"][5])
        self.H, self.W = arrays["naip"].shape[1:]
        self._fwd = self._inv = None

    # ---- coordinates
    def _tf(self):
        if self._fwd is None:
            from pyproj import Transformer
            self._fwd = Transformer.from_crs("EPSG:4326", self.crs, always_xy=True)
            self._inv = Transformer.from_crs(self.crs, "EPSG:4326", always_xy=True)
        return self._fwd, self._inv

    def ll_to_xy(self, lon, lat):
        return self._tf()[0].transform(lon, lat)

    def xy_to_ll(self, x, y):
        return self._tf()[1].transform(x, y)

    def xy_to_rc(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        return (self.y1 - y) / self.res - 0.5, (x - self.x0) / self.res - 0.5

    def rc_to_xy(self, r, c):
        r, c = np.asarray(r, float), np.asarray(c, float)
        return self.x0 + (c + 0.5) * self.res, self.y1 - (r + 0.5) * self.res

    def rc_to_ll(self, r, c):
        x, y = self.rc_to_xy(r, c)
        lon, lat = self.xy_to_ll(x, y)
        return np.asarray(lon), np.asarray(lat)

    def ll_to_rc(self, lon, lat):
        x, y = self.ll_to_xy(lon, lat)
        return self.xy_to_rc(x, y)

    # ---- layers as floats
    def naip(self):
        return self.a["naip"].astype(np.float32)

    def seg(self, name):
        return self.a["seg"][SEG.index(name)].astype(np.float32) / 255.0

    def hag(self):
        h = self.a["hag"].astype(np.float32) * 0.25
        h[self.a["hag"] == 255] = np.nan
        return h

    def has_lidar(self):
        return float((self.a["hag"] != 255).mean()) > 0.5

    def dtm(self):
        z = self.a["dtm"].astype(np.float32) / 100.0 + float(self.meta.get("dtm_base_m") or 0.0)
        z[self.a["dtm"] == 65535] = np.nan
        return z

    def cls(self):
        return self.a["cls"]

    def inten(self):
        i = self.a["inten"].astype(np.float32)
        i[self.a["inten"] == 0] = np.nan
        return i

    def valid(self):
        return self.a["naip"].any(axis=0)

    # ---- crop / io
    def crop(self, center_ll, size_m):
        r, c = self.ll_to_rc(*center_ll)
        n = int(round(size_m / self.res))
        r0 = int(np.clip(round(float(r)) - n // 2, 0, max(0, self.H - n)))
        c0 = int(np.clip(round(float(c)) - n // 2, 0, max(0, self.W - n)))
        r1, c1 = min(self.H, r0 + n), min(self.W, c0 + n)
        arr = {k: (v[..., r0:r1, c0:c1]).copy() for k, v in self.a.items()}
        meta = json.loads(json.dumps(self.meta))
        g = meta["grid"]
        x0 = self.x0 + c0 * self.res
        y1 = self.y1 - r0 * self.res
        g.update(width=c1 - c0, height=r1 - r0, transform=[self.res, 0, x0, 0, -self.res, y1],
                 bounds=[x0, y1 - (r1 - r0) * self.res, x0 + (c1 - c0) * self.res, y1])
        lo, la = self.xy_to_ll([x0, x0 + (c1 - c0) * self.res], [y1 - (r1 - r0) * self.res, y1])
        g["ll_bbox_wsen"] = [float(lo[0]), float(la[0]), float(lo[1]), float(la[1])]
        meta["crop"] = dict(of=meta.get("slug"), r0=r0, c0=c0, size_m=size_m)
        lab = None
        if self.labels:
            w, s, e, nn = g["ll_bbox_wsen"]
            keep = []
            for f in self.labels["features"]:
                cc = np.array(flat_coords(f["geometry"]) or [[1e9, 1e9]], float)
                if ((cc[:, 0] >= w - 0.003) & (cc[:, 0] <= e + 0.003) & (cc[:, 1] >= s - 0.003) & (cc[:, 1] <= nn + 0.003)).any():
                    keep.append(f)
            lab = dict(self.labels, features=keep)
        return Stack(arr, meta, lab)

    def save(self, d):
        os.makedirs(d, exist_ok=True)
        np.savez_compressed(os.path.join(d, "stack.npz"), **self.a)
        json.dump(self.meta, open(os.path.join(d, "meta.json"), "w"), indent=1, default=str)
        if self.labels is not None:
            json.dump(self.labels, open(os.path.join(d, "labels.geojson"), "w"))


def load(d):
    z = np.load(os.path.join(d, "stack.npz"))
    arrays = {k: z[k] for k in z.files}
    meta = json.load(open(os.path.join(d, "meta.json")))
    lp = os.path.join(d, "labels.geojson")
    labels = json.load(open(lp)) if os.path.exists(lp) else None
    return Stack(arrays, meta, labels)


def synthetic(H=400, W=400, res=1.0, lon0=-90.0, lat0=40.0):
    """An empty stack on a UTM grid around (lon0, lat0) for tests."""
    from pyproj import Transformer
    epsg = 32600 + int((lon0 + 180) // 6) + 1
    x, y = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True).transform(lon0, lat0)
    x0, y1 = float(np.floor(x)), float(np.ceil(y))
    meta = dict(schema="perception_stack/1", slug="synthetic", dtm_base_m=200.0,
                grid=dict(crs=f"EPSG:{epsg}", res_m=res, width=W, height=H, transform=[res, 0, x0, 0, -res, y1]),
                course=dict(name="Synthetic", center=[lon0, lat0]))
    arr = dict(naip=np.zeros((4, H, W), np.uint8), seg=np.zeros((5, H, W), np.uint8),
               hag=np.zeros((H, W), np.uint8), cls=np.full((H, W), 2, np.uint8),
               inten=np.full((H, W), 100, np.uint8), dtm=np.full((H, W), 1000, np.uint16))
    return Stack(arr, meta, dict(type="FeatureCollection", features=[]))
