"""Hole lines for a course OSM does not map well enough to route (tiers C / D): OSM greens / tee boxes / fairways
where OSM has them, plus the fast-path perception scene's (fastscene.py) where it does not, routed by the same
joint solver as route_joint.py (zero_tap/joint, card-aware, tee_reuse) and written as golf=hole ways.

    co, info = candidates(fc, scene)         # zero_tap/joint Course: OSM first, scene detections that add to it
    r = route(fc, scene, card, n_holes)      # route_joint.route's result + per-hole sources

A detection enters only with its probability >= P_GREEN / detector.route_p_tee(), and never within MERGE_YD of an OSM object of the
same kind (OSM wins). The joint models were fitted on OSM candidates (p 0.9 each), so every kept candidate gets
p 0.9 too: the detector's probability only decides whether it is a candidate. Gate (fast.py): a course routed on
detections is shown only with min margin >= route_joint.MIN_MARGIN and no virtual hole, like route_joint; every
hole whose green or tee came from the detector carries a confirm flag.
"""
from __future__ import annotations

import math
import os

import numpy as np

import detector as _DET
import route_joint as RJ

P_GREEN = 0.35
P_TEE = 0.3        # v1 fits; the cutoff in use is detector.route_p_tee() (per U-Net, env ROUTE_P_TEE overrides)
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


def candidates(fc, scene, p_green=P_GREEN, p_tee=None, n_holes=18, split_tees=None):
    C, F, M, S = _mods()
    p_tee = _DET.route_p_tee() if p_tee is None else p_tee
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
    pads = [t for t in st if t.get("kind") == "pad"]     # DEM pads (opt-in): after the split halves, so they never
    st = [t for t in st if t.get("kind") != "pad"]       # take a real complex's half out of the MAX_CAND budget
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
    for t in pads:
        if len(co["T"]) >= MAX_CAND:
            break
        bp = [C._xy(pj, b["centroid"]) for b in t.get("boxes", []) if b.get("centroid")] or [C._xy(pj, t["centroid"])]
        c = tuple(np.mean(bp, 0))
        if osm_tc and min(math.hypot(c[0] - a, c[1] - b) for a, b in osm_tc) < MERGE_YD:
            continue
        co["T"].append(dict(c=c, pts=bp, id="scene:" + t["id"], ax=_axis(bp), p=0.9, src="scene"))
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
    pt = (fc or {}).get("course_point") if os.environ.get("ROUTE_CLUB_POINT", "0") == "1" else None
    C._pick_club(co, park + sp, club, C._xy(pj, pt) if pt else None)
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


# Fallback for a routing that would be hard-blocked by its own doing (fast.extra_gate): two holes whose greens are
# within SHARED_YD of each other (the solver uses each green candidate once, but two candidates can be one green,
# or a virtual green can snap onto a real one in the package build). The replacement is the complete routing without
# a shared green that changes the fewest holes (then the lowest solver cost) among the re-ranker's alternatives (the
# routing before the re-ranker, the beams, renumberings, start / end re-solves, also around the blocked routing) and
# re-solves with one green of each offending pair excluded; its changed holes and the holes of the
# blocked pair are marked approximate (route_gate). A routing without a shared green is never touched.
# ROUTE_SHARED_FALLBACK=0 turns it off. (The other routing-side hard blocks: card-order conflict reads the web cards
# only; a missing hole is a candidate the solver could not fill, which no alternative here fixes.)
SHARED_YD = 15.0                   # = fast.GATE_SHARED_GREEN_YD
SHARED_FALLBACK = os.environ.get("ROUTE_SHARED_FALLBACK", "1") == "1"
SHARED_ORDER = os.environ.get("ROUTE_SHARED_ORDER", "ham")      # fewest changed holes first, then cost ("cost": cost only)


SNAP_YD = 40.0                     # geometry/build_holes.find_green: a line end snaps to a green this close


