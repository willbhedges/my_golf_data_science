"""S4 gap-fill: NAIP classifier polygons -> per-hole zones in the yard frame (ARCHITECTURE.md 3.6).

  python3 course_data/imagery/gapfill.py course_data/spirit_hollow [--loho]

gapfill(course_dir, holes, loho=False) -> {ref: [{"lie", "poly": [[x, y], ...], "p", "area_yd2"}, ...]}
  holes: {ref: hole} with tee_ll + aim_ll (the yard frame of 3.5; proj ENU) - e.g. auto_holes.json.
  Uses course_data/imagery/<slug>/gapfill.geojson (classify.py), or with loho=True the per-hole
  gapfill_loho/<key>.geojson from the model that did not see that hole (acceptance circularity rule).
Rules: only recovery / native / water; anything inside an OSM fairway, green, bunker, water or tee is
cut out (imagery never overrides OSM's mapped classes); pieces < 150 yd2 dropped; window +/-150 yds
lateral, 40 behind the tee to 40 past the green (min 330 along).
Writes course_data/imagery/<slug>/zones_vision.json (zones_vision_loho.json with --loho).
"""
import argparse
import json
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box, shape
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R                                     # noqa: E402

PROTECT = {("golf", "fairway"), ("golf", "green"), ("golf", "bunker"), ("golf", "tee"),
           ("natural", "water"), ("natural", "sand"), ("golf", "water_hazard"),
           ("golf", "lateral_water_hazard")}


def _protected(course_dir):
    fc = json.load(open(os.path.join(course_dir, "osm.geojson")))
    geoms = []
    for f in fc["features"]:
        p = f["properties"]
        if f["geometry"]["type"] in ("Polygon", "MultiPolygon") and any(p.get(k) == v for k, v in PROTECT):
            g = shape(f["geometry"])
            if g.is_valid or g.buffer(0).is_valid:
                geoms.append(g.buffer(0))
    return unary_union(geoms) if geoms else None


def _polys(g):
    return [g] if g.geom_type == "Polygon" else [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]


def gapfill(course_dir, holes, loho=False, imagery_dir=None):
    slug = os.path.basename(os.path.normpath(course_dir))
    idir = imagery_dir or os.path.join(HERE, slug)
    prot = _protected(course_dir)
    base = json.load(open(os.path.join(idir, "gapfill.geojson")))["features"]
    out = {}
    for ref, h in holes.items():
        feats = base
        if loho:
            p = os.path.join(idir, "gapfill_loho", f"{ref}.geojson")
            if not os.path.exists(p):
                continue
            feats = json.load(open(p))["features"]
        fr = R.Frame(h["tee_ll"], h["aim_ll"], proj="enu")
        g_yd = fr.ll_to_yds([h.get("green_ll") or h["aim_ll"]])[0]
        L = max(330.0, -g_yd[1] + 40)
        win = box(-150, -L, 150, 40)                  # yard frame: y = -along
        prot_yd = None
        if prot is not None:
            prot_yd = unary_union([Polygon(fr.ll_to_yds(np.array(pp.exterior.coords)),
                                           [fr.ll_to_yds(np.array(r.coords)) for r in pp.interiors]).buffer(0)
                                   for pp in _polys(prot)])
        zones = []
        for f in feats:
            for pg in _polys(shape(f["geometry"])):
                q = Polygon(fr.ll_to_yds(np.array(pg.exterior.coords)),
                            [fr.ll_to_yds(np.array(r.coords)) for r in pg.interiors]).buffer(0)
                q = q.intersection(win)
                if prot_yd is not None and not q.is_empty:
                    q = q.difference(prot_yd)
                for piece in _polys(q):
                    if piece.area < 150:
                        continue
                    piece = piece.simplify(2.0)
                    if piece.interiors:                    # model wants hole-free vertex lists
                        piece = Polygon(piece.exterior)
                    zones.append(dict(lie=f["properties"]["lie"],
                                      poly=[[round(x, 1), round(y, 1)] for x, y in piece.exterior.coords],
                                      p=f["properties"]["p"], area_yd2=round(piece.area)))
        out[str(ref)] = zones
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course_dir")
    ap.add_argument("--holes", help="holes JSON with tee_ll/aim_ll (default <course_dir>/auto_holes.json)")
    ap.add_argument("--loho", action="store_true")
    a = ap.parse_args()
    hp = a.holes or os.path.join(a.course_dir, "auto_holes.json")
    holes = json.load(open(hp))["holes"]
    res = gapfill(a.course_dir, holes, loho=a.loho)
    slug = os.path.basename(os.path.normpath(a.course_dir))
    meta = json.load(open(os.path.join(HERE, slug, "georef.json")))["imagery"]
    doc = dict(schema="zones_vision/1",
               imagery=dict(source="naip", date=meta["acquired"][0], gsd_m=meta["resolution_m"]),
               model="course_data/imagery/classify.py extratrees ndvi-texture-dem v1" + (" LOHO" if a.loho else ""),
               frame="yard (ENU about tee_ll, forward = aim_ll)", holes_from=os.path.relpath(hp), holes=res)
    name = "zones_vision_loho.json" if a.loho else "zones_vision.json"
    with open(os.path.join(HERE, slug, name), "w") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    for k, z in res.items():
        print(k, {lie: sum(1 for q in z if q["lie"] == lie) for lie in ("recovery", "native", "water")})


if __name__ == "__main__":
    main()
