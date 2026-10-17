"""Blind element detectors on one stack: greens, tee boxes / complexes, fairways, bunkers, water, trees,
buildings, parking, driving range, clubhouse. Each returns a list of dicts in grid metres (xy) with a mask
label image where useful; scene.py converts to the course_scene/1 schema (lon/lat).

Object-level probabilities come from the trained models (models/*.pkl via train.py) when present, else rules.
Every object also carries `feat` (the feature row the models use) so perceive.py can write training tables.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage as ndi

import geo

GREEN_P, GREEN_MIN_M2, GREEN_MAX_M2 = 0.5, 120, 4000
TEE_P, TEE_MIN_M2, TEE_MAX_M2 = 0.4, 20, 2500
FAIRWAY_P, FAIRWAY_MIN_M2 = 0.5, 700
BUNKER_P, BUNKER_MIN_M2 = 0.5, 10
WATER_MIN_M2 = 150
TREE_H = 4.0
COMPLEX_GAP_M = 10.0           # boxes whose edges are within 2 x 10 m form one complex
COMPLEX_MERGE_M = 70.0         # + clusters within 70 m that line up along their common axis
COMPLEX_ALIGN_DEG = 25.0


def _rule_p(x, lo, hi):
    return float(np.clip((x - lo) / max(hi - lo, 1e-9), 0, 1))


def _xy(st, r, c):
    x, y = st.rc_to_xy(r, c)
    return float(x), float(y)


def _components(st, mask, min_px, arrays, max_px=None):
    lab, n = geo.label(mask, min_px)
    if max_px and n:
        sizes = np.bincount(lab.ravel())
        big = sizes > max_px
        big[0] = False
        lab[big[lab]] = 0
        lab, n = geo.label(lab > 0, 1)
    stats = geo.comp_stats(lab, n, arrays) if n else {}
    return lab, n, stats


def _apply(model, rows, cols):
    if model is None or not rows:
        return None
    X = np.array([[r.get(c, np.nan) for c in cols] for r in rows], float)
    pr = model.predict_proba(X)
    return pr, list(model.classes_)


# ----------------------------------------------------------------------------- greens
def greens(st, L, models=None):
    pg = st.seg("green")
    m = ndi.binary_opening(pg >= GREEN_P, iterations=1)
    m = ndi.binary_fill_holes(m)
    arrays = dict(p=pg, tophat=L["tophat"], slope=L["slope"], ndvi=L["ndvi"], hag=L["hag"], fair=st.seg("fairway"),
                  bunker_near=ndi.maximum_filter(st.seg("bunker"), size=15))
    lab, n, s = _components(st, m, GREEN_MIN_M2, arrays, GREEN_MAX_M2 / st.res ** 2)
    ax, ln, wd, comp = geo.shape_stats(lab, n, st.res) if n else ([], [], [], [])
    pmax = geo.comp_max(lab, n, pg) if n else []
    # surround (15-40 m ring) height for "raised"
    out = []
    z = L["dtm"]
    for i in range(n):
        x, y = _xy(st, s["r"][i], s["c"][i])
        area = s["area_px"][i] * st.res ** 2
        feat = dict(area=area, p_mean=s["p"][i], p_max=pmax[i], tophat=s["tophat"][i], slope=s["slope"][i],
                    ndvi=s["ndvi"][i], hag=s["hag"][i], fair_mean=s["fair"][i], bunker_near=s["bunker_near"][i],
                    compact=comp[i], elong=ln[i] / max(wd[i], 1e-6))
        out.append(dict(id=f"g{i + 1}", lab=i + 1, xy=(x, y), area=area, feat=feat, axis=ax[i]))
    rings = geo.rings_from_labels(st, lab)
    for g in out:
        g["ring"] = rings.get(g["lab"])
    _raised(st, lab, out, z)
    return out, lab


def _raised(st, lab, objs, z):
    if not np.isfinite(z).any() or not objs:
        for o in objs:
            o["raised"] = None
            o["elev"] = None
        return
    objs_sl = ndi.find_objects(lab)
    pad = int(40 / st.res)
    for o in objs:
        sl = objs_sl[o["lab"] - 1]
        if sl is None:
            o["raised"] = o["elev"] = None
            continue
        r0, r1 = max(sl[0].start - pad, 0), min(sl[0].stop + pad, lab.shape[0])
        c0, c1 = max(sl[1].start - pad, 0), min(sl[1].stop + pad, lab.shape[1])
        m = lab[r0:r1, c0:c1] == o["lab"]
        zz = z[r0:r1, c0:c1]
        d = ndi.distance_transform_edt(~m) * st.res
        ring = (d >= 15) & (d <= 40) & np.isfinite(zz)
        inner = m & np.isfinite(zz)
        if inner.sum() < 5 or ring.sum() < 5:
            o["raised"] = o["elev"] = None
            continue
        o["elev"] = float(np.mean(zz[inner]))
        o["raised"] = float(o["elev"] - np.median(zz[ring]))
        o["feat"]["raised"] = o["raised"]


# ----------------------------------------------------------------------------- tees
def tee_boxes(st, L, green_lab, models=None):
    pt = st.seg("tee")
    seg_m = ndi.binary_opening(pt >= TEE_P, iterations=1)
    pad_m = np.zeros_like(seg_m)
    if L["lidar"] and np.isfinite(L["dtm"]).mean() > 0.5:
        pad_m = lidar_pad_mask(L["dtm"], st.res)
        # pads are turf: drop pavement / roofs / trees / water
        pad_m &= (np.nan_to_num(L["ndvi"], nan=0) > 0.15) & (np.nan_to_num(L["hag"], nan=0) < 1.0)
    near_green = ndi.binary_dilation(green_lab > 0, iterations=int(6 / st.res))
    m = (seg_m | pad_m) & ~near_green
    arrays = dict(p=pt, pad=pad_m.astype(np.float32), seg=seg_m.astype(np.float32), tophat=L["tophat"],
                  slope=L["slope"], ndvi=L["ndvi"], fair=st.seg("fairway"), green=st.seg("green"), hag=L["hag"])
    lab, n, s = _components(st, m, TEE_MIN_M2, arrays, TEE_MAX_M2 / st.res ** 2)
    ax, ln, wd, comp = geo.shape_stats(lab, n, st.res) if n else ([], [], [], [])
    pmax = geo.comp_max(lab, n, pt) if n else []
    out = []
    for i in range(n):
        x, y = _xy(st, s["r"][i], s["c"][i])
        area = s["area_px"][i] * st.res ** 2
        src = (["segment"] if s["seg"][i] > 0.2 else []) + (["lidar_pad"] if s["pad"][i] > 0.2 else [])
        feat = dict(area=area, p_mean=s["p"][i], p_max=pmax[i], pad_frac=s["pad"][i], seg_frac=s["seg"][i],
                    tophat=s["tophat"][i], slope=s["slope"][i], ndvi=s["ndvi"][i], fair_mean=s["fair"][i],
                    green_mean=s["green"][i], hag=s["hag"][i], compact=comp[i], elong=ln[i] / max(wd[i], 1e-6),
                    length=ln[i], width=wd[i])
        # rule: segment evidence dominates; lidar-only pads are weak, both agree = strong
        p = 0.25 + 0.7 * _rule_p(s["p"][i], 0.2, 0.7) if src else 0.0
        if src == ["lidar_pad"]:
            p = 0.25 + 0.25 * _rule_p(s["tophat"][i] if np.isfinite(s["tophat"][i]) else 0, 0.1, 0.4)
        elif len(src) == 2:
            p = min(1.0, p + 0.15)
        out.append(dict(id=f"tb{i + 1}", lab=i + 1, xy=(x, y), area=area, src=src, feat=feat, p=p, axis=ax[i],
                        length=ln[i], width=wd[i]))
    if models and models.get("tee_box"):
        md = models["tee_box"]
        res = _apply(md["clf"], [b["feat"] for b in out], md["features"])
        if res:
            pr, cl = res
            for b, row in zip(out, pr):
                b["p"] = float(row[cl.index(1)])
    rings = geo.rings_from_labels(st, lab)
    for b in out:
        b["ring"] = rings.get(b["lab"])
    return out, lab


def lidar_pad_mask(z, res):
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tees"))
    try:
        import lidar_pads as lp
        m = np.zeros(z.shape, bool)
        for comp in lp.components(z, res):
            m[comp["rows"], comp["cols"]] = True
        return m
    except Exception as e:                                       # noqa: BLE001
        print("lidar pads failed:", repr(e)[:200])
        return np.zeros(z.shape, bool)


def tee_complexes(st, boxes, box_lab, greens_, min_box_p=0.3):
    """Cluster boxes into one complex per hole start: boxes within 2 x COMPLEX_GAP_M, then clusters that line
    up along their common axis within COMPLEX_MERGE_M."""
    keep = [b for b in boxes if b["p"] >= min_box_p]
    if not keep:
        return []
    ids = {b["lab"]: b for b in keep}
    mk = np.isin(box_lab, list(ids))
    dil = ndi.binary_dilation(mk, iterations=int(COMPLEX_GAP_M / st.res))
    clab, nc = ndi.label(dil, structure=np.ones((3, 3)))
    groups = {}
    for b in keep:
        r, c = st.xy_to_rc(*b["xy"])
        k = int(clab[int(np.clip(round(float(r)), 0, st.H - 1)), int(np.clip(round(float(c)), 0, st.W - 1))])
        if k == 0:                                               # centroid outside its own (concave) shape
            k = 10_000 + b["lab"]
        groups.setdefault(k, []).append(b)
    cl = [_complex(g) for g in groups.values()]
    # merge aligned clusters (forward tees 30-70 m up the line)
    merged = True
    while merged:
        merged = False
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                a, b = cl[i], cl[j]
                d = math.hypot(a["xy"][0] - b["xy"][0], a["xy"][1] - b["xy"][1])
                if d > COMPLEX_MERGE_M or d < 1:
                    continue
                brg = geo.bearing(a["xy"], b["xy"]) % 180
                axes = [x["axis"] for x in (a, b) if x["axis"] is not None and x["elong"] >= 1.6]
                if not axes or any(geo.angle_diff(brg, ax) > COMPLEX_ALIGN_DEG for ax in axes):
                    continue
                if _green_between(a["xy"], b["xy"], greens_):
                    continue
                cl[i] = _complex(a["boxes"] + b["boxes"])
                cl.pop(j)
                merged = True
                break
            if merged:
                break
    for k, c in enumerate(sorted(cl, key=lambda c: (-c["xy"][1], c["xy"][0]))):
        c["id"] = f"t{k + 1}"
        for j, b in enumerate(c["boxes"]):
            b["cid"] = f"t{k + 1}.{j + 1}"
    return cl


def _green_between(a, b, greens_, tol=12.0):
    for g in greens_:
        p = np.array(g["xy"])
        A, B = np.array(a), np.array(b)
        ab = B - A
        t = np.clip(np.dot(p - A, ab) / max(np.dot(ab, ab), 1e-9), 0, 1)
        if np.hypot(*(A + t * ab - p)) < tol + math.sqrt(g["area"] / math.pi):
            return True
    return False


def _complex(bs):
    w = np.array([max(b["area"], 1.0) for b in bs])
    P = np.array([b["xy"] for b in bs])
    c = (P * w[:, None]).sum(0) / w.sum()
    pts = np.vstack([np.asarray(b["ring"], float) for b in bs if b.get("ring")] or [P])
    q = pts - pts.mean(0)
    axis, elong, length = None, 1.0, 0.0
    if len(q) >= 3:
        ev, evec = np.linalg.eigh(np.cov(q.T))
        v = evec[:, 1]
        axis = (math.degrees(math.atan2(v[0], v[1])) + 360) % 180
        proj = q @ v
        length = float(proj.max() - proj.min())
        width = float((q @ evec[:, 0]).max() - (q @ evec[:, 0]).min())
        elong = length / max(width, 1e-6)
    p = 1.0 - float(np.prod([1 - b["p"] for b in bs]))
    return dict(boxes=bs, xy=(float(c[0]), float(c[1])), axis=axis, elong=elong, length=length, p=min(p, 0.99),
                area=float(w.sum()), src=sorted({s for b in bs for s in b["src"]}))


def complex_features(c, greens_, others):
    g = np.array([gr["xy"] for gr in greens_]) if greens_ else np.zeros((0, 2))
    d = np.hypot(*(g - np.array(c["xy"])).T) if len(g) else np.array([])
    return dict(n_boxes=len(c["boxes"]), area=c["area"], length=c["length"], elong=c["elong"],
                max_box_p=max(b["p"] for b in c["boxes"]), mean_seg=float(np.mean([b["feat"]["p_mean"] for b in c["boxes"]])),
                has_pad=float(any("lidar_pad" in b["src"] for b in c["boxes"])),
                has_seg=float(any("segment" in b["src"] for b in c["boxes"])),
                d_green=float(d.min()) if d.size else 999.0,
                n_greens_80_600=float(((d >= 80) & (d <= 600)).sum()) if d.size else 0.0,
                n_greens_lt60=float((d < 60).sum()) if d.size else 0.0)


# ----------------------------------------------------------------------------- fairways
def fairways(st, L):
    pf = st.seg("fairway")
    m = ndi.binary_opening(pf >= FAIRWAY_P, iterations=2)
    m = ndi.binary_fill_holes(m)
    lab, n, s = _components(st, m, FAIRWAY_MIN_M2 / st.res ** 2, dict(p=pf))
    ax, ln, wd, comp = geo.shape_stats(lab, n, st.res) if n else ([], [], [], [])
    rings = geo.rings_from_labels(st, lab, simplify_m=1.0)
    objs = ndi.find_objects(lab)
    G = st.naip()[1]
    out = []
    for i in range(n):
        sl = objs[i]
        sub = lab[sl] == i + 1
        cl = centerline(sub, st, sl)
        stripe, coh = stripe_orientation(G[sl], sub)
        area = s["area_px"][i] * st.res ** 2
        L_m = float(np.sum(np.hypot(*np.diff(cl, axis=0).T))) if len(cl) > 1 else 0.0
        chord = geo.bearing(cl[0], cl[-1]) % 180 if len(cl) > 1 else ax[i]
        out.append(dict(id=f"f{i + 1}", lab=i + 1, xy=_xy(st, s["r"][i], s["c"][i]), area=area, ring=rings.get(i + 1),
                        centerline=cl, length=L_m, width=area / max(L_m, 1.0), axis=chord, stripe=stripe,
                        stripe_strength=coh, p=float(np.clip(s["p"][i], 0, 1))))
    return out, lab


def centerline(sub, st, sl, smooth_m=6.0):
    """Longest path through the skeleton of one component (xy metres), smoothed."""
    from skimage.morphology import skeletonize
    m = ndi.binary_closing(np.pad(sub, 3), iterations=3)[3:-3, 3:-3]
    sk = skeletonize(m)
    rr, cc = np.nonzero(sk)
    if rr.size < 2:
        rr, cc = np.nonzero(sub)
        if rr.size == 0:
            return np.zeros((0, 2))
        r, c = rr.mean(), cc.mean()
        return np.array([_xy(st, r + sl[0].start, c + sl[1].start)] * 2)
    idx = {(a, b): k for k, (a, b) in enumerate(zip(rr.tolist(), cc.tolist()))}
    import networkx as nx
    Gs = nx.Graph()
    for (a, b), k in idx.items():
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            q = (a + dr, b + dc)
            if q in idx:
                Gs.add_edge(k, idx[q], weight=math.hypot(dr, dc))
    if Gs.number_of_nodes() < 2:
        k0 = 0
        return np.array([_xy(st, rr[k0] + sl[0].start, cc[k0] + sl[1].start)] * 2)
    comp = max(nx.connected_components(Gs), key=len)
    H = Gs.subgraph(comp)
    s0 = next(iter(comp))
    d1 = nx.single_source_dijkstra_path_length(H, s0)
    a = max(d1, key=d1.get)
    d2, paths = nx.single_source_dijkstra(H, a)
    b = max(d2, key=d2.get)
    path = paths[b]
    pts = np.array([_xy(st, rr[k] + sl[0].start, cc[k] + sl[1].start) for k in path])
    if len(pts) > 5:
        k = max(1, int(smooth_m / st.res))
        ker = np.ones(2 * k + 1) / (2 * k + 1)
        xs = np.convolve(np.pad(pts[:, 0], k, mode="edge"), ker, "valid")
        ys = np.convolve(np.pad(pts[:, 1], k, mode="edge"), ker, "valid")
        pts = np.c_[xs, ys]
        from shapely.geometry import LineString
        pts = np.asarray(LineString(pts).simplify(2.0).coords)
    return pts


def stripe_orientation(g, mask, erode=3):
    """Dominant mowing-stripe orientation (undirected bearing) and coherence inside mask from the structure
    tensor of the high-passed green band."""
    m = ndi.binary_erosion(mask, iterations=erode)
    if m.sum() < 200:
        return None, 0.0
    hp = g - ndi.gaussian_filter(g, 4)
    gr = ndi.sobel(hp, axis=0)          # +rows = south
    gc = ndi.sobel(hp, axis=1)          # +cols = east
    e, nn = gc, -gr
    Jee, Jnn, Jen = (e * e)[m].mean(), (nn * nn)[m].mean(), (e * nn)[m].mean()
    tr = Jee + Jnn
    if tr <= 1e-9:
        return None, 0.0
    coh = math.sqrt((Jee - Jnn) ** 2 + 4 * Jen ** 2) / tr
    phi = 0.5 * math.atan2(2 * Jen, Jee - Jnn)             # gradient angle from east, counter-clockwise
    grad_bearing = (90.0 - math.degrees(phi)) % 180
    stripe = (grad_bearing + 90.0) % 180
    return float(stripe), float(coh)


# ----------------------------------------------------------------------------- bunkers, water, trees
def bunkers(st, L):
    pb = st.seg("bunker")
    m = pb >= BUNKER_P
    lab, n, s = _components(st, m, BUNKER_MIN_M2 / st.res ** 2, dict(p=pb))
    rings = geo.rings_from_labels(st, lab)
    return [dict(id=f"b{i + 1}", lab=i + 1, xy=_xy(st, s["r"][i], s["c"][i]), area=s["area_px"][i] * st.res ** 2,
                 ring=rings.get(i + 1), p=float(s["p"][i])) for i in range(n)], lab


def water(st, L):
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "segment"))
    from model import nir_water
    img = st.a["naip"]
    m, score = nir_water(img)
    cls9 = st.cls() == 9
    if cls9.mean() > 0.0005:
        m = m | ndi.binary_opening(cls9, iterations=1)
    h = L["hag"]
    if L["lidar"]:
        m &= ~(np.nan_to_num(h, nan=0) > 2.0)
        # tree shadows read as dark water: drop small blobs ringed by tall canopy
        tall = np.nan_to_num(h, nan=0) > 3.0
        lab0, n0 = geo.label(m, 1)
        if n0:
            ring_lab = np.where(lab0 == 0, ndi.grey_dilation(lab0, size=(13, 13)), 0)
            frac = np.asarray(ndi.mean(tall.astype(np.float32), ring_lab, range(1, n0 + 1)))
            sizes = np.bincount(lab0.ravel(), minlength=n0 + 1)[1:]
            bad = np.nonzero((np.nan_to_num(frac) > 0.35) & (sizes < 2000))[0] + 1
            m[np.isin(lab0, bad)] = False
    lab, n, s = _components(st, m, WATER_MIN_M2 / st.res ** 2, dict(score=score, cls9=cls9.astype(np.float32)))
    ax, ln, wd, comp = geo.shape_stats(lab, n, st.res) if n else ([], [], [], [])
    rings = geo.rings_from_labels(st, lab, simplify_m=1.0)
    out = []
    for i in range(n):
        p = float(np.clip(0.55 + 0.4 * max(s["cls9"][i], (s["score"][i] - 0.5) * 2), 0, 0.99))
        out.append(dict(id=f"w{i + 1}", lab=i + 1, xy=_xy(st, s["r"][i], s["c"][i]), area=s["area_px"][i] * st.res ** 2,
                        ring=rings.get(i + 1), p=p, kind="stream" if (wd[i] < 15 and ln[i] > 4 * wd[i]) else "pond"))
    return out, lab


def trees(st, L):
    if L["lidar"]:
        h = np.nan_to_num(L["hag"], nan=0)
        m = (h >= TREE_H) & (st.cls() != 6)
    else:
        m = L["tall"]
        h = np.zeros(m.shape, np.float32)
    m = ndi.binary_opening(m, iterations=1)
    lab, n, s = _components(st, m, 8, dict(h=h))
    p90 = geo.comp_percentile(lab, n, np.where(lab > 0, h, np.nan), 90) if n else []
    big = [i for i in range(n) if s["area_px"][i] * st.res ** 2 >= 400]
    sub = np.where(np.isin(lab, np.array(big) + 1), lab, 0) if big else np.zeros_like(lab)
    rings = geo.rings_from_labels(st, sub, simplify_m=1.5)
    out = []
    for i in range(n):
        area = s["area_px"][i] * st.res ** 2
        out.append(dict(id=f"c{i + 1}", lab=i + 1, xy=_xy(st, s["r"][i], s["c"][i]), area=area,
                        height=float(p90[i]) if np.isfinite(p90[i]) else None, kind="stand" if area >= 400 else "tree",
                        ring=rings.get(i + 1), p=0.95 if L["lidar"] else 0.6))
    return out, lab


# ----------------------------------------------------------------------------- buildings, parking
def buildings(st, L):
    h = np.nan_to_num(L["hag"], nan=0)
    cls = st.cls()
    if L["lidar"]:
        roof = (h >= 2.5) & (np.nan_to_num(L["ndvi"], nan=1) < 0.2)
        smooth = ndi.uniform_filter(h, 3)
        flatish = np.abs(h - smooth) < 1.0
        m = (cls == 6) | (roof & flatish)
    else:
        return [], np.zeros(h.shape, np.int32)
    m = ndi.binary_opening(ndi.binary_closing(m, iterations=1), iterations=1)
    lab, n, s = _components(st, m, 40 / st.res ** 2, dict(cls6=(cls == 6).astype(np.float32), h=h, ndvi=L["ndvi"]))
    rings = geo.rings_from_labels(st, lab, simplify_m=1.0)
    out = []
    for i in range(n):
        p = float(np.clip(0.45 + 0.5 * s["cls6"][i] + 0.1 * (s["h"][i] > 3) - 0.3 * (s["ndvi"][i] > 0.25), 0, 0.99))
        out.append(dict(id=f"bl{i + 1}", lab=i + 1, xy=_xy(st, s["r"][i], s["c"][i]), area=s["area_px"][i] * st.res ** 2,
                        ring=rings.get(i + 1), height=float(s["h"][i]), p=p))
    return out, lab


def parking(st, L, bld_lab, path_prob=None, models=None):
    paved = L["paved"] & (bld_lab == 0)
    m = ndi.binary_opening(paved, iterations=2)
    m = ndi.binary_closing(m, iterations=2)
    lab, n, s = _components(st, m, 400 / st.res ** 2,
                            dict(ndvi=L["ndvi"], bright=L["bright"], slope=L["slope"],
                                 pathp=path_prob if path_prob is not None else np.zeros(m.shape, np.float32),
                                 wmax=L["paved_width"]))
    ax, ln, wd, comp = geo.shape_stats(lab, n, st.res) if n else ([], [], [], [])
    rings = geo.rings_from_labels(st, lab, simplify_m=1.0)
    out = []
    for i in range(n):
        area = s["area_px"][i] * st.res ** 2
        elong = ln[i] / max(wd[i], 1e-6)
        feat = dict(area=area, ndvi=s["ndvi"][i], bright=s["bright"][i], slope=s["slope"][i], pathp=s["pathp"][i],
                    elong=elong, width=wd[i], length=ln[i], compact=comp[i])
        p = 0.3 + 0.4 * _rule_p(wd[i], 12, 30) + 0.2 * _rule_p(area, 400, 3000) - 0.3 * _rule_p(elong, 4, 10)
        out.append(dict(id=f"pk{i + 1}", lab=i + 1, xy=_xy(st, s["r"][i], s["c"][i]), area=area, ring=rings.get(i + 1),
                        p=float(np.clip(p, 0.02, 0.95)), feat=feat))
    if models and models.get("parking"):
        md = models["parking"]
        res = _apply(md["clf"], [o["feat"] for o in out], md["features"])
        if res:
            pr, cl = res
            for o, row in zip(out, pr):
                o["p"] = float(row[cl.index(1)])
    return out, lab


# ----------------------------------------------------------------------------- driving range
def driving_range(st, L, complexes, greens_, clubhouse_xy=None):
    """A range = a wide hitting strip (a tee complex whose long axis runs ACROSS the open turf in front of it)
    + 150-300 m of open, low, mown turf with no green, typically near the clubhouse."""
    turf = (np.nan_to_num(L["ndvi"], nan=0) > 0.2) & (np.nan_to_num(L["hag"], nan=0) < 1.0) & L["valid"]
    gxy = np.array([g["xy"] for g in greens_]) if greens_ else np.zeros((0, 2))
    best = None
    for c in complexes:
        if c["axis"] is None or c["length"] < 35:
            continue
        for sgn in (1, -1):
            brg = (c["axis"] + 90 * sgn) % 360                    # play runs across the strip
            v = np.array([math.sin(math.radians(brg)), math.cos(math.radians(brg))])
            u = np.array([v[1], -v[0]])
            # sample a 220 m x strip-length rectangle in front
            ts = np.arange(20, 240, 5.0)
            ws = np.linspace(-c["length"] / 2, c["length"] / 2, 9)
            P = np.array(c["xy"])[None, None] + ts[:, None, None] * v + ws[None, :, None] * u
            r, cc = st.xy_to_rc(P[..., 0].ravel(), P[..., 1].ravel())
            ok = (r >= 0) & (r <= st.H - 1) & (cc >= 0) & (cc <= st.W - 1)
            if ok.mean() < 0.8:
                continue
            ri, ci = np.round(r[ok]).astype(int), np.round(cc[ok]).astype(int)
            frac = float(turf[ri, ci].mean())
            far = np.array(c["xy"]) + 150 * v
            gin = 0
            if len(gxy):
                rel = gxy - np.array(c["xy"])
                along = rel @ v
                across = np.abs(rel @ u)
                gin = int(((along > 30) & (along < 240) & (across < c["length"] / 2 + 20)).sum())
            dch = math.hypot(*(np.array(clubhouse_xy) - np.array(c["xy"]))) if clubhouse_xy is not None else 400.0
            score = frac - 0.35 * gin + 0.15 * (dch < 350) + 0.1 * min(c["length"] / 80, 1)
            if frac > 0.85 and gin <= 1 and (best is None or score > best["score"]):
                best = dict(score=score, complex=c, bearing=brg, v=v, u=u, frac=frac, dch=dch)
    if not best:
        return None
    c = best["complex"]
    v, u = best["v"], best["u"]
    o = np.array(c["xy"])
    half = max(c["length"] / 2, 30)
    poly = [o - half * u, o + half * u, o + half * u + 250 * v, o - half * u + 250 * v, o - half * u]
    p = float(np.clip(0.3 + 0.4 * (best["frac"] - 0.85) / 0.15 + 0.2 * (best["dch"] < 350), 0.05, 0.9))
    return dict(complex=c["id"], ring=np.array(poly), xy=tuple(o + 125 * v), hitting_end=tuple(o), axis=best["bearing"] % 180,
                length=250.0, width=2 * half, p=p)


# ----------------------------------------------------------------------------- clubhouse
def clubhouse(st, bld, parks, greens_, complexes, G=None, models=None):
    if not bld:
        if parks:
            pk = max(parks, key=lambda p: p["area"] * p["p"])
            return dict(xy=pk["xy"], building=None, p=0.2, how="largest parking (no buildings)"), []
        return None, []
    pk = [p for p in parks if p["p"] >= 0.4]
    PK = np.array([p["xy"] for p in pk]) if pk else np.zeros((0, 2))
    PA = np.array([p["area"] for p in pk]) if pk else np.zeros(0)
    gx = np.array([g["xy"] for g in greens_]) if greens_ else np.zeros((0, 2))
    tx = np.array([c["xy"] for c in complexes]) if complexes else np.zeros((0, 2))
    course_c = np.vstack([gx, tx]).mean(0) if len(gx) + len(tx) else np.array([st.x0 + st.W / 2, st.y1 - st.H / 2])
    nodes = np.array([(G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes]) if G is not None and G.number_of_nodes() else np.zeros((0, 2))
    rows = []
    BX = np.array([b["xy"] for b in bld if b["area"] >= 60]) if bld else np.zeros((0, 2))
    amax = max([b["area"] for b in bld] + [1.0])
    for b in bld:
        if b["area"] < 120:
            continue
        p = np.array(b["xy"])
        dpk = np.hypot(*(PK - p).T) if len(PK) else np.array([999.0])
        dg = np.hypot(*(gx - p).T) if len(gx) else np.array([999.0])
        dt = np.hypot(*(tx - p).T) if len(tx) else np.array([999.0])
        dn = np.hypot(*(nodes - p).T) if len(nodes) else np.array([999.0])
        f = dict(area=b["area"], height=b.get("height") or 0.0, d_park=float(dpk.min()),
                 park_area_150=float(PA[dpk < 150].sum()) if len(PA) else 0.0,
                 d_green=float(dg.min()), n_green_250=float((dg < 250).sum()), d_tee=float(dt.min()),
                 n_tee_250=float((dt < 250).sum()), d_center=float(np.hypot(*(course_c - p))),
                 n_path_nodes_80=float((dn < 80).sum()),
                 park_area_60=float(PA[dpk < 60].sum()) if len(PA) else 0.0,
                 area_rel=b["area"] / amax,
                 n_bld_100=float((np.hypot(*(BX - p).T) < 100).sum() - 1) if len(BX) else 0.0)
        s = (math.log(max(b["area"], 1)) + 1.2 * math.log1p(f["park_area_150"] / 500) + 0.8 * min(f["n_green_250"], 2)
             + 0.6 * min(f["n_tee_250"], 2) - f["d_center"] / 800 - (2.0 if f["d_green"] > 500 else 0)
             - 0.15 * min(f["n_bld_100"], 10) + 1.0 * f["area_rel"])
        rows.append(dict(b=b, feat=f, score=s))
    if not rows:
        return None, []
    if models and models.get("clubhouse"):
        md = models["clubhouse"]
        res = _apply(md["clf"], [r["feat"] for r in rows], md["features"])
        if res:
            pr, cl = res
            for r, row in zip(rows, pr):
                r["score"] = float(row[cl.index(1)])
    sc = np.array([r["score"] for r in rows])
    best = rows[int(sc.argmax())]
    if models and models.get("clubhouse"):
        p = float(sc.max())
    else:
        e = np.exp(sc - sc.max())
        p = float(e.max() / e.sum())
    return dict(xy=best["b"]["xy"], building=best["b"]["id"], p=p, how="building score",
                evidence=dict(park_area_150=best["feat"]["park_area_150"], n_green_250=best["feat"]["n_green_250"])), rows


# ----------------------------------------------------------------------------- green kinds
def classify_greens(st, greens_, complexes, ch, models=None, parks=(), bld=()):
    """hole vs practice: a practice green is near the clubhouse and has no tee complex at a playable distance
    that isn't itself next to the clubhouse; trained model when available."""
    tx = np.array([c["xy"] for c in complexes]) if complexes else np.zeros((0, 2))
    tp = np.array([c["p"] for c in complexes]) if complexes else np.zeros(0)
    chx = np.array(ch["xy"]) if ch else None
    gx = np.array([g["xy"] for g in greens_]) if greens_ else np.zeros((0, 2))
    PK = np.array([p["xy"] for p in parks if p["p"] >= 0.4]) if parks else np.zeros((0, 2))
    BL = np.array([b["xy"] for b in bld if b["area"] >= 150]) if bld else np.zeros((0, 2))
    for g in greens_:
        p = np.array(g["xy"])
        d = np.hypot(*(tx - p).T) if len(tx) else np.array([])
        dch = float(np.hypot(*(chx - p))) if chx is not None else 999.0
        dg = np.hypot(*(gx - p).T) if len(gx) else np.array([])
        dg = dg[dg > 1]
        f = g["feat"]
        f.update(n_tee_80_600=float(((d >= 80) & (d <= 600) & (tp >= 0.5)).sum()) if d.size else 0.0,
                 d_tee=float(d.min()) if d.size else 999.0, d_clubhouse=dch, d_green=float(dg.min()) if dg.size else 999.0,
                 n_green_150=float((dg < 150).sum()) if dg.size else 0.0,
                 d_parking=float(np.hypot(*(PK - p).T).min()) if len(PK) else 999.0,
                 d_building=float(np.hypot(*(BL - p).T).min()) if len(BL) else 999.0,
                 n_tee_lt60=float((d < 60).sum()) if d.size else 0.0, raised=g.get("raised") if g.get("raised") is not None else np.nan)
        g["tees_in_range"] = int(f["n_tee_80_600"])
        g["d_clubhouse"] = dch if chx is not None else None
        pg = _rule_p(f["p_mean"], 0.45, 0.75) * (0.4 + 0.6 * _rule_p(f["area"], GREEN_MIN_M2, 350))
        pprac = 0.1 + 0.6 * (dch < 180) + 0.2 * (f["area"] > 1100) - 0.25 * min(f["n_tee_80_600"], 2) / 2
        pprac = float(np.clip(pprac, 0.02, 0.95))
        g["p"] = float(np.clip(0.15 + 0.8 * pg, 0, 0.98))
        g["p_practice"] = g["p"] * pprac
        g["p_hole"] = g["p"] * (1 - pprac)
    if models and models.get("green"):
        md = models["green"]
        res = _apply(md["clf"], [g["feat"] for g in greens_], md["features"])
        if res:
            pr, cl = res
            for g, row in zip(greens_, pr):
                ph = float(row[cl.index(1)]) if 1 in cl else 0.0
                pp = float(row[cl.index(2)]) if 2 in cl else 0.0
                g["p"], g["p_hole"], g["p_practice"] = ph + pp, ph, pp
    for g in greens_:
        if g["p_hole"] >= 0.5:
            g["kind"] = "hole"
        elif g["p_practice"] >= 0.5:
            g["kind"] = "practice"
        else:
            g["kind"] = "uncertain"
    return greens_
