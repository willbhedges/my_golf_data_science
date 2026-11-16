"""Hole lines for a course OSM does not map well enough to route (tiers C / D): OSM greens / tee boxes / fairways
where OSM has them, plus the fast-path perception scene's (fastscene.py) where it does not, routed by the same
joint solver as route_joint.py (zero_tap/joint, card-aware, tee_reuse) and written as golf=hole ways.

    co, info = candidates(fc, scene)         # zero_tap/joint Course: OSM first, scene detections that add to it
    r = route(fc, scene, card, n_holes)      # route_joint.route's result + per-hole sources

A detection enters only with its probability >= P_GREEN / P_TEE, and never within MERGE_YD of an OSM object of the
same kind (OSM wins). The joint models were fitted on OSM candidates (p 0.9 each), so every kept candidate gets
p 0.9 too: the detector's probability only decides whether it is a candidate. Gate (fast.py): a course routed on
detections is shown only with min margin >= route_joint.MIN_MARGIN and no virtual hole, like route_joint; every
hole whose green or tee came from the detector carries a confirm flag.
"""
from __future__ import annotations

import math

import numpy as np

import route_joint as RJ

P_GREEN = 0.5
P_TEE = 0.4
MERGE_YD = 25.0
FAIRWAY_MIN_M2 = 1500.0


def _mods():
    return RJ._mods()


MAX_GREENS_PER_HOLE, MAX_TEES_PER_HOLE, MAX_CAND = 2.0, 3.0, 60     # the joint solver's bitmask holds 63


