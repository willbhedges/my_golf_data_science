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
import os

import numpy as np

import route_joint as RJ

P_GREEN = 0.35
P_TEE = 0.3
MERGE_YD = 25.0
FAIRWAY_MIN_M2 = 1500.0


def _mods():
    return RJ._mods()


MAX_GREENS_PER_HOLE, MAX_TEES_PER_HOLE, MAX_CAND = 2.0, 3.0, 60     # the joint solver's bitmask holds 63


SPLIT_TEES = os.environ.get("ROUTE_SPLIT_TEES", "1") == "1"     # v2 default (route_bench train: all-right 8 -> 11)
SPLIT_MIN_YD, SPLIT_GAP_YD = 25.0, 6.0


def split_complex(pts, min_len=None, min_gap=None):
    """a tee complex whose boxes may belong to two holes (boxes touching, so the detector merged them): split at the
    largest gap between consecutive boxes along its long axis when it spans >= SPLIT_MIN_YD and that gap is >=
    SPLIT_GAP_YD. -> [] or [boxes a, boxes b] (the routing keeps the whole complex as well)"""
    min_len = SPLIT_MIN_YD if min_len is None else min_len
    min_gap = SPLIT_GAP_YD if min_gap is None else min_gap
    P = np.asarray(pts, float).reshape(-1, 2)
    if len(P) < 2:
        return []
    c = P - P.mean(0)
    w, v = np.linalg.eigh(c.T @ c)
    s = c @ v[:, 1]
    o = np.argsort(s)
    if s[o[-1]] - s[o[0]] < min_len:
        return []
    gaps = np.diff(s[o])
    j = int(np.argmax(gaps))
    if gaps[j] < min_gap:
        return []
    return [[tuple(P[i]) for i in o[:j + 1]], [tuple(P[i]) for i in o[j + 1:]]]


def candidates(fc, scene, p_green=P_GREEN, p_tee=P_TEE, n_holes=18, split_tees=None):
    C, F, M, S = _mods()
    from shapely.geometry import Polygon
    TR = C.TR
    split_tees = SPLIT_TEES if split_tees is None else split_tees
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
    if split_tees:                                   # complexes that may serve two holes: their two halves as well
        n0 = len(co["T"])
        for k in range(n0):
            tt = co["T"][k]
            if tt["src"] != "scene" or len(co["T"]) >= MAX_CAND:
                continue
            for half, bp2 in zip("ab", split_complex(tt["pts"])):
                co["T"].append(dict(c=tuple(np.mean(bp2, 0)), pts=bp2, id=tt["id"] + "/" + half, ax=_axis(bp2),
                                    p=0.9, src="scene"))
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
    co["obst"] = obstacles(fc, scene, pj, C)
    co["trees"] = [C._xy(pj, t["centroid"]) + (math.sqrt(max(float(t.get("area_m2") or 0.0), 1.0) / math.pi) / 0.9144,)
                   for t in (scene or {}).get("trees") or [] if t.get("centroid") and float(t.get("p", 1.0)) >= 0.5
                   and float(t.get("area_m2") or 0.0) >= 20.0]
    sp = [C._xy(pj, p["centroid"]) + (float(p.get("area_m2") or 0),) for p in (scene or {}).get("parking") or []]
    C._pick_club(co, park + sp, club)
    co = C._finish(co)
    info = dict(greens_osm=n_osm_g, greens_scene=len(co["G"]) - n_osm_g,
                tees_osm=sum(t["src"] == "osm" for t in co["T"]), tees_scene=sum(t["src"] == "scene" for t in co["T"]),
                fairways_osm=osm_fair, fairways_scene=len(fair) - osm_fair)
    return co, info


ROADS = ("motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street",
         "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link")


def obstacles(fc, scene, pj, C):
    """Polygons (local yd) a hole is not played over: OSM buildings, car parks and public roads (buffered 5 yd) from
    the non-golf OSM features, and the scene's detected buildings / car parks (p >= 0.5)."""
    from shapely.geometry import LineString
    out = []
    for f in (fc or {}).get("features", []):
        p, g = f.get("properties") or {}, f.get("geometry") or {}
        if p.get("golf") or p.get("origin") == "fastscene":
            continue
        if (p.get("building") or p.get("amenity") == "parking") and g.get("type") in ("Polygon", "MultiPolygon"):
            for r in C.TR._outer(g):
                q = C._poly(pj, r)
                if q is not None and q.area > 20:
                    out.append(q)
        elif p.get("highway") in ROADS and g.get("type") == "LineString" and len(g["coordinates"]) >= 2:
            try:
                out.append(LineString([C._xy(pj, c) for c in g["coordinates"]]).buffer(5.0))
            except Exception:                                        # noqa: BLE001
                pass
    for key in ("buildings", "parking"):
        for o in (scene or {}).get(key) or []:
            if o.get("polygon") and len(o["polygon"]) >= 3 and float(o.get("p", 1.0)) >= 0.5:
                q = C._poly(pj, o["polygon"])
                if q is not None:
                    out.append(q)
    return out