def _green_spots(S2, sol, d, pp, co):
    """per hole the green the package build will give it (local yd), None for a hole without a line. A virtual
    green end snaps to the nearest green the package holds (OSM greens + the scene greens this routing uses) within
    SNAP_YD of its edge, as build_holes.find_green does (edge approximated by centre distance - radius)."""
    virt = S2.place_virtual(sol)
    if pp.get("refine") and d.get("_maps") is not None:
        virt = S2.refine_virtual(sol, virt, d["_maps"], pp.get("refine_params"))
    world = [j for j, src in enumerate(co["Gsrc"]) if src != "scene"] + \
        [int(g) for k, t, g in sol["holes"] if g >= 0 and co["Gsrc"][g] == "scene"]
    out = []
    for i, (k, t, g) in enumerate(sol["holes"]):
        v = virt.get(i) or {}
        if (t < 0 and "tee" not in v) or (g < 0 and "green" not in v):
            out.append(None)
            continue
        if g < 0:
            q = np.asarray(v["green"], float)
            ed = [(max(0.0, float(np.hypot(*(q - np.asarray(co["G"][j], float)))) - float(co["Gr"][j])), j)
                  for j in world]
            if ed and min(ed)[0] < SNAP_YD:
                g = min(ed)[1]
        out.append(np.asarray(co["G"][g], float) if g >= 0 else np.asarray(v["green"], float))
    return out


def _shared_pairs(S2, sol, d, pp, co):
    G = _green_spots(S2, sol, d, pp, co)
    return [(i, j) for i in range(len(G)) for j in range(i + 1, len(G))
            if G[i] is not None and G[j] is not None and float(np.hypot(*(G[i] - G[j]))) <= SHARED_YD]