def candidates(fc, scene, p_green=P_GREEN, p_tee=P_TEE, n_holes=18):
    C, F, M, S = _mods()
    from shapely.geometry import Polygon
    TR = C.TR
    feats = (fc or {}).get("features", [])
    osm_g = [f for f in feats if (f.get("properties") or {}).get("golf") == "green"
             and (f.get("properties") or {}).get("inside_course") is not False]
    osm_t = [f for f in feats if (f.get("properties") or {}).get("golf") == "tee"
             and (f.get("properties") or {}).get("inside_course") is not False]
    sg = [g for g in (scene or {}).get("greens") or [] if g.get("kind") != "practice"
          and float(g.get("p_hole", g.get("p", 0))) >= p_green]
    st = [t for t in (scene or {}).get("tee_complexes") or [] if not t.get("virtual")
          and float(t.get("p", 0)) * (1 - float(t.get("p_range_tee") or 0)) >= p_tee]
    sg = sorted(sg, key=lambda g: -float(g.get("p_hole", g.get("p", 0))))[:max(0, min(MAX_CAND - len(osm_g), int(MAX_GREENS_PER_HOLE * n_holes)))]
    st = sorted(st, key=lambda t: -float(t.get("p", 0)))[:int(MAX_TEES_PER_HOLE * n_holes)]
    pts = [TR._centroid(TR._outer(f["geometry"])[0]) for f in osm_g if TR._outer(f["geometry"])] + [g["centroid"] for g in sg]
    if not pts:
        raise ValueError("no greens (OSM or detected)")
    pj = TR.Proj(float(np.mean([q[0] for q in pts])), float(np.mean([q[1] for q in pts])))
    co = dict(pj=pj, source="osm+scene", G=[], Gr=[], Gp=[], Gid=[], Gsrc=[], T=[], fair=[], club=None)
    for f in osm_g:
        for r in TR._outer(f["geometry"]):
            q = C._poly(pj, r)
            if q is not None and q.area > 30:
                co["G"].append((q.centroid.x, q.centroid.y))
                co["Gr"].append(math.sqrt(q.area / math.pi))
                co["Gp"].append(0.9)
                co["Gid"].append("osm:%s/%s" % (f["properties"].get("osm_type"), f["properties"].get("osm_id")))
                co["Gsrc"].append("osm")
    n_osm_g = len(co["G"])
    for g in sg:
        xy = C._xy(pj, g["centroid"])
        if n_osm_g and min(math.hypot(xy[0] - a, xy[1] - b) for a, b in co["G"][:n_osm_g]) < MERGE_YD:
            continue
        co["G"].append(xy)
        co["Gr"].append(math.sqrt(max(float(g.get("area_m2") or 300.0), 30.0) / math.pi) / 0.9144)
        co["Gp"].append(0.9)
        co["Gid"].append("scene:" + g["id"])
        co["Gsrc"].append("scene")
    # tee boxes: OSM polygons / points, grouped into complexes as from_osm does; scene complexes added whole
    boxes = []
    for f in osm_t:
        p = f["properties"]
        fid = "osm:%s/%s" % (p.get("osm_type", "x"), p.get("osm_id", "?"))
        if f["geometry"]["type"] == "Point":
            x, y = C._xy(pj, f["geometry"]["coordinates"])
            boxes.append((Polygon([(x - 3, y - 3), (x + 3, y - 3), (x + 3, y + 3), (x - 3, y + 3)]), fid))
            continue
        for r in TR._outer(f["geometry"]):
            q = C._poly(pj, r)
            if q is not None:
                boxes.append((q, fid))
    par = list(range(len(boxes)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i][0].distance(boxes[j][0]) <= 28.0:
                par[find(i)] = find(j)
    grp = {}
    for i in range(len(boxes)):
        grp.setdefault(find(i), []).append(i)
    for mem in grp.values():
        bp = [(boxes[i][0].centroid.x, boxes[i][0].centroid.y) for i in mem]
        co["T"].append(dict(c=tuple(np.mean(bp, 0)), pts=bp, id=boxes[mem[0]][1], ax=_axis(bp), p=0.9, src="osm"))
    osm_tc = [t["c"] for t in co["T"]]
    for t in st:
        bp = [C._xy(pj, b["centroid"]) for b in t.get("boxes", []) if b.get("centroid")] or [C._xy(pj, t["centroid"])]
        c = tuple(np.mean(bp, 0))
        if osm_tc and min(math.hypot(c[0] - a, c[1] - b) for a, b in osm_tc) < MERGE_YD:
            continue
        ax = None
        if t.get("axis_deg") is not None and float(t.get("length_m") or 0) > 12:
            a = math.radians(float(t["axis_deg"]))
            ax = (math.sin(a), math.cos(a))
        co["T"].append(dict(c=c, pts=bp, id="scene:" + t["id"], ax=ax or _axis(bp), p=0.9, src="scene"))
    if not co["T"]:
        raise ValueError("no tees (OSM or detected)")
    co["T"] = co["T"][:MAX_CAND]
    fair, park, club = C._osm_context(fc, pj)
    osm_fair = len(fair)
    for f in (scene or {}).get("fairways") or []:
        q = C._poly(pj, f["polygon"])
        if q is None or q.area * 0.836 < FAIRWAY_MIN_M2:
            continue
        if any(q.intersection(o["poly"]).area > 0.3 * q.area for o in fair[:osm_fair]):
            continue
        fair.append(dict(poly=q, cl=C.centreline(q)))
    co["fair"] = fair
    sp = [C._xy(pj, p["centroid"]) + (float(p.get("area_m2") or 0),) for p in (scene or {}).get("parking") or []]
    C._pick_club(co, park + sp, club)
    co = C._finish(co)
    info = dict(greens_osm=n_osm_g, greens_scene=len(co["G"]) - n_osm_g,
                tees_osm=sum(t["src"] == "osm" for t in co["T"]), tees_scene=sum(t["src"] == "scene" for t in co["T"]),
                fairways_osm=osm_fair, fairways_scene=len(fair) - osm_fair)
    return co, info


def _axis(pts):
    if len(pts) < 2:
        return None
    d = np.asarray(pts, float) - np.mean(pts, 0)
    w, v = np.linalg.eigh(d.T @ d)
    return (float(v[0, 1]), float(v[1, 1])) if w[1] > 15 ** 2 else None


def route(fc, scene, card, n_holes, co=None):
    import pickle
    C, F, M, S = _mods()
    if RJ._MS[0] is None:
        RJ._MS[0] = pickle.load(open(RJ.MODEL, "rb"))
    if co is None:
        co, info = candidates(fc, scene, n_holes=n_holes)
    else:
        info = {}
    geo = F.geometry(co)
    hp, hx = F.hole_features(co, geo)
    wp, wx, W = F.walk_features(co, geo)
    d = dict(row=dict(slug="x"), co=co, geo=geo, hp=hp, hx=hx, wp=wp, wx=wx, W=W, card=card, kind=int(n_holes))
    d["sc"] = M.predict(RJ._MS[0], d)
    sol = S.solve(d, card, RJ.PARAMS, None)
    if not sol["seq"]:
        return dict(features=[], min_margin=0.0, why="no routing found", **info)
    mg = S.margins(sol, None)
    pars = (card or {}).get("par") or []
    feats, nv, det, used = [], 0, [], []
    for i, (t, g) in enumerate(sol["holes"]):
        if t < 0 or g < 0:
            nv += 1
            continue
        tc = co["T"][t]
        far = int(np.argmax(np.hypot(*(np.asarray(tc["pts"]) - np.asarray(co["G"][g])).T)))
        path = RJ._line(F, co, tc["pts"][far], co["G"][g])
        line = [[round(v, 7) for v in co["pj"].inv(*q)] for q in path]
        L = float(geo["P"][t, g])
        par = pars[i % len(pars)] if pars else (3 if L < 245 else 4 if L < 470 else 5)
        src = dict(green=co["Gsrc"][g], tee=tc["src"])
        used += [co["Gid"][g], tc["id"]]
        if "scene" in src.values():
            det.append(str(i + 1))
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": line},
                      "properties": {"golf": "hole", "ref": str(i + 1), "par": str(par), "src": "joint:scene",
                                     "green_src": src["green"], "tee_src": src["tee"],
                                     "margin": round(float(mg[i]), 2)}})
    return dict(features=feats, min_margin=float(min(mg)) if len(mg) else 0.0, margins=[round(float(m), 2) for m in mg],
                n_virtual=nv, n_holes=int(n_holes), greens=len(co["G"]), tee_complexes=len(co["T"]),
                detected_holes=det, _used=used, **info)