def _axis(pts):
    if len(pts) < 2:
        return None
    d = np.asarray(pts, float) - np.mean(pts, 0)
    w, v = np.linalg.eigh(d.T @ d)
    return (float(v[0, 1]), float(v[1, 1])) if w[1] > 15 ** 2 else None


V1_PARAMS = dict(K=18, beam=3000, tee_reuse=1, tee_box="long", c_vt=2.0, c_vg=2.0)   # c_vt / c_vg: route_bench tune (train)
RERANK = int(os.environ.get("ROUTE_RERANK", "1") or 0)   # route_rerank.py: alternatives scored by a learned model
V1_LIKE = ("v1", "v2")         # v2: v1's solver + map-recovered greens and learned hole / walk scores (route_learn.py)
ROUTER = os.environ.get("ROUTE_SCENE_VERSION", "v2")      # fast.py's unmapped routing (v1 / v0: the previous solvers)
SCENE_MODEL = os.path.join(RJ.J, "model_scene.pkl")    # evidence models fitted on detection-like candidates (fit_scene.py)
_SM = {}


def _models(version, params):
    """v0: model_osm.pkl (as before); v1: model_scene.pkl when present (params 'model': 'osm' keeps model_osm)"""
    import pickle
    path = RJ.MODEL if version not in V1_LIKE or (params or {}).get("model") == "osm" or not os.path.exists(SCENE_MODEL) \
        else SCENE_MODEL
    if path not in _SM:
        _SM[path] = pickle.load(open(path, "rb"))
    return _SM[path]


def prepare(fc, scene, card, n_holes, co=None, version="v0", params=None):
    """candidates + geometry + features + evidence-model scores -> (d, info): the solver's input (cacheable)"""
    C, F, M, S = _mods()
    ms = _models(version, params)
    if co is None:
        co, info = candidates(fc, scene, n_holes=n_holes)
    else:
        info = {}
    geo = F.geometry(co)
    hp, hx = F.hole_features(co, geo)
    wp, wx, W = F.walk_features(co, geo)
    d = dict(row=dict(slug="x"), co=co, geo=geo, hp=hp, hx=hx, wp=wp, wx=wx, W=W, card=card, kind=int(n_holes))
    d["sc"] = M.predict(ms, d)
    return d, info


def _alts(S2, sol, k):
    """the k best other routings of the plain and the priced beam: [(cost gap, holes whose (tee, green) differ)],
    by gap (the course-level confidence reads them; the chosen routing is unchanged)"""
    pr, seq = sol["pr"], sol["seq"]
    try:
        rs = S2.beam2(pr, keep=k + 1)
        if pr.P.get("lag_iters", 0) > 0:
            pz = sol.get("price")
            if pz is None:
                pz = sol["price"] = S2.lagrange(pr)
            rs += S2.beam2(pr, keep=k + 1, price=pz)
    except Exception:                                                # noqa: BLE001
        return []
    best = [tuple(pr.cand[c][1:]) for c in seq]
    out, seen = [], {tuple(seq)}
    for cost, s2 in sorted(rs, key=lambda r: r[0]):
        if tuple(s2) in seen:
            continue
        seen.add(tuple(s2))
        ham = sum(tuple(pr.cand[c][1:]) != b for c, b in zip(s2, best))
        if ham:
            out.append([round(max(0.0, float(cost) - float(sol["cost"])), 3), int(ham)])
    return out[:k]


