"""Score a perceived scene (detector outputs in grid metres) against OSM truth (truth.Truth). Definitions are
repeated in REPORT.md. Every block carries `eligible` (whether this course's OSM mapping is complete enough
for that element to be scored) so pooled numbers only use courses where OSM is a fair reference."""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage as ndi

P_DET = 0.5
GREEN_MATCH_M = 6.0
TEE_START_M = 30.0
TEE_PREC_M = 25.0
PATH_TOL_M = 4.0
CONNECT_ATTACH_M = 45.0


def _poly(ring):
    from shapely.geometry import Polygon
    try:
        return Polygon(ring).buffer(0)
    except Exception:                                            # noqa: BLE001
        return None


def _prf(tp_p, n_p, tp_t, n_t):
    prec = tp_p / n_p if n_p else None
    rec = tp_t / n_t if n_t else None
    return dict(precision=None if prec is None else round(prec, 4), recall=None if rec is None else round(rec, 4),
                n_pred=n_p, n_true=n_t, tp_pred=tp_p, tp_true=tp_t)


def eval_class_overlap(st, T, pred_lab, keep_ids, truth_objs, min_area_m2=0.0, region=None):
    from rasterio import features
    import geo
    tl = np.zeros((st.H, st.W), np.int32)
    shapes = []
    for k, o in enumerate(truth_objs):
        p = _poly(o["ring"])
        if p is None or p.is_empty or p.area < min_area_m2:
            continue
        shapes.append((p, len(shapes) + 1))
    if shapes:
        tl = features.rasterize(shapes, out_shape=(st.H, st.W), transform=geo.affine(st), fill=0, dtype="int32")
    if region is not None:
        tl = np.where(region, tl, 0)
    present = np.unique(tl)
    present = present[present > 0]
    truth_mask = tl > 0
    union = np.isin(pred_lab, list(keep_ids)) if keep_ids else np.zeros_like(truth_mask)
    objs = ndi.find_objects(pred_lab)
    tp_p, n_p = 0, 0
    for i in keep_ids:
        sl = objs[i - 1] if i - 1 < len(objs) else None
        if sl is None:
            continue
        m = pred_lab[sl] == i
        if region is not None and not region[sl][m].mean() >= 0.5:
            continue
        n_p += 1
        if truth_mask[sl][m].mean() >= 0.3:
            tp_p += 1
    tp_t = 0
    if len(present):
        cov = np.asarray(ndi.mean(union.astype(np.float32), tl, present))
        tp_t = int((np.nan_to_num(cov) >= 0.3).sum())
    return _prf(tp_p, n_p, tp_t, len(present))