def scene_features(scene, kinds=("green", "tee", "fairway", "bunker", "water"), used=None):
    """Scene objects as OSM-style features (properties golf=..., src fastscene) for the package build: greens and
    tee boxes the routing used (ids in `used`, None = all above threshold), fairways, bunkers, water."""
    out = []

    def poly(ring):
        return {"type": "Polygon", "coordinates": [ring + ([ring[0]] if ring and ring[0] != ring[-1] else [])]}
    if "green" in kinds:
        for g in scene.get("greens") or []:
            if g.get("polygon") and len(g["polygon"]) >= 3 and (used is None and float(g.get("p_hole", g.get("p", 0))) >= P_GREEN
                                                                  or used is not None and "scene:" + g["id"] in used):
                out.append(dict(type="Feature", geometry=poly(g["polygon"]),
                                properties=dict(golf="green", src="fastscene", p=g.get("p_hole", g.get("p")), id=g["id"])))
    if "tee" in kinds:
        for t in scene.get("tee_complexes") or []:
            if t.get("virtual") or (used is not None and "scene:" + t["id"] not in used):
                continue
            if used is None and float(t.get("p", 0)) < P_TEE:
                continue
            for b in t.get("boxes") or []:
                if b.get("polygon") and len(b["polygon"]) >= 3:
                    out.append(dict(type="Feature", geometry=poly(b["polygon"]),
                                    properties=dict(golf="tee", src="fastscene", p=t.get("p"), id=b.get("id"))))
    for kind, key, golf in (("fairway", "fairways", "fairway"), ("bunker", "bunkers", "bunker"), ("water", "water", "water_hazard")):
        if kind not in kinds:
            continue
        for o in scene.get(key) or []:
            if o.get("polygon") and len(o["polygon"]) >= 3 and float(o.get("p", 1.0)) >= 0.5:
                out.append(dict(type="Feature", geometry=poly(o["polygon"]),
                                properties=dict(golf=golf, src="fastscene", p=o.get("p"), id=o.get("id"))))
    return out


def needs_perception(fc, n_holes):
    """True when OSM cannot be routed on its own: < 3 hole lines and greens or tee boxes short of the hole count
    (tiers C / D). Courses with (nearly) every line, or with greens + tees for route_joint, keep their paths."""
    lines = green = tee = 0
    for f in (fc or {}).get("features", []):
        p = f.get("properties") or {}
        if p.get("inside_course") is False:
            continue
        g = p.get("golf")
        lines += g == "hole" and (f.get("geometry") or {}).get("type") == "LineString"
        green += g == "green"
        tee += g == "tee"
    return lines < 3 and (green < 0.8 * n_holes or tee < 0.8 * n_holes)


def run(pkg_dir, fc, card, n_holes, log=None):
    """Build the fast-path scene (fastscene.build -> pkg_dir/scene.json), route OSM + detections jointly.
    -> (route result without features, supplement features [golf=hole lines + the detected greens / tee boxes the
    route uses + detected fairways / bunkers / water where OSM has none of that kind], seconds)"""
    import time
    import fastscene as FS
    T = {}
    t = time.time()
    scene, info = FS.build(pkg_dir)
    T["scene"] = info["seconds"]
    t1 = time.time()
    co, ci = candidates(fc, scene, n_holes=n_holes)
    r = route(fc, scene, card, n_holes, co=co)
    r.update(ci)
    T["route"] = round(time.time() - t1, 2)
    used = set(r.pop("_used", []))
    have = {(f.get("properties") or {}).get("golf") for f in (fc or {}).get("features", [])
            if (f.get("properties") or {}).get("inside_course") is not False}
    kinds = ["fairway"] * ("fairway" not in have) + ["bunker"] * ("bunker" not in have) + \
            ["water"] * (not ({"water_hazard", "lateral_water_hazard"} & have))
    sup = list(r.get("features") or [])
    sup += scene_features(scene, ("green", "tee"), used=used)
    sup += scene_features(scene, tuple(kinds))
    for f in sup:
        f["properties"]["origin"] = "fastscene"
    T["total"] = round(time.time() - t, 2)
    return {k: v for k, v in r.items() if k != "features"}, sup, T