def route(fc, scene, card, n_holes, co=None, version="v0", params=None, prepared=None):
    """version v0: zero_tap/joint solve.py (missing tee / hole = free placeholder); v1: solve2.py (the card places
    missing tees / greens; virtual ends are written as hole-line ends with tee_src / green_src 'virtual').
    prepared: prepare()'s (d, info) to skip the candidate / feature stage."""
    C, F, M, S = _mods()
    params = dict(params or {})
    d, info = prepared or prepare(fc, scene, card, n_holes, co, version, params)
    params.pop("model", None)
    co, geo = d["co"], d["geo"]
    if version in V1_LIKE:
        import solve2 as S2
        pp = dict(V1_PARAMS)
        pp.update(V2_PARAMS if version == "v2" else {})
        pp.update(params or {})
        nomg = pp.pop("no_margins", False)
        fix_seq = pp.pop("fix_seq", None)                    # the bench's out-of-fold re-ranker pick (route_rerank)
        rr = pp.pop("rerank", RERANK if version == "v2" else 0)
        sol = S2.solve(d, card, pp, None)
        if not sol["seq"]:
            return dict(features=[], min_margin=0.0, why="no routing found", **info)
        rr_info = None
        if fix_seq is not None or rr:
            import route_rerank as RR
            seq0 = list(sol["seq"])
            if fix_seq is not None:
                new = [int(c) for c in fix_seq] if len(fix_seq) == len(seq0) else seq0
                rr_info = dict(fixed=True)
            else:
                new, rr_info = RR.rerank(sol["pr"], seq0)
            if new != seq0:
                sol = dict(sol, seq=new, holes=[sol["pr"].cand[c] for c in new],
                           cost=RR.cost_parts(sol["pr"], new)["total"], cost0=sol["cost"])
                rr_info = dict(rr_info or {}, switched=True,
                               changed=[i for i, (a, b) in enumerate(zip(seq0, new)) if a != b])
        tee_box = pp.pop("tee_box", "far")
        tee_fix = pp.pop("tee_fix", None)                    # the bench's out-of-fold tee choices (route_tee)
        tee_dump = pp.pop("tee_dump", None)                  # a list: route_tee candidates appended (training rows)
        tee_rr = pp.pop("tee", 1)
        n_alts = int(pp.pop("alts", 8))
        # margins against the solver's own optimum: a re-ranked routing's unchanged holes keep their min-marginals,
        # its changed holes get ~0 (the optimum does not use them there)
        mg = [0.0] * len(sol["seq"]) if nomg else S2.margins(dict(sol, cost=sol.get("cost0", sol["cost"])), None)
        alts = _alts(S2, sol, n_alts) if n_alts else []
        virt = S2.place_virtual(sol)
        if pp.get("refine") and d.get("_maps") is not None:        # virtual ends onto P(green) / P(tee) / fairway ends
            virt = S2.refine_virtual(sol, virt, d["_maps"], pp.get("refine_params"))
        pr2 = sol["pr"]
        holes = [(t, g) for k, t, g in sol["holes"]]
    else:
        alts = []
        sol = S.solve(d, card, dict(RJ.PARAMS, **(params or {})), None)
        if not sol["seq"]:
            return dict(features=[], min_margin=0.0, why="no routing found", **info)
        mg = S.margins(sol, None)
        virt = {}
        holes = sol["holes"]
    pars = (card or {}).get("par") or []
    feats, nv, det, used = [], 0, [], []
    n_vt = n_vg = n_miss = 0
    hole_f = []                                     # per-hole confidence features (v1): the gate's calibration input
    yk = None
    if version in V1_LIKE and pr2.Y is not None:
        yk = pr2.ygeom()
    TQ, GQ = [], []                                 # tee / green spot per hole (local yd), None: no end
    for i, (t, g) in enumerate(holes):
        v = virt.get(i) or {}
        if (t < 0 and "tee" not in v) or (g < 0 and "green" not in v):
            TQ.append(None)
            GQ.append(None)
            continue
        gq = co["G"][g] if g >= 0 else np.asarray(v["green"])
        if t >= 0:
            tc = co["T"][t]
            far = int(np.argmax(np.hypot(*(np.asarray(tc["pts"]) - gq).T)))
            if version in V1_LIKE and tee_box != "far" and g >= 0 and pr2.Y is not None and len(tc["pts"]) > 1 \
                    and geo["Pbox"][t][g] is not None:
                yk = pr2.Y[0] if tee_box == "long" else pr2.ygeom()     # the box whose play length fits the card
                far = int(np.argmin(np.abs(np.asarray(geo["Pbox"][t][g]) - yk[i])))
                if d.get("_maps") is not None and pp.get("box_fair", 0) > 0:
                    # a complex holding two holes' boxes: the box whose line to the green runs down a fairway
                    import route_learn as RL
                    pts = np.asarray(tc["pts"], float)
                    fr = RL.line_stats(d["_maps"], pts, np.broadcast_to(np.asarray(gq, float), pts.shape),
                                       0.15, 0.85, 25)["fr_mean"]
                    cr = np.abs(np.asarray(geo["Pbox"][t][g]) - yk[i]) / max(float(yk[i]), 1.0)
                    far = int(np.argmin(pp.get("box_card", 2.0) * cr + pp["box_fair"] * (1.0 - fr)))
            TQ.append(tc["pts"][far])
        else:
            TQ.append(np.asarray(v["tee"]))
        GQ.append(gq)
    tee_info = None
    if version == "v2" and pr2.Y is not None:
        import route_tee as RT
        if tee_fix is not None:                     # the bench's out-of-fold tee choices
            TQ = [tuple(tee_fix[str(i)]) if str(i) in tee_fix and TQ[i] is not None else TQ[i]
                  for i in range(len(TQ))]
            tee_info = dict(fixed=True)
        elif tee_dump is not None or (tee_rr and RT.enabled()):
            cs = RT.candidates(d, pr2, holes, TQ, GQ)
            if tee_dump is not None:
                tee_dump.append(cs)
            if tee_rr and RT.enabled():
                TQ, tee_info = RT.refine(d, pr2, holes, TQ, GQ, cands=cs)
    for i, (t, g) in enumerate(holes):
        if TQ[i] is None:
            nv += 1
            n_miss += 1
            continue
        tq, gq = TQ[i], GQ[i]
        if t < 0:
            n_vt += 1
        if g < 0:
            n_vg += 1
        path = RJ._line(F, co, tq, gq)
        line = [[round(x, 7) for x in co["pj"].inv(*q)] for q in path]
        L = float(geo["P"][t, g]) if (t >= 0 and g >= 0) else float(np.hypot(*(np.asarray(tq) - np.asarray(gq))))
        par = pars[i % len(pars)] if pars else (3 if L < 245 else 4 if L < 470 else 5)
        src = dict(green=co["Gsrc"][g] if g >= 0 else "virtual", tee=co["T"][t]["src"] if t >= 0 else "virtual")
        if g >= 0:
            used.append(co["Gid"][g])
        if t >= 0:
            used.append(co["T"][t]["id"].split("/")[0])
        if "scene" in src.values() or "virtual" in src.values():
            det.append(str(i + 1))
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": line},
                      "properties": {"golf": "hole", "ref": str(i + 1), "par": str(par), "src": "joint:scene",
                                     "green_src": src["green"], "tee_src": src["tee"],
                                     "margin": round(float(mg[i]), 2)}})
        if version in V1_LIKE:
            Lp = float(np.sum(np.hypot(*np.diff(np.asarray(path, float), axis=0).T)))
            c = sol["seq"][i]
            hole_f.append(dict(ref=str(i + 1), margin=round(float(mg[i]), 3), kind=int(pr2.typ[c]),
                               card_rel=round(abs(Lp - float(yk[i])) / max(float(yk[i]), 1.0), 4) if yk is not None else None,
                               ob=round(float(pr2.ob_real[c]), 3) if c < pr2.real else None,
                               ph=round(float(pr2.ph.get((t, g), 0.0)), 4) if (t >= 0 and g >= 0) else None,
                               cross=int(sum(pr2.X[c, c2] for c2 in sol["seq"] if c2 < pr2.real)) if c < pr2.real else 0,
                               pw=_walk_p(d, holes, i, pr2.loop), **_obj_f(d, t, g)))
            if rr_info and rr_info.get("switched"):
                hole_f[-1]["rr"] = int(i in rr_info["changed"])
    if version not in V1_LIKE:
        n_vt = sum(1 for t, g in holes if t < 0 and g >= 0)
    return dict(features=feats, min_margin=float(min(mg)) if len(mg) else 0.0, margins=[round(float(m), 2) for m in mg],
                n_virtual=nv if version not in V1_LIKE else n_vt + n_vg + n_miss, n_vt=n_vt, n_vg=n_vg, n_miss=n_miss,
                n_holes=int(n_holes), greens=len(co["G"]), tee_complexes=len(co["T"]), version=version,
                cost=float(sol["cost"]), rerank=rr_info if version in V1_LIKE else None,
                tee_refine=tee_info if version in V1_LIKE else None, detected_holes=det, _used=used, hole_features=hole_f, alts=alts,
                has_card=bool(S.card_sets(card, int(n_holes)) is not None), **info)