def evaluate(st, L, D, T):
    out = dict(slug=st.meta.get("slug"), state=st.meta.get("state") or (st.meta.get("course") or {}).get("state"),
               mapped_holes=T.mapped_holes, n_osm_greens=len(T.greens), n_osm_tees=len(T.tees))
    region = T.in_boundary_mask(pad_m=40)
    nh = T.mapped_holes
    # ---------------- greens
    gs = D["greens"]
    tg = [(g, _poly(g["ring"])) for g in T.greens]
    tg = [(g, p) for g, p in tg if p is not None and not p.is_empty]
    from shapely.geometry import Point

    def match_green(o):
        pt = Point(*o["xy"])
        best, bd = None, 1e9
        for g, p in tg:
            d = p.distance(pt)
            if d < bd:
                best, bd = g, d
        return best if bd <= GREEN_MATCH_M else None
    for o in gs:
        m = match_green(o)
        o["_truth"] = None if m is None else m["kind"]
        o["_truth_ref"] = None if m is None else m.get("ref")
    eligible = nh >= 9 and len(T.greens) >= 0.8 * nh
    det = [o for o in gs if o["p"] >= P_DET]
    any_tp = sum(1 for o in det if o["_truth"] is not None)
    found = set()
    for o in det:
        if o["_truth"] is not None:
            found.add(id(match_green(o)))
    out["greens_any"] = dict(_prf(any_tp, len(det), len(found), len(tg)), eligible=bool(len(T.greens) >= 9))
    # hole greens, practice excluded: predicted hole-kind vs truth hole greens
    ph = [o for o in gs if o["kind"] == "hole"]
    true_hole = [g for g, _ in tg if g["kind"] == "hole"]
    tp_p = sum(1 for o in ph if o["_truth"] == "hole")
    found_h = {id(match_green(o)) for o in ph if o["_truth"] == "hole"}
    conf = dict(practice_called_hole=sum(1 for o in ph if o["_truth"] == "practice"),
                practice_called_practice=sum(1 for o in gs if o["kind"] == "practice" and o["_truth"] == "practice"),
                hole_called_practice=sum(1 for o in gs if o["kind"] == "practice" and o["_truth"] == "hole"),
                practice_true=sum(1 for g, _ in tg if g["kind"] == "practice"),
                hole_uncertain=sum(1 for o in gs if o["kind"] == "uncertain" and o["_truth"] == "hole"))
    out["greens_hole"] = dict(_prf(tp_p, len(ph), len(found_h), len(true_hole)), eligible=bool(eligible), **conf)
    # ---------------- tee complexes
    cx = [c for c in D["complexes"] if c["p"] >= P_DET]
    starts = [h["start"] for h in T.holes]

    def cdist(c, p):
        pts = np.array([b["xy"] for b in c["boxes"]])
        return float(np.min(np.hypot(*(pts - np.array(p)).T)))
    rec_hits = sum(1 for s in starts if cx and min(cdist(c, s) for c in cx) <= TEE_START_M)
    tee_polys = [_poly(t["ring"]) for t in T.tees]
    tee_polys = [p for p in tee_polys if p is not None and not p.is_empty]
    elig_prec = len(T.tees) >= 1.5 * max(nh, 1) and nh >= 9

    def c_is_true(c):
        for b in c["boxes"]:
            pt = Point(*b["xy"])
            if any(p.distance(pt) <= TEE_PREC_M for p in tee_polys):
                return True
        return any(cdist(c, s) <= TEE_PREC_M for s in starts)
    for c in D["complexes"]:
        c["_truth"] = c_is_true(c) if (tee_polys or starts) else None
    tp_c = sum(1 for c in cx if c["_truth"])
    # complexes per hole start: one complex should explain one start (over-splitting shows as extra complexes)
    out["tee_complexes"] = dict(_prf(tp_c, len(cx), rec_hits, len(starts)), eligible=bool(nh >= 9), precision_eligible=bool(elig_prec),
                                n_complex_per_hole=round(len(cx) / nh, 2) if nh else None)
    boxes = [b for b in D["boxes"] if b["p"] >= P_DET]
    for b in D["boxes"]:
        pt = Point(*b["xy"])
        b["_truth"] = bool(any(p.distance(pt) <= 8.0 for p in tee_polys)) if tee_polys else None
    found_t = sum(1 for p in tee_polys if any(p.distance(Point(*b["xy"])) <= 8.0 for b in boxes))
    out["tee_boxes"] = dict(_prf(sum(1 for b in boxes if b["_truth"]), len(boxes), found_t, len(tee_polys)), eligible=bool(elig_prec))
    # ---------------- fairways / bunkers / water / buildings / parking (object overlap)
    fl = D["fairway_lab"]
    out["fairways"] = dict(eval_class_overlap(st, T, fl, [f["lab"] for f in D["fairways"]], T.fairways, 300, region),
                           eligible=bool(len(T.fairways) >= 0.6 * max(nh, 1) and nh >= 9))
    out["bunkers"] = dict(eval_class_overlap(st, T, D["bunker_lab"], [b["lab"] for b in D["bunkers"] if b["p"] >= P_DET],
                                             T.bunkers, 10, region), eligible=bool(len(T.bunkers) >= 10))
    out["water"] = dict(eval_class_overlap(st, T, D["water_lab"], [w["lab"] for w in D["water"]], T.water, 150, region),
                        eligible=bool(len(T.water) >= 1))
    out["buildings"] = dict(eval_class_overlap(st, T, D["building_lab"], [b["lab"] for b in D["buildings"] if b["p"] >= P_DET],
                                               T.buildings, 40, region), eligible=bool(len(T.buildings) >= 5))
    pk_ids = [p["lab"] for p in D["parking"] if p["p"] >= P_DET]
    out["parking"] = dict(eval_class_overlap(st, T, D["parking_lab"], pk_ids, T.parking, 200, region),
                          eligible=bool(len(T.parking) >= 1))
    for p in D["parking"]:
        m = D["parking_lab"] == p["lab"]
        tmask = T.raster("parking") if T.parking else None
        p["_truth"] = bool(tmask[m].mean() >= 0.3) if tmask is not None and m.any() else (None if not T.parking else False)
        if not p["_truth"] and T.parking_pts:
            if any(math.hypot(q[0] - p["xy"][0], q[1] - p["xy"][1]) < math.sqrt(p["area"]) for q in T.parking_pts):
                p["_truth"] = True
    # fairway axis vs the hole line through it; stripe orientation vs the same
    ax_err, st_err, st_err_all = [], [], []
    import truth as TR
    for f in D["fairways"]:
        if not T.holes or len(f["centerline"]) < 2:
            continue
        best = min(((TR.line_bearing_at(h["line"], np.array(f["xy"])), h) for h in T.holes), key=lambda t: t[0][1])
        (brg, d), h = best
        if d > 25 or brg is None:
            continue
        import geo
        ax_err.append(geo.angle_diff(f["axis"], brg % 180))
        if f["stripe"] is not None:
            st_err_all.append(geo.angle_diff(f["stripe"], brg % 180))
            if f["stripe_strength"] >= 0.15:
                st_err.append(geo.angle_diff(f["stripe"], brg % 180))
    out["fairway_axis"] = dict(n=len(ax_err), median_err_deg=_med(ax_err), within_20deg=_frac(ax_err, 20),
                               stripe_n=len(st_err_all), stripe_median_err_deg=_med(st_err_all),
                               stripe_strong_n=len(st_err), stripe_strong_median_err_deg=_med(st_err),
                               stripe_strong_within_20deg=_frac(st_err, 20))
    # ---------------- cart paths
    out["cart_paths"] = eval_paths(st, T, D["graph"], region)
    out["relations"] = eval_relations(T, D)
    # ---------------- clubhouse / range
    ch = D.get("clubhouse")
    if T.clubhouse is not None:
        out["clubhouse"] = dict(error_m=round(math.hypot(ch["xy"][0] - T.clubhouse[0], ch["xy"][1] - T.clubhouse[1]), 1) if ch else None,
                                truth=T.clubhouse_how, eligible=True)
    else:
        out["clubhouse"] = dict(error_m=None, truth=None, eligible=False)
    if T.ranges:
        r = D.get("range")
        hit = False
        if r:
            pr = _poly(r["ring"])
            hit = any(pr is not None and _poly(t["ring"]) is not None and pr.intersection(_poly(t["ring"])).area >= 0.25 * min(pr.area, _poly(t["ring"]).area)
                      for t in T.ranges)
        out["driving_range"] = dict(truth=len(T.ranges), predicted=bool(r), hit=bool(hit), eligible=True)
    else:
        out["driving_range"] = dict(truth=0, predicted=bool(D.get("range")), hit=None, eligible=False)
    return out


