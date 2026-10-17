"""Cart paths: per-pixel probability (trained classifier, else a rule) -> skeleton -> graph with junctions.

    prob, road = path_prob(L, model)              # (H, W) float32 in [0, 1] each
    G = skeleton_graph(prob >= thr, prob, L)      # networkx Graph: nodes {x, y}, edges {pts, length, p, width}
    G = bridge_gaps(G, prob); G = prune(G)
"""
from __future__ import annotations

import math

import numpy as np
from scipy import ndimage as ndi

import features as F

THR = 0.5
SPUR_M = 10.0
GAP_M = 14.0
LONG_GAP_M = 40.0
LONG_GAP_DEG = 30.0
MIN_COMP_M = 30.0
ROAD_WIDTH_M = 6.5
MIN_LINE_M = 25.0
MAX_LINE_WIDTH_M = 6.0


def rule_prob(L):
    """No model yet: thin, non-vegetated, low, narrower than a road, not sand -> path."""
    nd = L["ndvi"]
    paved = L["paved"]
    width = L["paved_width_max"]
    bunker = L.st.seg("bunker")
    c = np.clip(L["nd_contrast"] / 0.15, 0, 1)
    lp = np.clip(L["line_paved"] / 0.15, 0, 1)
    p = (0.45 * c + 0.35 * lp + 0.2 * np.clip((-0.1 - L["ndvi_rel"]) / 0.2, 0, 1))
    p = np.where(paved | (lp > 0.6), p, p * 0.3)
    p = np.where((width > ROAD_WIDTH_M) | (bunker > 0.5), p * 0.25, p)
    road = np.where(paved & (width > ROAD_WIDTH_M), 0.7, 0.0)
    return np.nan_to_num(p, nan=0).astype(np.float32), road.astype(np.float32)


def model_prob(L, model):
    """model: {"clf": sklearn classifier with classes 0 other / 1 path / 2 road, "features": [...]}"""
    X = F.path_feature_stack(L, list(model["features"]))
    n, H, W = X.shape
    flat = X.reshape(n, -1).T
    valid = L["valid"].ravel()
    out = np.zeros((H * W, 3), np.float32)
    clf = model["clf"]
    step = 400_000
    vi = np.nonzero(valid)[0]
    for s in range(0, len(vi), step):
        ii = vi[s:s + step]
        out[ii] = clf.predict_proba(flat[ii])
    cls = list(clf.classes_)
    p = out[:, cls.index(1)].reshape(H, W) if 1 in cls else np.zeros((H, W), np.float32)
    r = out[:, cls.index(2)].reshape(H, W) if 2 in cls else np.zeros((H, W), np.float32)
    return p, r


def path_prob(L, model=None):
    if model is not None:
        try:
            return model_prob(L, model)
        except Exception as e:                                   # noqa: BLE001
            print("path model failed, rule fallback:", repr(e)[:300])
    return rule_prob(L)


