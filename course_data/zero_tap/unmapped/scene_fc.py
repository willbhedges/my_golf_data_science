"""Perception scene (course_scene/1) -> OSM-style feature collection that pathroute's Scene reads unchanged.

The unmapped tier's fc (truth.strip_golf: no golf=* at all) keeps buildings, car parks, highway paths and water;
this adds the perceived golf layer on top, tagged the way OSM tags it:

  greens        golf=green polygons with p >= g_min (any kind: practice greens are left to the decoder, which drops
                greens that fit no route); `p`, `p_hole`, `kind`, `raised_m` kept as properties
  tee boxes     golf=tee: every box of every complex with p_complex >= t_min (OSM maps boxes, and pathroute_v2's
                complex model groups boxes itself); a complex without boxes becomes one tee
                (tee_mode="complex": one golf=tee per perceived complex, its hull)
  extra tees    optional (`pads=True`): lidar pads / segment-model tee blobs that are not already inside a perceived
                complex and sit 60-650 m from a perceived green (the "missing back tee" fallback)
  fairways      golf=fairway polygons with p >= f_min
  cart paths    golf=cartpath lines (perceived edges)
  water         golf=water_hazard polygons with p >= 0.5 (OSM water already in the fc stays)
  clubhouse     building=clubhouse polygon when the scene's clubhouse p >= 0.5

Ids are `osm_type=p`, `osm_id=<scene id>` so pathroute_v2's per-feature property lookup works.
"""
from __future__ import annotations

import math


def _poly(ring):
    r = [list(p[:2]) for p in ring]
    if r and r[0] != r[-1]:
        r.append(r[0])
    return {"type": "Polygon", "coordinates": [r]}


def _f(geom, oid, **props):
    return {"type": "Feature", "geometry": geom, "properties": dict(osm_type="p", osm_id=oid, **props)}


def _m(a, b):
    """metres between two lon/lat points (equirectangular, fine at course scale)."""
    kx = 111320.0 * math.cos(math.radians((a[1] + b[1]) / 2))
    return math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * 110540.0)


def golf_features(scene, g_min=0.0, t_min=0.0, f_min=0.0, pads=None, seg=None, extra_tees=False, tee_mode="boxes"):
    out = []
    greens = [g for g in scene.get("greens", []) if float(g.get("p", 1)) >= g_min and g.get("polygon")]
    for g in greens:
        out.append(_f(_poly(g["polygon"]), g["id"], golf="green", p=g.get("p"), p_hole=g.get("p_hole"),
                      kind=g.get("kind"), raised_m=g.get("raised_m")))
    tee_pts = []
    for t in scene.get("tee_complexes", []):
        pc = float(t.get("p", 1)) * (1 - float(t.get("p_range_tee") or 0))
        if pc < t_min:
            continue
        boxes = [b for b in t.get("boxes", []) if b.get("polygon") and len(b["polygon"]) >= 3]
        if tee_mode == "complex":
            boxes = []
        if boxes:
            for b in boxes:
                out.append(_f(_poly(b["polygon"]), b["id"], golf="tee", p=b.get("p"), p_complex=pc, complex=t["id"]))
                tee_pts.append(b["centroid"])
        elif t.get("polygon") and len(t["polygon"]) >= 3:
            out.append(_f(_poly(t["polygon"]), t["id"], golf="tee", p=pc, p_complex=pc, complex=t["id"]))
            tee_pts.append(t["centroid"])
        elif t.get("centroid"):
            out.append(_f({"type": "Point", "coordinates": list(t["centroid"][:2])}, t["id"], golf="tee", p=pc,
                          p_complex=pc, complex=t["id"]))
            tee_pts.append(t["centroid"])
    if extra_tees:
        gc = [g["centroid"] for g in greens if g.get("kind") != "practice"]
        cands = []
        for i, p in enumerate(pads or []):
            ring = [[q[1], q[0]] for q in p.get("coords") or []]          # pads.json is [lat, lon]
            c = [p["centroid"][1], p["centroid"][0]]
            if len(ring) >= 3 and 60 <= float(p.get("area_m2") or 0) <= 1500:
                cands.append((f"pad{i}", c, ring, "lidar_pad"))
        for i, f in enumerate((seg or {}).get("features", [])):
            if (f.get("properties") or {}).get("class") != "tee":
                continue
            geom = f.get("geometry") or {}
            if geom.get("type") != "Polygon":
                continue
            ring = geom["coordinates"][0]
            c = [sum(q[0] for q in ring) / len(ring), sum(q[1] for q in ring) / len(ring)]
            cands.append((f"seg{i}", c, ring, "segment"))
        kept = []
        for oid, c, ring, src in cands:
            if any(_m(c, q) < 25 for q in tee_pts + [k[1] for k in kept]):
                continue
            dg = min((_m(c, q) for q in gc), default=0)
            if not (60 <= dg <= 650) or min((_m(c, q) for q in gc), default=1e9) < 40:
                continue
            kept.append((oid, c, ring, src))
        for oid, c, ring, src in kept:
            out.append(_f(_poly(ring), oid, golf="tee", p=0.2, p_complex=0.2, complex=oid, extra=src))
    for fw in scene.get("fairways", []):
        if float(fw.get("p", 1)) >= f_min and fw.get("polygon") and len(fw["polygon"]) >= 3:
            out.append(_f(_poly(fw["polygon"]), fw["id"], golf="fairway", p=fw.get("p")))
    for e in (scene.get("cart_paths") or {}).get("edges", []):
        if e.get("line") and len(e["line"]) >= 2:
            out.append(_f({"type": "LineString", "coordinates": [list(q[:2]) for q in e["line"]]}, e["id"],
                          golf="cartpath", p=e.get("p")))
    for w in scene.get("water", []):
        if float(w.get("p", 1)) >= 0.5 and w.get("polygon") and len(w["polygon"]) >= 3:
            out.append(_f(_poly(w["polygon"]), w["id"], golf="water_hazard", p=w.get("p")))
    ch = scene.get("clubhouse") or {}
    if ch and float(ch.get("p") or 0) >= 0.5 and ch.get("building"):
        b = next((x for x in scene.get("buildings", []) if x["id"] == ch["building"]), None)
        if b and b.get("polygon"):
            out.append(_f(_poly(b["polygon"]), "club_" + b["id"], golf="clubhouse", building="clubhouse"))
    return out


def unmapped_fc(fc, scene, **kw):
    """fc: the tier's (golf-stripped) feature collection -> the same plus the perceived golf layer."""
    return {"type": "FeatureCollection", "features": list(fc.get("features", [])) + golf_features(scene, **kw)}
