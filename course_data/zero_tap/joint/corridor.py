"""joint routing: corridor rasters. A hole is played over turf (fairway / green / tee), not over buildings, roads or
car parks; a virtual tee / green sits where a fairway corridor leads.

    R = Raster(co)                       # co["fair"] polygons, co["obst"] polygons (local yd)
    R.frac(P0, P1, R.fair)               # [...] share of each segment P0 -> P1 (arrays [..., 2]) on fairway
    R.frac(P0, P1, R.obst)               # ... on a building / road / car park

Cells of CELL yd, segments sampled at NS points between 8 % and 92 % of their length (the tee and green ends are
off the fairway on most holes). Everything is vectorised: thousands of segments in a few milliseconds.
"""
from __future__ import annotations

import numpy as np

CELL = 4.0
NS = 16


def _fill(mask, x0, y0, polys, cell):
    import cv2
    H, W = mask.shape
    for p in polys:
        geoms = getattr(p, "geoms", [p])
        for g in geoms:
            if g.is_empty or not hasattr(g, "exterior"):
                continue
            ext = np.asarray(g.exterior.coords)
            q = np.round(np.c_[(ext[:, 0] - x0) / cell, (ext[:, 1] - y0) / cell]).astype(np.int32)
            cv2.fillPoly(mask, [q.reshape(-1, 1, 2)], 1)
            for hole in g.interiors:
                h = np.asarray(hole.coords)
                q = np.round(np.c_[(h[:, 0] - x0) / cell, (h[:, 1] - y0) / cell]).astype(np.int32)
                cv2.fillPoly(mask, [q.reshape(-1, 1, 2)], 0)
    return mask


class Raster:
    def __init__(self, co, cell=CELL, pad=900.0):
        G = np.asarray(co["G"], float).reshape(-1, 2)
        pts = [G]
        if co.get("T"):
            pts.append(np.array([t["c"] for t in co["T"]], float).reshape(-1, 2))
        P = np.vstack(pts)
        self.x0, self.y0 = float(P[:, 0].min() - pad), float(P[:, 1].min() - pad)
        x1, y1 = float(P[:, 0].max() + pad), float(P[:, 1].max() + pad)
        self.cell = cell
        self.W, self.H = int((x1 - self.x0) / cell) + 1, int((y1 - self.y0) / cell) + 1
        self.fair = _fill(np.zeros((self.H, self.W), np.uint8), self.x0, self.y0,
                          [f["poly"] for f in co.get("fair") or []], cell)
        self.obst = _fill(np.zeros((self.H, self.W), np.uint8), self.x0, self.y0, co.get("obst") or [], cell)
        self.has_fair = bool(self.fair.any())

    def frac(self, P0, P1, mask, lo=0.08, hi=0.92, ns=NS):
        P0 = np.asarray(P0, float)
        P1 = np.asarray(P1, float)
        s = np.linspace(lo, hi, ns)
        shp = np.broadcast_shapes(P0.shape, P1.shape)
        P0 = np.broadcast_to(P0, shp)
        P1 = np.broadcast_to(P1, shp)
        X = P0[..., None, 0] + (P1[..., None, 0] - P0[..., None, 0]) * s
        Y = P0[..., None, 1] + (P1[..., None, 1] - P0[..., None, 1]) * s
        c = np.clip(((X - self.x0) / self.cell).astype(np.int64), 0, self.W - 1)
        r = np.clip(((Y - self.y0) / self.cell).astype(np.int64), 0, self.H - 1)
        return mask[r, c].mean(-1)

    def at(self, P, mask):
        P = np.asarray(P, float)
        c = np.clip(((P[..., 0] - self.x0) / self.cell).astype(np.int64), 0, self.W - 1)
        r = np.clip(((P[..., 1] - self.y0) / self.cell).astype(np.int64), 0, self.H - 1)
        return mask[r, c]