# --------------------------------------------------------------------------- skeleton graph
_NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def skeleton_graph(mask, prob, st, width=None):
    """Graph of the skeleton of `mask`: nodes at ends / junctions, edges = pixel chains (xy metres)."""
    import networkx as nx
    from skimage.morphology import skeletonize
    m = ndi.binary_closing(mask, iterations=1)
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if n:
        sizes = np.bincount(lab.ravel())
        keep = sizes >= 12
        keep[0] = False
        m = keep[lab]
    sk = skeletonize(m)
    nbc = ndi.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - 1
    nodes_mask = sk & ((nbc == 1) | (nbc >= 3) | (nbc == 0))
    nlab, nn = ndi.label(nodes_mask, structure=np.ones((3, 3)))
    G = nx.Graph()
    H, W = sk.shape

    def xy(r, c):
        x, y = st.rc_to_xy(r, c)
        return float(x), float(y)
    if nn:
        cr = ndi.center_of_mass(np.ones_like(nlab), nlab, range(1, nn + 1))
        for i, (r, c) in enumerate(cr):
            x, y = xy(r, c)
            G.add_node(i + 1, x=x, y=y)
    seg = sk & ~nodes_mask
    slab, ns = ndi.label(seg, structure=np.ones((3, 3)))
    objs = ndi.find_objects(slab)
    for si, sl in enumerate(objs):
        if sl is None:
            continue
        r0, c0 = max(sl[0].start - 1, 0), max(sl[1].start - 1, 0)
        r1, c1 = min(sl[0].stop + 1, H), min(sl[1].stop + 1, W)
        sub = slab[r0:r1, c0:c1] == si + 1
        rr, cc = np.nonzero(sub)
        pix = set(zip((rr + r0).tolist(), (cc + c0).tolist()))
        # node clusters touching this chain
        touch = {}
        for (r, c) in pix:
            for dr, dc in _NB:
                q = (r + dr, c + dc)
                if 0 <= q[0] < H and 0 <= q[1] < W and nlab[q] > 0:
                    touch.setdefault(int(nlab[q]), q)
        chain = _order_chain(pix, touch)
        if not chain:
            continue
        ends = list(touch.keys())
        if len(ends) >= 2:
            u, v = _chain_end_nodes(chain, touch)
        elif len(ends) == 1:
            u = v = ends[0]
        else:                                                    # closed loop without nodes
            r, c = chain[0]
            u = v = max(G.nodes) + 1 if G.number_of_nodes() else 1
            x, y = xy(r, c)
            G.add_node(u, x=x, y=y)
        pts = [(G.nodes[u]["x"], G.nodes[u]["y"])] + [xy(r, c) for r, c in chain] + [(G.nodes[v]["x"], G.nodes[v]["y"])]
        rs = np.array([p[0] for p in chain])
        cs = np.array([p[1] for p in chain])
        pm = float(np.mean(prob[rs, cs]))
        wd = float(np.median(width[rs, cs])) if width is not None else None
        _add_edge(G, u, v, pts, pm, wd)
    # node clusters adjacent to each other without a chain (junction blobs touching) -> join
    if nn:
        dil = ndi.grey_dilation(nlab, size=(3, 3))
        pairs = set()
        for a, b in zip(nlab[nodes_mask].tolist(), dil[nodes_mask].tolist()):
            if a and b and a != b:
                pairs.add((min(a, b), max(a, b)))
        for a, b in pairs:
            if not G.has_edge(a, b):
                pa, pb = (G.nodes[a]["x"], G.nodes[a]["y"]), (G.nodes[b]["x"], G.nodes[b]["y"])
                _add_edge(G, a, b, [pa, pb], 0.5, None)
    return G


def _add_edge(G, u, v, pts, p, w):
    pts = np.asarray(pts, float)
    length = float(np.sum(np.hypot(*np.diff(pts, axis=0).T))) if len(pts) > 1 else 0.0
    if G.has_edge(u, v):
        if G.edges[u, v]["length"] <= length:
            return
    G.add_edge(u, v, pts=pts, length=length, p=p, width=w)


def _order_chain(pix, touch):
    if not pix:
        return []
    def nbrs(q):
        return [(q[0] + dr, q[1] + dc) for dr, dc in _NB if (q[0] + dr, q[1] + dc) in pix]
    # start next to a node if any, else at a pixel with one neighbour
    start = None
    if touch:
        tq = list(touch.values())[0]
        cand = [p for p in pix if max(abs(p[0] - tq[0]), abs(p[1] - tq[1])) <= 1]
        start = cand[0] if cand else None
    if start is None:
        ones = [p for p in pix if len(nbrs(p)) <= 1]
        start = ones[0] if ones else next(iter(pix))
    chain, seen = [start], {start}
    cur = start
    while True:
        nx_ = [q for q in nbrs(cur) if q not in seen]
        if not nx_:
            break
        # prefer 4-neighbours (straighter chain)
        nx_.sort(key=lambda q: abs(q[0] - cur[0]) + abs(q[1] - cur[1]))
        cur = nx_[0]
        chain.append(cur)
        seen.add(cur)
    return chain