def _med(v):
    return round(float(np.median(v)), 1) if v else None


def _frac(v, t):
    return round(float(np.mean(np.array(v) <= t)), 3) if v else None


def eval_paths(st, T, G, region):
    """Length precision / recall within PATH_TOL_M inside the course (+40 m); connectivity of hole transitions."""
    from shapely.geometry import LineString, MultiLineString, Point
    from shapely.ops import unary_union
    true_len = T.cart_length_m(inside=True)
    nh = T.mapped_holes
    elig = true_len >= 1500.0 * max(nh, 9) / 18.0
    lines = [LineString(d["pts"]) for _, _, d in G.edges(data=True) if len(d["pts"]) >= 2]
    pred = unary_union(lines) if lines else MultiLineString()
    tl = [LineString(l) for l in T.cart_paths if len(l) >= 2]
    truth = unary_union(tl) if tl else MultiLineString()
    bnd = None
    if T.boundary:
        from shapely.geometry import Polygon
        bnd = unary_union([Polygon(r).buffer(40) for r in T.boundary if len(r) >= 3])
        pred = pred.intersection(bnd)
        truth = truth.intersection(bnd)
    pl, tl_ = pred.length, truth.length
    p_in = pred.intersection(truth.buffer(PATH_TOL_M)).length if pl and tl_ else 0.0
    t_in = truth.intersection(pred.buffer(PATH_TOL_M)).length if pl and tl_ else 0.0
    out = dict(pred_km=round(pl / 1000, 3), true_km=round(tl_ / 1000, 3),
               length_precision=round(p_in / pl, 4) if pl else None, length_recall=round(t_in / tl_, 4) if tl_ else None,
               eligible=bool(elig))
    # connectivity: for each consecutive hole transition the OSM paths connect, does the perceived graph?
    import networkx as nx
    TG = osm_path_graph(T.cart_paths)
    tr = T.transitions()
    agree = n = 0
    ratio = []
    for t in tr:
        tc = _route(TG, t["green_end"], t["next_start"])
        if tc is None:
            continue
        n += 1
        pc = _route(G, t["green_end"], t["next_start"])
        if pc is not None and pc <= 2.0 * tc + 60:
            agree += 1
            ratio.append(pc / max(tc, 1.0))
    out["transitions_osm_connected"] = n
    out["connectivity_acc"] = round(agree / n, 4) if n else None
    out["connected_route_ratio_median"] = round(float(np.median(ratio)), 3) if ratio else None
    out["components"] = nx.number_connected_components(G) if G.number_of_nodes() else 0
    return out