def _obj_f(d, t, g):
    """detector attributes of the hole's green / tee complex (route_learn.obj_attrs, v2): p, green from the map"""
    ga, ta = d.get("_gattr"), d.get("_tattr")
    out = {}
    if ga is not None and g >= 0:
        out.update(gp=_r(ga[g][0]), garea=_r(ga[g][1]), gmap=int(ga[g][2] > 0))
    if ta is not None and t >= 0:
        out.update(tp=_r(ta[t][0]), tbox=int(ta[t][1]))
    return out


def _r(v):
    v = float(v)
    return None if v != v else round(v, 3)


def _walk_p(d, holes, i, loop):
    """walk-model probability of the walk into hole i (previous green -> this tee), None at a loop start or when
    either end is virtual"""
    if i % loop == 0 or i == 0:
        return None
    gp, t = holes[i - 1][1], holes[i][0]
    if gp < 0 or t < 0:
        return None
    if "_pw" not in d:
        d["_pw"] = {(int(a), int(b)): float(p) for (a, b), p in zip(d["wp"], d["sc"]["pw"])}
    return round(d["_pw"].get((int(gp), int(t)), 0.0), 4)


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


V2_PARAMS = dict(c_vt=3.0, c_vg=4.0, tee_box="geom", w_x=3.0, w_s=0.75, refine=1)   # route_bench tune on train (v2 scores)