def _shared_fallback(S2, sol, d, pp, co, seq0=None):
    """-> (sol, info): sol unchanged unless its routing has a shared green and a complete alternative without one
    exists. info None when there is no shared green."""
    pairs = _shared_pairs(S2, sol, d, pp, co)
    if not pairs:
        return sol, None
    import route_rerank as RR
    pr = sol["pr"]
    seq = [int(c) for c in sol["seq"]]
    n_miss = sum(pr.cand[c][0] == S2.MISS for c in seq)
    info = dict(pairs=[[i + 1, j + 1] for i, j in pairs], switched=False)
    alts = []
    if seq0 is not None and list(seq0) != seq:
        alts.append(("before_rerank", [int(c) for c in seq0]))
    try:                                     # the re-ranker's alternatives (around seq0) and those around seq
        rc = getattr(pr, "rr_cands", None)
        alts += [(k, s) for k, s in (rc or [])]
        if not rc or rc[0][1] != seq:
            alts += [(k, s) for k, s in RR.candidates(pr, seq)[1:]]
    except Exception:                                                # noqa: BLE001
        pass
    for i, j in pairs:                       # re-solve without one green of the pair (at that hole / everywhere)
        for h in (i, j):
            g = int(pr.cand[seq[h]][2])
            if g < 0:
                continue
            for fb in ({(h, "g", g)}, {(p, "g", g) for p in range(pr.N)}):
                try:
                    r = S2.search(pr, forbid=fb)
                except Exception:                                    # noqa: BLE001
                    r = None
                if r:
                    alts.append(("drop_green", [int(c) for c in r[0][1]]))
    pool = []
    seen = {tuple(seq)}
    for kind, s in alts:
        if len(s) != len(seq) or tuple(s) in seen or not RR.valid(pr, s):
            continue
        seen.add(tuple(s))
        if sum(pr.cand[c][0] == S2.MISS for c in s) > n_miss:
            continue
        ham = sum(pr.cand[a][1:] != pr.cand[b][1:] for a, b in zip(seq, s))
        cost = float(RR.cost_parts(pr, s)["total"])
        pool.append(((ham, cost) if SHARED_ORDER == "ham" else (cost,), len(pool), cost, kind, s))
    info["n_alts"] = len(pool)
    best = None
    for _, _, cost, kind, s in sorted(pool):       # the cheapest one without a shared green
        if not _shared_pairs(S2, dict(sol, seq=s, holes=[pr.cand[c] for c in s]), d, pp, co):
            best = (cost, kind, s)
            break
    if best is None:
        return sol, info
    cost, kind, s = best
    changed = [i for i, (a, b) in enumerate(zip(seq, s)) if pr.cand[a][1:] != pr.cand[b][1:]]
    info.update(switched=True, kind=kind, cost=round(cost, 3), changed=changed,
                affected=sorted(set(changed) | {i for p in pairs for i in p}))
    return dict(sol, seq=s, holes=[pr.cand[c] for c in s], cost=cost, cost0=sol.get("cost0", sol["cost"])), info


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
        shared_fb = None
        if SHARED_FALLBACK:
            sol, shared_fb = _shared_fallback(S2, sol, d, pp, co, seq0=list(seq0) if (fix_seq is not None or rr) else None)
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
            moved = set((shared_fb or {}).get("changed") or [])     # made for the routing the fallback replaced
            TQ = [tuple(tee_fix[str(i)]) if str(i) in tee_fix and TQ[i] is not None and i not in moved else TQ[i]
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
            if shared_fb and shared_fb.get("switched") and i in shared_fb["affected"]:
                hole_f[-1]["fallback"] = 1          # route_gate caps its P below APPROX_P: marked approximate
    if version not in V1_LIKE:
        n_vt = sum(1 for t, g in holes if t < 0 and g >= 0)
    return dict(features=feats, min_margin=float(min(mg)) if len(mg) else 0.0, margins=[round(float(m), 2) for m in mg],
                n_virtual=nv if version not in V1_LIKE else n_vt + n_vg + n_miss, n_vt=n_vt, n_vg=n_vg, n_miss=n_miss,
                n_holes=int(n_holes), greens=len(co["G"]), tee_complexes=len(co["T"]), version=version,
                cost=float(sol["cost"]), rerank=rr_info if version in V1_LIKE else None,
                tee_refine=tee_info if version in V1_LIKE else None,
                shared_fallback=shared_fb if version in V1_LIKE else None, detected_holes=det, _used=used, hole_features=hole_f, alts=alts,
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
            if used is None and float(t.get("p", 0)) < _DET.route_p_tee():
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


# 9-hole course with an 18-hole card (NOTES_ROUTING.md 2026-11-20 "n = 9"): many 9-hole cards list the nine twice
# (holes 10-18 = 1-9 from other tees). When the back nine's yardages are within NINE_DUP_TOL of the front nine's
# (median over the holes, the set that matches best) and the scene holds at most NINE_MAX_GREENS candidate greens,
# the course is routed as 9 holes on the front nine's yardages and delivered as a 9-hole course on the front-nine card
# (fast.py writes it as raw/scene_card.json); holes 10-18 are not built.
# ROUTE_NINE_DUP=0 turns it off.
NINE_DUP_TOL = float(os.environ.get("ROUTE_NINE_DUP_TOL", "0.05"))
NINE_MAX_GREENS = int(os.environ.get("ROUTE_NINE_MAX_GREENS", "12"))


def nine_dup(card):
    """median per-hole |front - back| / max over the card's complete 18-hole sets (the best set), None without one"""
    best = None
    for t in ((card or {}).get("tee_sets") or {}).values():
        y = t.get("yards") if isinstance(t, dict) else None
        if not isinstance(y, list) or len(y) != 18 or \
                not all(isinstance(v, (int, float)) and np.isfinite(v) and v > 0 for v in y):
            continue                             # malformed or incomplete set: no evidence either way
        d = float(np.median([abs(a - b) / max(a, b) for a, b in zip(y[:9], y[9:])]))
        best = d if best is None else min(best, d)
    return best


def route_n(card, scene, n):
    """the number of holes to route: 9 for an 18-hole card that repeats its nine on a scene with few greens, else n"""
    if os.environ.get("ROUTE_NINE_DUP", "1") == "0" or int(n) != 18:
        return int(n)
    d = nine_dup(card)
    if d is None or d > NINE_DUP_TOL:
        return int(n)
    ng = sum(1 for g in (scene or {}).get("greens") or [] if g.get("kind") != "practice"
             and float(g.get("p_hole", g.get("p", 0))) >= P_GREEN)
    return 9 if ng <= NINE_MAX_GREENS else int(n)


def front_nine(card):
    """the card cut to its first nine holes (every tee set, par / handicap rows), marked nine_of=18"""
    import copy
    c = copy.deepcopy(card)
    for k in ("par", "handicap"):
        if isinstance(c.get(k), list) and len(c[k]) == 18:
            c[k] = c[k][:9]
    for t in (c.get("tee_sets") or {}).values():
        if not isinstance(t, dict):
            continue
        for k in ("yards", "par", "handicap"):
            if isinstance(t.get(k), list) and len(t[k]) == 18:
                t[k] = t[k][:9]
        if t.get("yards"):
            t["total"] = int(sum(v or 0 for v in t["yards"]))
            t.pop("total_stated", None)
        for k in ("rating", "slope", "par_total", "course_rating", "slope_rating", "bogey_rating"):
            t.pop(k, None)                       # 18-hole aggregates: no nine-hole value can be derived from them
        par = t.get("par") if isinstance(t.get("par"), list) else c.get("par")
        if isinstance(par, list) and len(par) == 9:
            t["par_total"] = int(sum(v or 0 for v in par))
    if isinstance(c.get("facility"), dict):
        c["facility"] = dict(c["facility"], numberOfHoles=9)
    c["nine_of"] = 18
    return c


def needs_perception(fc, n_holes):
    """True when OSM does not draw the holes: < 3 hole lines (tiers C / D). Since the pair_keeposm bench (600
    courses, OSM greens and tees given, lines hidden: scene router 89.4 % of holes right, route_joint 80.8 %) that
    includes courses with every green and tee mapped; route_joint keeps OSM's own unnumbered lines, and is the
    fallback when the scene routing fails."""
    lines = green = tee = 0
    for f in (fc or {}).get("features", []):
        p = f.get("properties") or {}
        if p.get("inside_course") is False:
            continue
        g = p.get("golf")
        lines += g == "hole" and (f.get("geometry") or {}).get("type") == "LineString"
        green += g == "green"
        tee += g == "tee"
    return lines < 3


V2_PARAMS = dict(c_vt=3.0, c_vg=4.0, tee_box="geom", w_x=3.0, w_s=0.75, refine=1)   # route_bench tune on train (v2 scores)


def route_v2(fc, scene, card, n_holes, P, hag=None, params=None):
    """v2: greens the U-Net P(green) map holds but the scene dropped are added (route_learn.augment_scene), hole /
    walk scores from route_learn's models (real-candidate fit, fairway / turf / tree features along each line),
    solve2 with V2_PARAMS. -> (route result, candidate info, the augmented scene)"""
    import route_learn as RL
    scene0 = scene
    scene, n_aug = RL.augment_scene(scene, P, n_holes=n_holes)
    r, ci = _route_v2_on(fc, scene, card, n_holes, P, hag, params)
    ci = dict(ci, greens_map=n_aug)
    ms = _multi_site(fc, scene0, scene, card, n_holes, P, hag, params)
    if ms is not None:
        r, ci2, scene = ms
        ci = dict(ci2, greens_map=n_aug)
    return r, ci, scene


def _route_v2_on(fc, scene, card, n_holes, P, hag=None, params=None):
    """route_v2 on an already augmented scene -> (route result, candidate info)"""
    import route_learn as RL
    co, ci = candidates(fc, scene, n_holes=n_holes)
    d, _ = prepare(fc, scene, card, n_holes, co=co, version="v2")
    M = RL.corridor_maps(P, scene["grid"], hag=hag).bind(co["pj"])
    learned = RL.rescore(d, scene, M, card, n_holes)
    if learned and (params or {}).get("map_fair", V2_PARAMS.get("map_fair")):
        d["co"]["maps"] = M
    r = route(fc, scene, card, n_holes, version="v2" if learned else "v1",
              params=dict(V2_PARAMS, **(params or {})) if learned else params, prepared=(d, {}))
    return r, dict(ci, learned_scores=learned)


# 27 / 36-hole sites (NOTES_ROUTING.md 2026-11-20 "27 / 36-hole sites"): on a scene with >= MULTI_GREENS x n candidate
# greens (the raw scene) the router can mix the courses of a site. The candidates are split by k-means on the green
# centroids (k = 2, 3; tee complexes and every green go to the nearest centre); each cluster holding >= 0.9 n of the
# candidate greens is routed alone, and the cluster routing with the lowest solver cost (re-ranker off for the
# comparison) replaces the whole-scene routing when it is cheaper than the whole scene's. ROUTE_MULTI_SITE=0 turns it off.
# Only scene objects are clustered: OSM greens / tees in fc (tier C / D courses with a few mapped objects) stay in every
# cluster and are not counted by the trigger; scene objects without a centroid are left out of every cluster.
MULTI_GREENS = float(os.environ.get("ROUTE_MULTI_GREENS", "1.5"))


def _n_cand_greens(scene):
    return sum(1 for g in (scene or {}).get("greens") or [] if g.get("kind") != "practice"
               and float(g.get("p_hole", g.get("p", 0))) >= P_GREEN)


def cluster_scenes(scene, n_holes, ks=(2, 3)):
    """[(k, j, scene restricted to cluster j)] for the k-means clusters holding >= 0.9 n candidate greens"""
    from sklearn.cluster import KMeans
    G = [g for g in scene.get("greens") or [] if g.get("kind") != "practice" and g.get("centroid")
         and float(g.get("p_hole", g.get("p", 0))) >= P_GREEN]
    if len(G) < 2 * 0.9 * n_holes:
        return []
    lat0 = float(np.mean([g["centroid"][1] for g in G]))
    kx = math.cos(math.radians(lat0)) * 111320.0

    def xy(ll):
        return np.array([ll[0] * kx, ll[1] * 110950.0])
    Z = np.array([xy(g["centroid"]) for g in G])
    out = []
    for k in ks:
        C = KMeans(k, n_init=10, random_state=0).fit(Z).cluster_centers_

        def lab(ll):
            return int(np.argmin(np.hypot(*(C - xy(ll)).T)))
        for j in range(k):
            keepg = [g for g in scene.get("greens") or [] if g.get("centroid") and lab(g["centroid"]) == j]
            if sum(1 for g in keepg if any(g is h for h in G)) < 0.9 * n_holes:
                continue
            keept = [t for t in scene.get("tee_complexes") or [] if t.get("centroid") and lab(t["centroid"]) == j]
            out.append((k, j, dict(scene, greens=keepg, tee_complexes=keept)))
    return out


def _multi_site(fc, scene0, scene, card, n_holes, P, hag, params):
    """-> (route result, candidate info, cluster scene) when a cluster routing is cheaper, else None"""
    if os.environ.get("ROUTE_MULTI_SITE", "1") == "0" or _n_cand_greens(scene0) < MULTI_GREENS * int(n_holes):
        return None
    cmp_p = dict(params or {}, rerank=0, tee=0, alts=0, no_margins=True)
    try:
        full, _ = _route_v2_on(fc, scene, card, n_holes, P, hag, cmp_p)
        best = None
        for k, j, sc in cluster_scenes(scene, int(n_holes)):
            rr, _ = _route_v2_on(fc, sc, card, n_holes, P, hag, cmp_p)
            if rr.get("cost") is not None and (best is None or rr["cost"] < best[0]):
                best = (float(rr["cost"]), k, j, sc)
        if best is None or full.get("cost") is None or not best[0] < float(full["cost"]):
            return None
        r, ci = _route_v2_on(fc, best[3], card, n_holes, P, hag, params)
        if not r.get("features"):
            return None
        r["multi_site"] = dict(k=best[1], cluster=best[2], cost=round(best[0], 3), cost_full=round(float(full["cost"]), 3))
        return r, ci, best[3]
    except Exception:                                                # noqa: BLE001
        return None                                                  # the whole-scene routing stands


# Card selection (NOTES_ROUTING.md 2026-11-20 "card selection"): the web cards can disagree (a card of the sister
# course on a 27 / 36-hole site, a stale or misnumbered card). When another web card's yardages differ materially from
# the chosen one, the course is routed with it as well, and the card the routed holes fit best (median relative
# residual of the hole line lengths to the card's best tee set) replaces the chosen card when it fits better by more
# than CARD_SELECT_MARGIN. Only here (tiers C / D, routed on detections); an explicit request card is never replaced.
# Opt-in (ROUTE_CARD_SELECT=1): on the strict out-of-fold bench never-used 200 lost holes (the switched courses lose
# their out-of-fold re-ranker / tee picks there), so it is not the default.
CARD_SELECT_MARGIN = float(os.environ.get("ROUTE_CARD_SELECT_MARGIN", "0.01"))
CARD_DIFFER = 0.01


def card_select_on():
    return os.environ.get("ROUTE_CARD_SELECT", "0") == "1"


def card_fit(feats, card, n):
    """median relative |line length - card yards| of the routed holes, for the card's best tee set (None: no fit)"""
    if not card or not feats:
        return None
    L = {}
    for f in feats:
        a = np.asarray(f["geometry"]["coordinates"], float)
        k = math.cos(math.radians(float(a[:, 1].mean())))
        L[int(f["properties"]["ref"])] = float(np.hypot(np.diff(a[:, 0]) * k, np.diff(a[:, 1])).sum() * 111320.0 / 0.9144)
    best = None
    for s in (card.get("tee_sets") or {}).values():
        y = list(s.get("yards") or [])
        if y and len(y) < n and n % len(y) == 0:
            y = y * (n // len(y))
        rr = [abs(L[i] - y[i - 1]) / max(float(y[i - 1]), 1.0) for i in L if i - 1 < len(y) and y[i - 1]]
        if rr:
            m = float(np.median(rr))
            best = m if best is None or m < best else best
    return best


def cards_differ(a, b, n, tol=CARD_DIFFER):
    """the two cards' closest tee sets differ by more than tol (median relative per hole)"""
    C, F, M, S = _mods()
    A, B = S.card_sets(a, n), S.card_sets(b, n)
    if A is None or B is None:
        return False
    return min(float(np.median(np.abs(x - y) / np.maximum(y, 1))) for x in A for y in B) > tol


def run(pkg_dir, fc, card, n_holes, log=None, card_select=True):
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
    nine = None
    if card_select and card and route_n(card, scene, n_holes) != int(n_holes):   # 9 holes, 18-hole card repeating them
        nine = card = front_nine(card)
        n_holes = 9
    P = info.get("P")
    if ROUTER == "v2" and P is not None and np.shape(P)[0] == 6:
        hag = getattr(info.get("stack"), "a", {}).get("hag")
        import route_learn as RL
        if (RL.tee_pads_on() or RL.tee_pads_cond(scene, n_holes)) and scene.get("grid"):   # DEM pads, off the package DEM
            try:
                scene = dict(scene, dem_pads=RL.dem_pads_file(os.path.join(pkg_dir, "imagery", "dem.tif"), scene["grid"], P))
            except Exception:                                    # noqa: BLE001
                scene = dict(scene, dem_pads=[])
        scene0 = scene
        r, ci, scene = route_v2(fc, scene0, card, n_holes, P, hag)
        if card_select and card_select_on() and card:
            r, ci, scene = _card_select(pkg_dir, fc, scene0, card, n_holes, P, hag, (r, ci, scene))
    else:
        co, ci = candidates(fc, scene, n_holes=n_holes)
        r = route(fc, scene, card, n_holes, co=co, version="v1" if ROUTER == "v2" else ROUTER)
    if ROUTER == "v2" and P is not None and np.shape(P)[0] == 6:
        r, ci, scene = _ensemble(pkg_dir, fc, card, n_holes, r, ci, scene)
    r.update(ci)
    if nine is not None:
        r["nine_card"] = nine
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
    if os.environ.get("SCENE_ALL_TEES", "1") != "0":
        # tee boxes the routing did not start a hole from, too: a routed line often starts at a forward tee, and the
        # tee stage can only put the back sets on a box it is given (Lake of the Woods 1, 2026-11-26: the Blue tee
        # walked 112 yds back along the line to a spot 30 yds from a detected box the supplement had left out)
        have_t = {f["properties"].get("id") for f in sup if f["properties"].get("golf") == "tee"}
        sup += [f for f in scene_features(scene, ("tee",)) if f["properties"].get("id") not in have_t]
    sup += scene_features(scene, tuple(kinds))
    for f in sup:
        f["properties"]["origin"] = "fastscene"
    T["total"] = round(time.time() - t, 2)
    return {k: v for k, v in r.items() if k != "features"}, sup, T


def _ensemble(pkg_dir, fc, card, n_holes, r, ci, scene):
    """route_conf (NOTES_ROUTING.md 2026-11-26): the course is routed a second time on the scene of the other detector
    (golfseg_own_v3; same routing fits and card), route_conf's model scores every hole of both routings from their
    agreement and the routing with more predicted right holes is kept. r['ensemble'] = dict(use 'a' | 'b', p {ref:
    P(hole right)} of the kept routing, sum_a, sum_b, agree, seconds). The second scene failing leaves the first
    routing with the single-routing model's p. ROUTE_ENSEMBLE=0 turns it off (route_gate's p)."""
    import time
    import route_conf as RC
    if not RC.on() or not any((f.get("properties") or {}).get("golf") == "hole" for f in r.get("features") or []):
        return r, ci, scene
    t = time.time()
    cs = (r.get("card_select") or {})
    card = cs.get("card") if cs.get("switched") and cs.get("card") else card
    try:
        a = RC.record(r, card, n_holes)
    except Exception as e:                                           # noqa: BLE001
        r["ensemble"] = dict(use="a", error=f"{type(e).__name__}: {e}"[:200])
        return r, ci, scene
    keep = {k: os.environ.get(k) for k in ("FASTSCENE_UNET",)}
    try:
        import fastscene as FS
        import route_learn as RL
        os.environ["FASTSCENE_UNET"] = RC.SECOND_UNET
        scene_b, info = FS.build(pkg_dir, out=False)
        Pb = info.get("P")
        hag = getattr(info.get("stack"), "a", {}).get("hag")
        if (RL.tee_pads_on() or RL.tee_pads_cond(scene_b, n_holes)) and scene_b.get("grid"):
            try:
                scene_b = dict(scene_b, dem_pads=RL.dem_pads_file(os.path.join(pkg_dir, "imagery", "dem.tif"), scene_b["grid"], Pb))
            except Exception:                                        # noqa: BLE001
                scene_b = dict(scene_b, dem_pads=[])
        rb, cib, scene_b2 = route_v2(fc, scene_b, card, n_holes, Pb, hag)
        b = RC.record(rb, card, n_holes)
        pk = RC.pick(a, b)
    except Exception as e:                                           # noqa: BLE001  (the first routing stays)
        try:
            p = RC.score(a)
        except Exception:                                            # noqa: BLE001
            p = None
        r["ensemble"] = dict(use="a", p=p, model="single", error=f"{type(e).__name__}: {e}"[:200],
                             seconds=round(time.time() - t, 1))
        return r, ci, scene
    finally:
        for k, v in keep.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
    pk.update(model="pair", second=os.path.basename(os.path.dirname(RC.SECOND_UNET)), seconds=round(time.time() - t, 1),
              right_a=None, right_b=None)
    try:                                 # verified holes: P(identity) >= VERIFY_P and a second card source agrees
        import json as _json
        web = _json.load(open(os.path.join(pkg_dir, "raw", "scorecard_web.json"))).get("cards") or []
    except Exception:                                                # noqa: BLE001
        web = []
    try:
        pk["verified"], pk["card_corroborated"] = RC.verified(pk, card, web)
    except Exception as e:                                           # noqa: BLE001
        pk["verified"], pk["verify_error"] = [], f"{type(e).__name__}: {e}"[:200]
    if pk["use"] == "b":
        for k in ("card_select",):                                   # the card choice was made on the first routing
            if k in r:
                rb[k] = r[k]
        rb["ensemble"] = pk
        try:                                                         # the package's scene is the kept routing's
            import json as _json
            _json.dump(scene_b, open(os.path.join(pkg_dir, "scene.json"), "w"), separators=(",", ":"))
        except Exception:                                            # noqa: BLE001
            pass
        return rb, cib, scene_b2
    r["ensemble"] = pk
    return r, ci, scene


def _card_select(pkg_dir, fc, scene0, card, n_holes, P, hag, cur):
    """route with every other web card that differs materially; keep the card the routed holes fit best (by more
    than CARD_SELECT_MARGIN) -> (r, ci, scene); r['card_select'] records the choice (and the card when switched)"""
    import json as _json
    try:
        web = _json.load(open(os.path.join(pkg_dir, "raw", "scorecard_web.json")))
    except Exception:                                                # noqa: BLE001
        return cur
    try:
        import scorecard as scm
        norm = scm.normalise
    except Exception:                                                # noqa: BLE001
        norm = lambda c: c                                           # noqa: E731
    f0 = card_fit(cur[0].get("features"), card, n_holes)
    best, info = (f0, None), dict(fit_chosen=f0, tried=[])
    for c in web.get("cards") or []:
        alt = c.get("card")
        if not alt:
            continue
        try:
            alt = norm(alt)
            if not cards_differ(alt, card, n_holes):
                continue
            r2 = route_v2(fc, scene0, alt, n_holes, P, hag)
        except Exception:                                            # noqa: BLE001
            continue
        f2 = card_fit(r2[0].get("features"), alt, n_holes)
        info["tried"].append(dict(source=c.get("source"), fit=f2))
        if f2 is not None and (best[0] is None or f2 < best[0]):
            best = (f2, (c.get("source"), alt, r2))
    if best[1] is not None and (f0 is None or f0 - best[0] > CARD_SELECT_MARGIN):
        src, alt, r2 = best[1]
        r2[0]["card_select"] = dict(info, switched=True, source=src, fit=best[0], card=alt)
        return r2
    cur[0]["card_select"] = dict(info, switched=False)
    return cur


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