def osm_path_graph(lines, snap=1.5):
    import networkx as nx
    G = nx.Graph()
    key = {}

    def k(p):
        kk = (round(p[0] / snap), round(p[1] / snap))
        if kk not in key:
            key[kk] = len(key) + 1
            G.add_node(key[kk], x=float(p[0]), y=float(p[1]))
        return key[kk]
    for l in lines:
        l = np.asarray(l, float)
        for a, b in zip(l[:-1], l[1:]):
            u, v = k(a), k(b)
            if u != v:
                G.add_edge(u, v, length=float(np.hypot(*(b - a))))
    # OSM ways that touch without a shared node: join ends within 4 m of another node
    ids = list(G.nodes)
    if ids:
        P = np.array([(G.nodes[n]["x"], G.nodes[n]["y"]) for n in ids])
        for i, n in enumerate(ids):
            if G.degree(n) == 1:
                d = np.hypot(*(P - P[i]).T)
                d[i] = 1e9
                j = int(d.argmin())
                if d[j] <= 4.0:
                    G.add_edge(n, ids[j], length=float(d[j]))
    return G


def _route(G, a, b, attach=CONNECT_ATTACH_M):
    import networkx as nx
    if G is None or G.number_of_nodes() == 0:
        return None
    ids = list(G.nodes)
    P = np.array([(G.nodes[n]["x"], G.nodes[n]["y"]) for n in ids])
    da = np.hypot(*(P - np.array(a)).T)
    db = np.hypot(*(P - np.array(b)).T)
    sa = [(ids[i], da[i]) for i in np.argsort(da)[:3] if da[i] <= attach]
    sb = [(ids[i], db[i]) for i in np.argsort(db)[:3] if db[i] <= attach]
    best = None
    for u, du in sa:
        try:
            dd = nx.single_source_dijkstra_path_length(G, u, cutoff=3000, weight="length")
        except Exception:                                        # noqa: BLE001
            continue
        for v, dv in sb:
            if v in dd:
                c = dd[v] + du + dv
                best = c if best is None else min(best, c)
    return best


def eval_relations(T, D):
    """Edge accuracy of the ordering prior: for each true hole n (n+1 mapped), take the perceived green matched to
    hole n's green and its top p_next tee complex: correct when that complex is within 30 m of hole n+1's start."""
    rel = D.get("relations") or []
    by_green = {}
    for r in rel:
        by_green.setdefault(r["green"], []).append(r)
    cx = {c["id"]: c for c in D["complexes"]}
    starts = {h["ref"]: h["start"] for h in T.holes if h["ref"] is not None}
    n = ok = ok_path = n_path = 0
    for g in D["greens"]:
        ref = g.get("_truth_ref")
        if ref is None or ref + 1 not in starts or g["id"] not in by_green:
            continue
        cands = by_green[g["id"]]
        top = max(cands, key=lambda r: r.get("p_next", 0))
        c = cx.get(top["tee"])
        if c is None:
            continue
        s = starts[ref + 1]
        d = min(math.hypot(b["xy"][0] - s[0], b["xy"][1] - s[1]) for b in c["boxes"])
        n += 1
        ok += d <= TEE_START_M
        if top.get("path_m") is not None:
            n_path += 1
            ok_path += d <= TEE_START_M
    return dict(n=n, top1_next_tee_acc=round(ok / n, 4) if n else None, n_with_path=n_path,
                top1_acc_when_path=round(ok_path / n_path, 4) if n_path else None)