def _chain_end_nodes(chain, touch):
    a, b = chain[0], chain[-1]

    def near(p):
        return min(touch, key=lambda k: max(abs(touch[k][0] - p[0]), abs(touch[k][1] - p[1])))
    u, v = near(a), near(b)
    if u == v and len(touch) >= 2:
        others = [k for k in touch if k != u]
        v = min(others, key=lambda k: max(abs(touch[k][0] - b[0]), abs(touch[k][1] - b[1])))
    return u, v


def prune(G, spur_m=SPUR_M, min_comp_m=MIN_COMP_M, rounds=3):
    import networkx as nx
    for _ in range(rounds):
        drop = [(u, v) for u, v, d in G.edges(data=True)
                if d["length"] < spur_m and (G.degree(u) == 1) != (G.degree(v) == 1)]
        if not drop:
            break
        G.remove_edges_from(drop)
        G.remove_nodes_from([n for n in list(G.nodes) if G.degree(n) == 0])
    for comp in list(nx.connected_components(G)):
        L = sum(d["length"] for _, _, d in G.subgraph(comp).edges(data=True))
        if L < min_comp_m:
            G.remove_nodes_from(comp)
    return merge_degree2(G)


def merge_degree2(G):
    """Contract degree-2 nodes so every edge runs junction/end -> junction/end."""
    changed = True
    while changed:
        changed = False
        for n in list(G.nodes):
            if n not in G or G.degree(n) != 2:
                continue
            nb = list(G.neighbors(n))
            if len(nb) != 2 or nb[0] == nb[1] or G.has_edge(nb[0], nb[1]):
                continue
            a, b = nb
            e1, e2 = G.edges[a, n], G.edges[n, b]
            p1 = _oriented(e1["pts"], (G.nodes[a]["x"], G.nodes[a]["y"]))
            p2 = _oriented(e2["pts"], (G.nodes[n]["x"], G.nodes[n]["y"]))
            pts = np.vstack([p1, p2[1:]])
            L1, L2 = e1["length"], e2["length"]
            p = (e1["p"] * L1 + e2["p"] * L2) / max(L1 + L2, 1e-6)
            w = [x for x in (e1.get("width"), e2.get("width")) if x is not None]
            G.remove_node(n)
            _add_edge(G, a, b, pts, p, float(np.mean(w)) if w else None)
            changed = True
    return G


def _oriented(pts, start):
    pts = np.asarray(pts, float)
    if np.hypot(*(pts[0] - start)) <= np.hypot(*(pts[-1] - start)):
        return pts
    return pts[::-1]


def bridge_gaps(G, prob, st, gap_m=GAP_M, min_p=0.12):
    """Join a dead end to the nearest node of the graph within gap_m when the straight gap is not clearly
    grass (mean path probability along it >= min_p) and the graph route between them is long (or absent)."""
    import networkx as nx
    if G.number_of_nodes() < 2:
        return G
    ids = list(G.nodes)
    P = np.array([(G.nodes[n]["x"], G.nodes[n]["y"]) for n in ids])
    comp = {}
    for ci, cset in enumerate(nx.connected_components(G)):
        for n in cset:
            comp[n] = ci
    added = 0
    for i, n in enumerate(ids):
        if G.degree(n) != 1:
            continue
        d = np.hypot(*(P - P[i]).T)
        d[i] = 1e9
        heading = _end_heading(G, n)
        for j in np.argsort(d)[:8]:
            if d[j] > LONG_GAP_M:
                break
            if d[j] > gap_m:                       # long gaps (under canopy): only straight ahead of the dead end
                if heading is None:
                    continue
                v = (P[j] - P[i]) / d[j]
                if float(np.dot(v, heading)) < math.cos(math.radians(LONG_GAP_DEG)):
                    continue
            m = ids[j]
            if G.has_edge(n, m):
                continue
            if comp[n] == comp[m]:
                try:
                    gl = nx.shortest_path_length(G, n, m, weight="length")
                except nx.NetworkXNoPath:
                    gl = 1e9
                if gl < 3 * d[j] + 20:
                    continue
            ts = np.linspace(0, 1, max(3, int(d[j] / st.res)))
            xs = P[i, 0] + ts * (P[j, 0] - P[i, 0])
            ys = P[i, 1] + ts * (P[j, 1] - P[i, 1])
            r, c = st.xy_to_rc(xs, ys)
            r = np.clip(np.round(r).astype(int), 0, prob.shape[0] - 1)
            c = np.clip(np.round(c).astype(int), 0, prob.shape[1] - 1)
            pm = float(prob[r, c].mean())
            if pm < min_p and d[j] <= gap_m:
                continue
            _add_edge(G, n, m, [P[i], P[j]], pm * 0.8, None)
            G.edges[n, m]["bridge"] = True
            added += 1
            break
    return G