def route_v2(fc, scene, card, n_holes, P, hag=None, params=None):
    """v2: greens the U-Net P(green) map holds but the scene dropped are added (route_learn.augment_scene), hole /
    walk scores from route_learn's models (real-candidate fit, fairway / turf / tree features along each line),
    solve2 with V2_PARAMS. -> (route result, candidate info, the augmented scene)"""
    import route_learn as RL
    scene, n_aug = RL.augment_scene(scene, P)
    co, ci = candidates(fc, scene, n_holes=n_holes)
    d, _ = prepare(fc, scene, card, n_holes, co=co, version="v2")
    M = RL.corridor_maps(P, scene["grid"], hag=hag).bind(co["pj"])
    learned = RL.rescore(d, scene, M, card, n_holes)
    if learned and (params or {}).get("map_fair", V2_PARAMS.get("map_fair")):
        d["co"]["maps"] = M
    r = route(fc, scene, card, n_holes, version="v2" if learned else "v1",
              params=dict(V2_PARAMS, **(params or {})) if learned else params, prepared=(d, {}))
    ci = dict(ci, greens_map=n_aug, learned_scores=learned)
    return r, ci, scene


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
    P = info.get("P")
    if ROUTER == "v2" and P is not None and np.shape(P)[0] == 6:
        r, ci, scene = route_v2(fc, scene, card, n_holes, P, getattr(info.get("stack"), "a", {}).get("hag"))
    else:
        co, ci = candidates(fc, scene, n_holes=n_holes)
        r = route(fc, scene, card, n_holes, co=co, version="v1" if ROUTER == "v2" else ROUTER)
    r.update(ci)
    try:                                         # web cards that disagree on the hole order (route_gate blocks)
        import json as _json
        import route_gate
        web = _json.load(open(os.path.join(pkg_dir, "raw", "scorecard_web.json")))
        r["card_conflict"] = route_gate.card_order_conflict(card, [c["card"] for c in web.get("cards", [])
                                                                   if c.get("card")], int(n_holes))
    except Exception:                                                # noqa: BLE001
        r["card_conflict"] = False
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


def confirm_questions(package, routed):
    """golf_confirm_scene/1: one question per hole whose tee or green came from the detector, the least certain
    first (the joint solver's per-hole min-marginal): "is this hole N's tee / green?" with the points to show. A
    "no" goes back to the router as an exclusion (not wired yet: the app's tap flow uses confirm.json's session)."""
    mg = routed.get("margins") or []
    det = set(routed.get("detected_holes") or [])
    qs = []
    for ref, h in (package.get("holes") or {}).items():
        if str(ref) not in det:
            continue
        i = int(ref) - 1
        qs.append(dict(hole=str(ref), margin=mg[i] if 0 <= i < len(mg) else None, tee_ll=h.get("tee_ll"),
                       green_ll=h.get("green_ll"), par=h.get("par"), card_yards=h.get("length"),
                       measured_yards=h.get("measured_length"),
                       ask=f"Is this hole {ref}: tee here, green there ({h.get('length')} yds on the card)?"))
    qs.sort(key=lambda q: (q["margin"] is None, q["margin"] if q["margin"] is not None else 0))
    return dict(schema="golf_confirm_scene/1", min_margin=routed.get("min_margin"), questions=qs,
                note="greens / tees from the fast-path perception scene (fastscene.py); OSM objects need no question")