def _end_heading(G, n, back_m=10.0):
    """Unit direction a dead end points to (from ~10 m back along its edge to the end)."""
    nb = list(G.neighbors(n))
    if len(nb) != 1:
        return None
    pts = _oriented(G.edges[n, nb[0]]["pts"], (G.nodes[n]["x"], G.nodes[n]["y"]))
    end = pts[0]
    d = np.hypot(*(pts - end).T)
    k = int(np.searchsorted(d, back_m)) if np.all(np.diff(d) >= 0) else min(len(pts) - 1, int(back_m))
    k = min(max(k, 1), len(pts) - 1)
    v = end - pts[k]
    nv = float(np.hypot(*v))
    return v / nv if nv > 1e-6 else None


def drop_roads(G, road_p=None, st=None, width_m=ROAD_WIDTH_M):
    """Remove edges that are road-wide or that the classifier calls road."""
    drop = []
    for u, v, d in G.edges(data=True):
        if d.get("width") is not None and d["width"] > width_m and d["length"] > 20:
            drop.append((u, v))
        elif road_p is not None and st is not None and len(d["pts"]) >= 2:
            r, c = st.xy_to_rc(d["pts"][:, 0], d["pts"][:, 1])
            r = np.clip(np.round(r).astype(int), 0, road_p.shape[0] - 1)
            c = np.clip(np.round(c).astype(int), 0, road_p.shape[1] - 1)
            if float(np.mean(road_p[r, c])) > 0.5:
                drop.append((u, v))
    G.remove_edges_from(drop)
    G.remove_nodes_from([n for n in list(G.nodes) if G.degree(n) == 0])
    return G


def build_graph(L, model=None, thr=None):
    prob, road = path_prob(L, model)
    if thr is None:
        thr = float((model or {}).get("thr", THR))
    return graph_from_prob(L, prob, road, thr), prob, road


def linear_components(mask, res=1.0, min_len_m=MIN_LINE_M, max_width_m=MAX_LINE_WIDTH_M):
    """Keep connected components that look like paths: a skeleton >= min_len_m long and a mean width
    (area / skeleton length) <= max_width_m. Drops blobs (roofs, drives, bunker rims, shadow clutter)."""
    from skimage.morphology import skeletonize
    m = ndi.binary_closing(mask, iterations=1)
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    if not n:
        return m
    sk = skeletonize(m)
    idx = np.arange(1, n + 1)
    area = np.asarray(ndi.sum(np.ones_like(lab, np.float32), lab, idx)) * res * res
    sl = np.asarray(ndi.sum(sk.astype(np.float32), lab, idx)) * res
    keep = (sl >= min_len_m) & (area / np.maximum(sl, 1e-6) <= max_width_m)
    keep = np.r_[False, keep]
    return keep[lab]


def graph_from_prob(L, prob, road, thr):
    width = L["paved_width_max"]
    G = skeleton_graph(linear_components(prob >= thr, L.st.res), prob, L.st, width=width)
    G = drop_roads(G, road, L.st)
    G = bridge_gaps(G, prob, L.st)
    return prune(G)


def graph_length(G):
    return float(sum(d["length"] for _, _, d in G.edges(data=True)))


def simplify(pts, tol=1.0):
    from shapely.geometry import LineString
    if len(pts) < 3:
        return np.asarray(pts, float)
    return np.asarray(LineString(pts).simplify(tol).coords, float)


def angle(a, b):
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))
