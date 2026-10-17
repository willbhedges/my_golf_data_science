"""Course structure from first principles: every hole (tee complex -> corridor -> green) and the playing order.

    from scene import scene_from_osm
    from solver import solve
    res = solve(scene, card=None)          # card (scorecard/1) is an optional prior; works without one

Model (log-likelihood terms; the weights are fitted on the dev courses only by fit.py -> params.json):

1. Tee complexes. Tee boxes within 22 yds of each other are one complex (a perception scene gives complexes).
2. Hole hypotheses. Every (green g, complex k) 70-700 yds apart is a candidate hole. Its formation score is a
   conditional-logit model over: the length likelihood (par 3/4/5 mixture fitted on dev holes), tee-box axes vs
   the line of play, the share of the line on fairway, a fairway whose two ends sit at the tee and the green
   (dog-legs keep their ends), the line crossing another green, other complexes on the corridor (forward tees)
   and on the far part of the line (another hole's tees), and "startability": a hole starts next to some other
   green (the previous hole) or the clubhouse, while forward-tee complexes sit in the middle of a corridor.
3. Sequence. A round is a path through N of the M greens (N = 9 / 18 / 27 / 36). Moving from green i to hole
   (k, j) adds the walk green i -> nearest box of k (log-normal, median ~60 yds, broad tail; when cart paths
   join them directly a longer walk stays plausible). The complex choice is summed out inside each transition,
   a complex can start only one hole (Lagrangian prices, subgradient until no complex is used twice).
   Anchors: tee 1 and green N near the clubhouse H; for 18 holes also green 9 and tee 10 (returning nines; the
   9 -> 10 walk may go through H). H is latent: tagged / detected clubhouse candidates, buildings by car parks
   and "hubs" where greens and hole starts meet, each with a prior; marginalised.
4. Inference: exact forward-backward over subsets (Held-Karp in log space, one BLAS matmul per layer): the
   partition function, the MAP route (Viterbi) and exact marginals P(green j is hole k). A hole's confidence is
   that marginal x the posterior of its tee complex given the route. Greens off the route are practice greens.
5. Par from the length (par posterior with a prior on the number of par 3s / 5s, i.e. total par ~70-72); hole
   numbers from the route; direction of play from tee -> green. A card adds a position term (hole k vs card k).
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

try:
    from shapely import contains_xy, prepare
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import unary_union
except Exception:                                                   # noqa: BLE001
    Polygon = None

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------- parameters (fit.py on dev)
PAR_MU = {3: 172.0, 4: 370.0, 5: 498.0}
PAR_SD = {3: 32.0, 4: 55.0, 5: 55.0}
PAR_PI = {3: 0.23, 4: 0.56, 5: 0.21}
LEN_FLOOR = 0.06
L_MIN, L_MAX = 70.0, 700.0
WALK_MED, WALK_SIG, WALK_TAIL = 60.0, 0.55, 0.05     # green edge -> next tee: log-normal + tail (uniform to 800)
PATH_MED, PATH_SIG = 130.0, 0.6                       # ... along a cart path that joins them directly
CH_MED, CH_SIG, CH_TAIL = 70.0, 0.75, 0.15            # anchor (tee 1, greens 9 / 18, tee 10) to the clubhouse
CX_LINK = 22.0
CX_CHAIN = 75.0
CORR_FWD, CORR_PERP = 0.62, 25.0
COVER_FWD, COVER_PERP = 0.5, 20.0
BEHIND_PERP = 16.0
COVER_BACK = 0.3                     # complexes a hole "uses" (its forward tees): exclusive
TOPK = 8
NOT_HOLE = 4.0                                        # log-odds that a green with no route is a practice green
TURN_VIA_H = 0.65
FORM_W = dict(chain=2.0, fw_x=2.0, length=1.0, align=0.6, fw_cov=1.0, fw_end=3.0, cross_green=3.0, fwd=0.5, far=1.5, start=0.6)
TEMP = 1.0                                            # posterior temperature (calibrated on dev)
LAGR_ITERS = 12
TFEATS = ("walk", "dist", "cos_prev", "cos_next", "path")
TRANS_W = dict(walk=1.0, dist=0.0, cos_prev=0.0, cos_next=0.0, path=1.0)
TURN_W = dict(walk=0.3, dist=0.0, cos_prev=0.0, cos_next=0.0, path=0.3)
ANCHOR_W = dict(t1=1.0, g18=1.0, g9=1.0, t10=1.0, t1_d=0.0, g18_d=0.0, g9_d=0.0, t10_d=0.0)


def load_params(path=os.path.join(HERE, "params.json")):
    global FORM_W, TEMP, NOT_HOLE, TURN_VIA_H, TRANS_W, TURN_W, ANCHOR_W
    if os.path.exists(path):
        p = json.load(open(path))
        TURN_W = dict(TURN_W, **p.get("turn_w", {}))
        ANCHOR_W = dict(ANCHOR_W, **p.get("anchor_w", {}))
        FORM_W = dict(FORM_W, **p.get("form_w", {}))
        TRANS_W = dict(TRANS_W, **p.get("trans_w", {}))
        TEMP = p.get("temp", TEMP)
        NOT_HOLE = p.get("not_hole", NOT_HOLE)
        TURN_VIA_H = p.get("turn_via_h", TURN_VIA_H)


load_params()


def _ln_lognorm(d, med, sig, tail, tmax=800.0):
    d = np.maximum(np.asarray(d, float), 1.0)
    core = np.exp(-0.5 * ((np.log(d) - math.log(med)) / sig) ** 2) / (d * sig * math.sqrt(2 * math.pi))
    return np.log((1 - tail) * core + tail / tmax)


def length_loglik(L):
    """(log p(L | hole) - log uniform(L_MIN..L_MAX), par posterior 3 x n)."""
    L = np.asarray(L, float)
    comps = np.stack([PAR_PI[p] * np.exp(-0.5 * ((L - PAR_MU[p]) / PAR_SD[p]) ** 2) / (PAR_SD[p] * math.sqrt(2 * math.pi))
                      for p in (3, 4, 5)])
    dens = (1 - LEN_FLOOR) * comps.sum(0) + LEN_FLOOR / (L_MAX - L_MIN)
    return np.log(dens * (L_MAX - L_MIN)), comps / np.maximum(comps.sum(0), 1e-300)


def walk_ll(d):
    return _ln_lognorm(d, WALK_MED, WALK_SIG, WALK_TAIL)


def path_ll(d):
    return _ln_lognorm(d, PATH_MED, PATH_SIG, WALK_TAIL)


def anchor_ll(d):
    return _ln_lognorm(d, CH_MED, CH_SIG, CH_TAIL, 1500.0)


def _angdiff(a, b):
    """Undirected angle difference in [0, pi/2]."""
    return np.abs((np.asarray(a) - b + math.pi / 2) % math.pi - math.pi / 2)


def _lse(a, axis=None):
    a = np.asarray(a, float)
    m = np.max(a, axis=axis, keepdims=True)
    m = np.where(np.isfinite(m), m, 0.0)
    r = np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True)) + m
    return np.squeeze(r, axis=axis) if axis is not None else float(r.ravel()[0])


# ----------------------------------------------------------------------------- tee complexes
def complexes(sc, link=CX_LINK):
    """Tee boxes -> complexes (single linkage within `link` yds). Perception tees already are complexes (they carry
    `box_xy`). -> [{boxes: [tee idx], xy (n x 2), c, axis, axis_w, conf, id}]"""
    T = np.array([t["c"] for t in sc.tees], float).reshape(-1, 2)
    n = len(T)
    if n == 0:
        return []
    if sc.source == "perception":
        out = []
        for i, t in enumerate(sc.tees):
            xy = np.array(t.get("box_xy") or [t["c"]], float).reshape(-1, 2)
            out.append(dict(id=t["id"], boxes=[i], xy=xy, c=np.asarray(t["c"], float), axis=t.get("axis"),
                            axis_w=min(1.0, max(0.0, (t.get("elong", 1.0) - 1.2) / 0.8)) if t.get("axis") is not None else 0.0,
                            conf=t.get("conf", 1.0)))
        return out
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    d = np.hypot(T[:, None, 0] - T[None, :, 0], T[:, None, 1] - T[None, :, 1])
    for i, j in zip(*np.nonzero(np.triu(d < link, 1))):
        par[find(i)] = find(j)
    # forward tees: boxes up to CX_CHAIN yds apart along a shared axis (each box's long axis, when it has one,
    # points at the other within 15 deg and the two axes agree within 25 deg)
    ax = [t.get("axis") if (t.get("axis") is not None and t.get("elong", 1) > 1.4) else None for t in sc.tees]
    for i, j in zip(*np.nonzero(np.triu((d >= link) & (d < CX_CHAIN), 1))):
        if ax[i] is None or ax[j] is None:
            continue
        dirn = math.atan2(T[j, 1] - T[i, 1], T[j, 0] - T[i, 0])
        if _angdiff(ax[i], dirn) < math.radians(15) and _angdiff(ax[j], dirn) < math.radians(15) and \
                _angdiff(ax[i], ax[j]) < math.radians(25):
            par[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    out = []
    for gi, idx in enumerate(groups.values()):
        xy = T[idx]
        # axis: elongated boxes' axes (doubled-angle mean, weighted by elongation), else the spread of the boxes
        num = np.zeros(2)
        for i in idx:
            t = sc.tees[i]
            if t.get("axis") is not None and t.get("elong", 1) > 1.3:
                wgt = min(1.0, (t["elong"] - 1.3) / 0.7)
                num += wgt * np.array([math.cos(2 * t["axis"]), math.sin(2 * t["axis"])])
        ax, aw = None, 0.0
        if len(idx) >= 2:
            c = xy - xy.mean(0)
            w, v = np.linalg.eigh(c.T @ c)
            ext = math.sqrt(max(w[1], 0) / len(idx)) * 2
            if ext > 10 and w[1] > 4 * max(w[0], 1e-9):
                ang = math.atan2(v[1, 1], v[0, 1])
                num += 2.0 * min(1.0, ext / 25) * np.array([math.cos(2 * ang), math.sin(2 * ang)]) * \
                    max(1.0, np.linalg.norm(num))
        if np.linalg.norm(num) > 1e-9:
            ax = 0.5 * math.atan2(num[1], num[0])
            aw = float(min(1.0, np.linalg.norm(num)))
        out.append(dict(id=f"c{gi}", boxes=[int(i) for i in idx], xy=xy, c=xy.mean(0), axis=ax, axis_w=aw,
                        conf=max(sc.tees[i].get("conf", 1.0) for i in idx)))
    return out


# ----------------------------------------------------------------------------- geometry prep
class Geo:
    def __init__(self, sc):
        if Polygon is None:
            raise RuntimeError("shapely is required")
        self.sc = sc
        self.G = np.array([g["c"] for g in sc.greens], float).reshape(-1, 2)
        self.gr_r = np.array([math.sqrt(max(g.get("area", 400.0), 50.0) / math.pi) for g in sc.greens])
        self.cx = complexes(sc)
        self.C = np.array([c["c"] for c in self.cx], float).reshape(-1, 2)
        self.fw = None
        self.greens_u = None
        self.fw_ends = []
        polys = []
        for f in sc.fairways:
            if f.get("ring") is not None and len(f["ring"]) >= 4:
                p = Polygon(f["ring"]).buffer(0)
                if p.area > 50:
                    polys.append(p)
                    self.fw_ends.append(tuple(f["ends"]) if f.get("ends") else _poly_ends(f["ring"]))
            elif f.get("line") is not None:
                ln = np.asarray(f["line"])
                polys.append(LineString(ln).buffer(18))
                self.fw_ends.append((ln[0], ln[-1]))
        self.fw_polys = []
        for p in polys:
            q = p.buffer(6)
            prepare(q)
            r = np.asarray(p.minimum_rotated_rectangle.exterior.coords)[:4]
            e1, e2 = r[1] - r[0], r[2] - r[1]
            e = e1 if np.hypot(*e1) >= np.hypot(*e2) else e2
            el = max(np.hypot(*e1), np.hypot(*e2)) / max(1.0, min(np.hypot(*e1), np.hypot(*e2)))
            self.fw_polys.append((q, math.atan2(e[1], e[0]), el))
        if polys:
            self.fw = unary_union(polys).buffer(8)
            prepare(self.fw)
        self.gpolys = []
        for g in sc.greens:
            if g.get("ring") is not None and len(g["ring"]) >= 4:
                p = Polygon(g["ring"]).buffer(3)
            else:
                p = Point(*g["c"]).buffer(max(8.0, math.sqrt(g.get("area", 400) / math.pi)))
            self.gpolys.append(p)
        if self.gpolys:
            self.greens_u = unary_union(self.gpolys)
            prepare(self.greens_u)
        self.has_fw = self.fw is not None and len(sc.fairways) >= 5
        self.cones = [[] for _ in sc.greens]
        if self.has_fw:
            for gi, gp in enumerate(self.gpolys):
                for fi, f in enumerate(sc.fairways):
                    if f.get("ring") is None or len(f["ring"]) < 4:
                        continue
                    fp = Polygon(f["ring"]).buffer(0)
                    if fp.distance(gp) > 35:
                        continue
                    r = np.asarray(f["ring"], float)
                    dg = np.hypot(*(r - self.G[gi]).T)
                    if dg.max() < 60:
                        continue
                    far = r[dg >= dg.max() - 0.35 * (dg.max() - dg.min())]
                    e_f = r[np.argmax(dg)]
                    near = r[dg <= dg.min() + 0.35 * (dg.max() - dg.min())].mean(0)
                    mid = far.mean(0)
                    d = e_f - (mid + near) / 2
                    if far.shape[0] >= 3:
                        c = far - far.mean(0)
                        _, _, vt = np.linalg.svd(c, full_matrices=False)
                        ax = vt[0] if np.dot(vt[0], d) > 0 else -vt[0]
                        el = 1.0
                        d = 0.5 * d / max(np.hypot(*d), 1e-9) + 0.5 * ax
                    d = d / max(np.hypot(*d), 1e-9)
                    self.cones[gi].append((e_f, d))
        self.fw_ends = np.array(self.fw_ends, float).reshape(-1, 2, 2)
        self.paths = PathGraph(sc.paths) if sc.paths else None

    def on_fairway(self, xy):
        if self.fw is None:
            return np.zeros(len(xy), bool)
        return contains_xy(self.fw, xy[:, 0], xy[:, 1])


def _poly_ends(ring):
    """The two extreme points of a polygon along its long axis (approximate centreline ends)."""
    r = np.asarray(ring, float)
    c = r.mean(0)
    _, _, vt = np.linalg.svd(r - c, full_matrices=False)
    pr = (r - c) @ vt[0]
    i, j = int(np.argmin(pr)), int(np.argmax(pr))
    return c + (r[i] - c) * 0.85, c + (r[j] - c) * 0.85


class PathGraph:
    """Cart paths as a graph (vertices of every polyline densified to 25 yds, consecutive vertices joined, vertices
    within 10 yds snapped together). Distances from a point: shortest route from the path vertices within 35 yds of
    it (plus that access leg); inf when not connected."""

    def __init__(self, lines, snap=10.0):
        from scipy.sparse import coo_matrix
        from scipy.spatial import cKDTree
        pts, ei, ej, ew = [], [], [], []
        for ln in lines:
            ln = np.asarray(ln, float)
            if len(ln) < 2:
                continue
            dense = [ln[0]]
            for a, b in zip(ln[:-1], ln[1:]):
                L = float(np.hypot(*(b - a)))
                k = max(1, int(math.ceil(L / 25)))
                for s in range(1, k + 1):
                    dense.append(a + (b - a) * s / k)
            base = len(pts)
            pts += dense
            for i in range(len(dense) - 1):
                ei.append(base + i)
                ej.append(base + i + 1)
                ew.append(float(np.hypot(*(dense[i + 1] - dense[i]))) + 0.01)
        self.P = np.array(pts, float).reshape(-1, 2)
        n = len(self.P)
        self.A = None
        if n:
            self.tree = cKDTree(self.P)
            for i, j in self.tree.query_pairs(snap):
                ei.append(i)
                ej.append(j)
                ew.append(float(np.hypot(*(self.P[i] - self.P[j]))) + 0.1)
            self.A = coo_matrix((ew + ew, (ei + ej, ej + ei)), shape=(n, n)).tocsr()

    def from_points(self, srcs, reach=35.0):
        from scipy.sparse.csgraph import dijkstra
        out = []
        for s in srcs:
            idx = self.tree.query_ball_point(s, reach)
            if not idx:
                out.append(None)
                continue
            dd = dijkstra(self.A, indices=idx, limit=900.0)
            leg = np.hypot(*(self.P[idx] - s).T)
            out.append(np.min(dd + leg[:, None], axis=0))
        return out

    def to_points(self, dist_row, pts, reach=35.0):
        if dist_row is None:
            return np.full(len(pts), np.inf)
        res = []
        for p in pts:
            idx = self.tree.query_ball_point(p, reach)
            if not idx:
                res.append(np.inf)
                continue
            res.append(float(np.min(dist_row[idx] + np.hypot(*(self.P[idx] - p).T))))
        return np.array(res)


# ----------------------------------------------------------------------------- hole hypotheses
FEATS = ("length", "align", "chain", "chain_neg", "p3_fw", "fw_cov", "fw_x", "fw_end", "cross_green", "fwd", "far", "start")


def features(sc, geo, clubs=()):
    """Features of every (green, complex) pair 70-700 yds apart -> [{gi, k, tee (back box), D, ppar, f}]."""
    G, C, cx = geo.G, geo.C, geo.cx
    nG, nC = len(G), len(C)
    if not nG or not nC:
        return []
    pairs = []
    for gi in range(nG):
        for k in range(nC):
            xy = cx[k]["xy"]
            dd = np.hypot(*(xy - G[gi]).T)
            b = int(np.argmax(dd))
            D = float(dd[b])
            if L_MIN <= D <= L_MAX:
                pairs.append((gi, k, xy[b], D))
    if not pairs:
        return []
    # canonical hypotheses: a complex with another one behind it on the line to the same green is a forward tee of
    # that hole -> only the back-most complex starts the hypothesis (its corridor covers the forward ones)
    canon = []
    for gi, k, t, D in pairs:
        u = (G[gi] - t) / D
        rel = C - t
        s = rel @ u / D
        perp = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
        behind = (s < -0.03) & (s > -0.4) & (perp < BEHIND_PERP) & (np.hypot(*(C - G[gi]).T) <= L_MAX)
        behind[k] = False
        if not behind.any() or True:
            canon.append((gi, k, t, D))
    pairs = canon
    P = len(pairs)
    tee = np.array([p[2] for p in pairs])
    gxy = G[[p[0] for p in pairs]]
    D = np.array([p[3] for p in pairs])
    v = gxy - tee
    u = v / D[:, None]
    ang = np.arctan2(u[:, 1], u[:, 0])
    ll_len, ppar = length_loglik(D)
    al = np.zeros(P)
    for i, (gi, k, _, _) in enumerate(pairs):
        c = cx[k]
        if c["axis"] is not None and c["axis_w"] > 0:
            dd = float(_angdiff(c["axis"], ang[i]))
            pc = 0.8 * math.exp(-0.5 * (dd / math.radians(10)) ** 2) / (math.radians(10) * math.sqrt(math.pi / 2)) \
                + 0.2 / (math.pi / 2)
            al[i] = math.log(pc * math.pi / 2) * c["axis_w"]
    s_line = np.linspace(0.25, 0.85, 13)
    pts = tee[:, None, :] + s_line[None, :, None] * v[:, None, :]
    cov = geo.on_fairway(pts.reshape(-1, 2)).reshape(P, -1).mean(1) if geo.has_fw else np.zeros(P)
    # in a fairway running along the line vs across it (crossing another hole's fairway)
    fal = np.zeros((P, len(s_line)), bool)
    fx = np.zeros((P, len(s_line)), bool)
    if geo.has_fw:
        flat = pts.reshape(-1, 2)
        for poly, fax, fel in geo.fw_polys:
            inn = contains_xy(poly, flat[:, 0], flat[:, 1]).reshape(P, -1)
            if not inn.any():
                continue
            mis = _angdiff(fax, ang) > math.radians(35)
            if fel < 1.6:
                mis = np.zeros(P, bool)
            fal |= inn & ~mis[:, None]
            fx |= inn & mis[:, None]
    fx = fx & ~fal
    fal = fal.mean(1)
    fx = fx.mean(1)
    p45 = ppar[1] + ppar[2]
    fe = np.zeros(P)
    if geo.has_fw and len(geo.fw_ends):
        e = geo.fw_ends
        for i in range(P):
            t, g = tee[i], gxy[i]
            da = np.minimum(np.hypot(*(e[:, 0] - t).T) + np.hypot(*(e[:, 1] - g).T),
                            np.hypot(*(e[:, 1] - t).T) + np.hypot(*(e[:, 0] - g).T))
            # fairway fit: tee -> near end -> far end -> green barely longer than the straight line, and the
            # fairway spanning a good share of the hole (sum over the fairways that fit; dog-legs bend but fit)
            dn1 = np.hypot(*(e[:, 0] - t).T)
            dn2 = np.hypot(*(e[:, 1] - t).T)
            near = np.where((dn1 <= dn2)[:, None], e[:, 0], e[:, 1])
            farp = np.where((dn1 <= dn2)[:, None], e[:, 1], e[:, 0])
            Lf = np.hypot(*(farp - near).T)
            det = (np.hypot(*(near - t).T) + Lf + np.hypot(*(g - farp).T)) / D[i]
            fe[i] = min(1.0, float((Lf / D[i] * np.exp(-np.maximum(0.0, det - 1.02) / 0.05)).sum()))
    chain = np.zeros(P)
    has_cone = np.zeros(P)
    if geo.has_fw:
        for i, (gi, k, _, _) in enumerate(pairs):
            if not geo.cones[gi]:
                continue
            hit = 0.0
            for e_f, d in geo.cones[gi]:
                w = cx[k]["xy"] - e_f
                along = w @ d
                lat = np.abs(w[:, 0] * d[1] - w[:, 1] * d[0])
                ok = (along > -25) & (along < 320)
                if ok.any():
                    hit = max(hit, float((lat[ok] < 25 + 0.3 * np.maximum(along[ok], 0)).any()))
            chain[i] = hit
            has_cone[i] = 1.0
    s_x = np.linspace(0.08, 0.85, 28)
    xs = tee[:, None, :] + s_x[None, :, None] * v[:, None, :]
    inside = contains_xy(geo.greens_u, xs[..., 0].ravel(), xs[..., 1].ravel()).reshape(P, -1)
    cg = np.zeros(P)
    for i in np.nonzero(inside.any(1))[0]:
        own = contains_xy(geo.gpolys[pairs[i][0]], xs[i, :, 0], xs[i, :, 1])
        cg[i] = float((inside[i] & ~own).any())
    fwd = np.zeros(P)
    far = np.zeros(P)
    cover = []
    for i, (gi, k, _, _) in enumerate(pairs):
        rel = C - tee[i]
        s = rel @ u[i] / D[i]
        perp = np.abs(rel[:, 0] * u[i, 1] - rel[:, 1] * u[i, 0])
        m = np.ones(nC, bool)
        m[k] = False
        fwd[i] = float(((s > 0.03) & (s < CORR_FWD) & (perp < CORR_PERP) & m).sum())
        cover.append(sorted({k} | set(np.nonzero((s > 0.0) & (s < COVER_FWD) & (perp < COVER_PERP))[0].tolist())))
        far[i] = float(((s >= 0.68) & (s < 0.95) & (perp < 14) & m).sum())
    start = np.zeros(P)
    Gr = geo.gr_r
    base = float(walk_ll(160.0))
    for i, (gi, k, _, _) in enumerate(pairs):
        xy = cx[k]["xy"]
        dg = np.hypot(G[:, None, 0] - xy[None, :, 0], G[:, None, 1] - xy[None, :, 1]).min(1) - Gr
        dg[gi] = 1e9
        best = float(walk_ll(max(dg.min(), 1.0)))
        for h in clubs:
            best = max(best, float(anchor_ll(np.hypot(*(xy - h["c"]).T).min())) - 1.0)
        start[i] = best - base
    out = []
    for i, (gi, k, t, d) in enumerate(pairs):
        out.append(dict(gi=gi, k=k, tee=t, D=d, ppar=ppar[:, i], cover=cover[i],
                        f=dict(length=float(ll_len[i]), align=float(al[i]),
                               fw_cov=float((fal[i] - 0.4) * p45[i]) if geo.has_fw else 0.0,
                               fw_x=-float(fx[i]), chain=float(chain[i] * p45[i]),
                               chain_neg=-float(has_cone[i] * (1 - chain[i]) * p45[i]),
                               p3_fw=-float(has_cone[i] * (1 - p45[i])),
                               fw_end=float((fe[i] - 0.3) * p45[i]) if geo.has_fw else 0.0, cross_green=-cg[i],
                               fwd=math.log1p(fwd[i]), far=-far[i], start=max(-4.0, min(4.0, start[i])))))
    return out


def hypotheses(sc, geo=None, topk=TOPK, w=None, clubs=None):
    """Per green: up to `topk` hole hypotheses sorted by formation log-score."""
    w = dict(FORM_W, **(w or {}))
    geo = geo or Geo(sc)
    clubs = sc.clubhouse if clubs is None else clubs
    per = [[] for _ in range(len(geo.G))]
    for h in features(sc, geo, clubs):
        h["score"] = sum(w.get(k, 0.0) * h["f"][k] for k in FEATS)
        per[h["gi"]].append(h)
    for i in range(len(per)):
        per[i].sort(key=lambda r: -r["score"])
        per[i] = per[i][:topk]
    return per, geo


# ----------------------------------------------------------------------------- clubhouse candidates
def hub_candidates(sc, geo, hyps, k=4):
    """Points where greens and hole starts meet (the clubhouse of returning nines: greens 9 / 18, tees 1 / 10)."""
    starts = np.array([h["tee"] for hs in hyps for h in hs[:1]]).reshape(-1, 2)
    G = geo.G
    cand = []
    for p in list(G) + list(starts):
        ng = int((np.hypot(*(G - p).T) < 150).sum())
        nt = int((np.hypot(*(starts - p).T) < 150).sum()) if len(starts) else 0
        cand.append((min(ng, 3) + min(nt, 3), p))
    cand.sort(key=lambda r: -r[0])
    out = []
    for s, p in cand:
        if any(np.hypot(*(p - q["c"])) < 150 for q in out):
            continue
        out.append(dict(c=np.asarray(p, float), w=0.04 * s / 6 + 0.005, how="hub"))
        if len(out) >= k:
            break
    return out


# ----------------------------------------------------------------------------- the DP
_LAYERS = {}


def _popcount_layers(M, N):
    key = (M, N)
    if key not in _LAYERS:
        masks = np.arange(1 << M, dtype=np.int64)
        pc = np.zeros(1 << M, np.int8)
        for b in range(M):
            pc += ((masks >> b) & 1).astype(np.int8)
        _LAYERS.clear()
        _LAYERS[key] = [np.nonzero(pc == k)[0] for k in range(N + 1)]
    return _LAYERS[key]


def route_dp(trans, start, end, N, turn=None, pos=None, viterbi=True, marginals=True, soft=True):
    """Soft and hard Held-Karp over paths of N distinct nodes out of M (M <= ~20).

    trans[i, j]  log-weight of moving from node i to node j        (M x M, very negative = impossible)
    start[j]     log-weight of j as the first node;  end[i] of i as the last
    turn[i, j]   replaces trans at the move from position 9 to 10 when given
    pos[j, k]    log-weight of node j at position k (0-based), e.g. a card prior
    -> dict(logZ, best (node list), best_score, marg (M x N): P(node j at position k))."""
    M = trans.shape[0]
    layers = _popcount_layers(M, N)
    NEG = -1e30
    bits = np.arange(M)
    alpha = np.full((1 << M, M), NEG, np.float32)
    for j in range(M):
        alpha[1 << j, j] = start[j] + (pos[j, 0] if pos is not None else 0.0)
    vit = alpha.copy() if viterbi else None
    for k in range(1, N):
        tr = turn if (turn is not None and k == 9) else trans
        idx = layers[k]
        bit = ((idx[:, None] >> bits[None, :]) & 1).astype(bool)
        new = idx[:, None] | (1 << bits)[None, :]
        rows, cols = np.nonzero(~bit)
        if not soft:
            A = None
        else:
            A = alpha[idx].astype(np.float64)
        if soft:
            am = A.max(1, keepdims=True)
            tm = tr.max(0, keepdims=True)
            eT = np.exp(np.clip(tr - tm, -700, 0))
            B = np.log(np.maximum(np.exp(A - am) @ eT, 1e-300)) + am + tm
            if pos is not None:
                B = B + pos[:, k][None, :]
            alpha[new[rows, cols], cols] = B[rows, cols]
        if viterbi:
            V = vit[idx]
            best = np.full((len(idx), M), NEG, np.float32)
            trf = tr.astype(np.float32)
            for i in range(M):
                np.maximum(best, V[:, i:i + 1] + trf[i][None, :], out=best)
            if pos is not None:
                best = best + pos[:, k][None, :].astype(np.float32)
            vit[new[rows, cols], cols] = best[rows, cols]
    last = layers[N]
    if soft:
        fin = alpha[last].astype(np.float64) + end[None, :]
        logZ = _lse(fin.ravel())
    else:
        logZ = float((vit[last].astype(np.float64) + end[None, :]).max())
    out = dict(logZ=float(logZ))
    if marginals and soft:
        beta = np.full((1 << M, M), NEG, np.float32)
        beta[last] = np.broadcast_to(end[None, :], (len(last), M))
        for k in range(N - 1, 0, -1):
            tr = turn if (turn is not None and k == 9) else trans
            idx = layers[k]
            bit = ((idx[:, None] >> bits[None, :]) & 1).astype(bool)
            new = idx[:, None] | (1 << bits)[None, :]
            nb = np.where(bit, NEG, beta[np.where(bit, idx[:, None], new), bits[None, :]]).astype(np.float64)
            if pos is not None:
                nb = nb + pos[:, k][None, :]
            nm = nb.max(1, keepdims=True)
            tm = tr.max(1, keepdims=True)
            eT = np.exp(np.clip(tr - tm, -700, 0))
            Bk = np.log(np.maximum(np.exp(nb - nm) @ eT.T, 1e-300)) + nm + tm.T
            beta[idx] = np.where(bit, Bk, NEG)
        marg = np.zeros((M, N))
        for k in range(N):
            idx = layers[k + 1]
            lp = alpha[idx].astype(np.float64) + beta[idx] - logZ
            marg[:, k] = np.exp(np.clip(lp, -700, 0)).sum(0)
        out["marg"] = marg
    if viterbi:
        fin_v = vit[last].astype(np.float64) + end[None, :]
        r, c = np.unravel_index(int(np.argmax(fin_v)), fin_v.shape)
        mask, j = int(last[r]), int(c)
        seq = [j]
        score = float(fin_v[r, c])
        for k in range(N - 1, 0, -1):
            tr = turn if (turn is not None and k == 9) else trans
            prev = mask & ~(1 << j)
            cand = vit[prev].astype(np.float64) + tr[:, j]
            if pos is not None:
                cand = cand + pos[j, k]
            cand[[i for i in range(M) if not (prev >> i) & 1]] = NEG
            i = int(np.argmax(cand))
            seq.append(i)
            mask, j = prev, i
        out.update(best=seq[::-1], best_score=score)
    return out


# ----------------------------------------------------------------------------- the solver
def n_holes_guess(hyps, n_cx=None, thr=1.0, return_scores=False):
    """9 / 18 / 27 / 36 from the number of greens that get a decent hole in an exclusive green -> complex
    assignment (practice greens and greens without a tee drop out)."""
    from scipy.optimize import linear_sum_assignment
    nG = len(hyps)
    n_cx = n_cx or (1 + max((h["k"] for hs in hyps for h in hs), default=0))
    S = np.full((nG, n_cx + nG), -50.0)
    for gi, hs in enumerate(hyps):
        for h in hs:
            S[gi, h["k"]] = h["score"]
        S[gi, n_cx + gi] = thr
    r, c = linear_sum_assignment(-S)
    good = int(sum(1 for gi, k in zip(r, c) if k < n_cx))
    asg = np.full(nG, -50.0)
    for gi, k in zip(r, c):
        asg[gi] = S[gi, k] if k < n_cx else -50.0 + (hyps[gi][0]["score"] if hyps[gi] else -50.0) * 0.01
    n = 36 if good >= 34 else 27 if good >= 26 else 18 if good >= 14 else (9 if good >= 5 else max(1, good))
    return (n, asg) if return_scores else n


def card_info(card):
    """(pars, yards) per hole from a scorecard/1 dict (yards = the longest tee set), or (None, None)."""
    if not card:
        return None, None
    pars = card.get("par") or card.get("pars")
    best = None
    for name, t in (card.get("tee_sets") or {}).items():
        y = t.get("yards") if isinstance(t, dict) else t
        if y and (best is None or sum(v or 0 for v in y) > sum(v or 0 for v in best)):
            best = y
    return pars, best or card.get("yards")


def transition_features(geo, hyps, keep, cxk, use_paths=True):
    """F[a, b, h, :] for the move green keep[a] -> hypothesis h of green keep[b]:
    walk      log-normal walk log-lik of the distance green edge -> nearest box of the complex
    dist      that distance / 100 yds
    cos_prev  cos(direction of play of a's hole, walk direction): players walk on, not back down the hole
    cos_next  cos(walk direction, direction of play of b's hole h): tees are reached from behind
    path      cart paths join a to the complex directly (route <= 2.2 x straight + 80): path log-lik gain"""
    G = geo.G
    Mk, K = cxk.shape
    nC = len(geo.cx)
    kp = np.asarray(keep)
    dgc = np.zeros((Mk, nC))
    vec = np.zeros((Mk, nC, 2))
    for k, c in enumerate(geo.cx):
        xy = c["xy"]
        dd = np.hypot(G[kp][:, None, 0] - xy[None, :, 0], G[kp][:, None, 1] - xy[None, :, 1])
        j = dd.argmin(1)
        dgc[:, k] = dd[np.arange(Mk), j]
        vec[:, k] = xy[j] - G[kp]
    dgc = np.maximum(dgc - geo.gr_r[kp][:, None], 1.0)
    wu = vec / np.maximum(np.hypot(vec[..., 0], vec[..., 1]), 1e-6)[..., None]
    dprev = np.zeros((Mk, 2))
    for a, g in enumerate(kp):
        hs = hyps[g]
        if not hs:
            continue
        sc = np.array([h["score"] for h in hs])
        p = np.exp(sc - sc.max())
        p /= p.sum()
        v = sum(pi * (G[g] - h["tee"]) / max(h["D"], 1.0) for pi, h in zip(p, hs))
        dprev[a] = v / max(np.hypot(*v), 1e-6)
    F = np.zeros((Mk, Mk, K, len(TFEATS)))
    ck = np.maximum(cxk, 0)
    dist = dgc[:, ck]
    F[..., 0] = walk_ll(dist)
    F[..., 1] = dist / 100.0
    F[..., 2] = np.einsum("abhx,ax->abh", wu[:, ck], dprev)
    dnext = np.zeros((Mk, K, 2))
    for b, g in enumerate(kp):
        for h, x in enumerate(hyps[g][:K]):
            dnext[b, h] = (G[g] - x["tee"]) / max(x["D"], 1.0)
    F[..., 3] = np.einsum("abhx,bhx->abh", wu[:, ck], dnext)
    if use_paths and geo.paths is not None and len(geo.paths.P):
        pg = geo.paths.from_points([G[g] for g in kp])
        pgc = np.full((Mk, nC), np.inf)
        for a in range(Mk):
            if pg[a] is None:
                continue
            for k, c in enumerate(geo.cx):
                pgc[a, k] = geo.paths.to_points(pg[a], c["xy"]).min()
        ok = np.isfinite(pgc) & (pgc < 2.2 * dgc + 80)
        gain = np.where(ok, np.maximum(0.0, np.logaddexp(walk_ll(dgc) + math.log(0.5),
                                                         path_ll(np.where(ok, pgc, 1e3)) + math.log(0.5)) - walk_ll(dgc)), 0.0)
        F[..., 4] = gain[:, ck]
    return F


class Problem:
    """Padded arrays over the kept greens (nodes) and their hypotheses (K per node):
    form[b, h], cxk[b, h] (complex index, -1 = padding), wl[a, b, h] walk log-lik green a -> hypothesis h of b."""

    def __init__(self, sc, hyps, geo, keep, use_paths=True):
        self.sc, self.hyps, self.geo, self.keep = sc, hyps, geo, keep
        G = geo.G
        self.hk = [hyps[g] for g in keep]
        Mk = len(keep)
        K = max(1, max(len(h) for h in self.hk))
        self.K = K
        self.form = np.full((Mk, K), -1e4)
        self.cxk = np.full((Mk, K), -1, int)
        nC = len(geo.cx)
        self.cov = np.zeros((Mk, K, nC + 1))
        self.Phi = np.zeros((Mk, K, len(FEATS)))
        self.pad = np.full((Mk, K), -1e4)
        for b, hs in enumerate(self.hk):
            for h, x in enumerate(hs):
                self.form[b, h] = x["score"]
                self.cxk[b, h] = x["k"]
                self.cov[b, h, x["cover"]] = 1.0
                self.Phi[b, h] = [x["f"][k] for k in FEATS]
                self.pad[b, h] = 0.0
        self.F = transition_features(geo, hyps, keep, self.cxk, use_paths)
        self.path_used = bool(use_paths and geo.paths is not None)
        self.wl = self.F @ np.array([TRANS_W[k] for k in TFEATS])          # (Mk, Mk, K)
        self.wd = self.F[..., TFEATS.index("dist")] * 100.0

    def anchors(self, c):
        """(start log-lik per hypothesis (Mk, K), end log-lik per green (Mk,)) for clubhouse point c."""
        G = self.geo.G
        dc = np.array([np.hypot(*(cx["xy"] - c).T).min() for cx in self.geo.cx])
        dg = np.maximum(np.hypot(*(G[self.keep] - c).T) - self.geo.gr_r[self.keep], 1.0)
        ck = np.maximum(self.cxk, 0)
        st = np.stack([anchor_ll(dc)[ck], np.minimum(dc[ck], 1500.0) / 100.0], -1)          # (Mk, K, 2)
        en = np.stack([anchor_ll(dg), np.minimum(dg, 1500.0) / 100.0], -1)                    # (Mk, 2)
        return st, en


def solve(sc, card=None, n_holes=None, use_paths=True, use_clubhouse=True, temp=None, form_w=None, topk=TOPK,
          max_greens=19, return_debug=False):
    temp = temp or TEMP
    clubs = list(sc.clubhouse) if use_clubhouse else []
    hyps, geo = hypotheses(sc, topk=topk, w=form_w, clubs=clubs)
    pars, yards = card_info(card)
    n_guess, asg = n_holes_guess(hyps, len(geo.C), return_scores=True)
    N = n_holes or (len(pars) if pars else (len(yards) if yards else n_guess))
    nG = len(sc.greens)
    if nG == 0 or not len(geo.C):
        return dict(schema="course_structure/1", status="no_greens_or_tees", holes=[], n_holes=N)
    best_form = np.array([hs[0]["score"] if hs else -30.0 for hs in hyps])
    gconf = np.array([g.get("p_hole", g.get("conf", 1.0)) for g in sc.greens])
    nothole = NOT_HOLE + np.log(np.maximum(gconf, 0.02)) - 0.5 * np.log(np.maximum(1 - gconf, 0.02))
    order = np.argsort(-(asg + 0.3 * best_form + nothole))
    if N > 20:
        keep = sorted(order[:min(nG, N + 2)].tolist())
        return _solve_large(sc, hyps, geo, keep, N, pars, yards, temp, clubs)
    M = max(min(nG, max_greens, N + 3), min(nG, N))
    keep = sorted(order[:M].tolist())
    if len(keep) < N:
        N = len(keep)
    pb = Problem(sc, hyps, geo, keep, use_paths=use_paths)
    Mk = len(keep)
    nh = nothole[keep]
    Hc = clubs + hub_candidates(sc, geo, hyps)
    wsum = sum(h["w"] for h in Hc)
    pos_base = _card_pos(pb.hk, pars, yards, N) if (pars or yards) else None
    price = np.zeros(len(geo.C) + 1)
    anchors = [pb.anchors(H["c"]) for H in Hc]
    eye = np.eye(Mk, dtype=bool)
    NEG = -1e4

    import crf
    theta = crf.theta_from_params()

    def mats(st_en, lam, parts=False):
        trans, turn, start, end, P = crf.potentials(pb, st_en, theta, N, price=lam, nh=nh)
        out = (trans / temp, None if turn is None else turn / temp, start / temp, end / temp)
        return (out, P) if parts else out

    def run_all(lam, marginals, only=None, soft=True):
        runs = []
        for i, (H, se) in enumerate(zip(Hc, anchors)):
            if only is not None and i not in only:
                continue
            trans, turn, start, end = mats(se, lam)
            r = route_dp(trans, start, end, N, turn=turn, pos=None if pos_base is None else pos_base / temp,
                         marginals=marginals, soft=soft)
            r.update(H=H, se=se, i=i, logw=r["logZ"] + math.log(H["w"] / wsum),
                     mapw=r["best_score"] + math.log(H["w"] / wsum))
            runs.append(r)
        return runs

    # Lagrangian prices: no complex starts two holes on the MAP route
    runs = run_all(price, marginals=False, soft=False)
    top = sorted(runs, key=lambda r: -r["mapw"])[:3]
    only = {r["i"] for r in top}
    best_i = {top[0]["i"]}
    for it in range(LAGR_ITERS):
        br = max(runs, key=lambda r: r["mapw"])
        cnt = _coverage(pb, mats(br["se"], price, parts=True)[1], br["best"], N)
        if cnt.max() <= 1:
            break
        price = price + 1.0 * (cnt > 1) * (1 + 0.5 * it)
        runs = run_all(price, marginals=False, only=best_i, soft=False)
    runs = run_all(price, marginals=True, only=only)
    lw = np.array([r["logw"] for r in runs])
    pw = np.exp(lw - _lse(lw))
    marg = sum(p * r["marg"] for p, r in zip(pw, runs))
    br = max(runs, key=lambda r: r["mapw"])
    br["mats"], br["parts"] = mats(br["se"], price, parts=True)
    return _assemble(sc, geo, pb, br, marg, pw, N, pars, yards, temp, price, return_debug, runs)


VIA_LL = float(walk_ll(WALK_MED * 1.6))


def _turn_walk(wl):
    """Walk green 9 -> tee 10: direct, or through the clubhouse (any distance; both ends are anchored to it)."""
    return np.logaddexp(math.log(TURN_VIA_H) + VIA_LL, math.log(1 - TURN_VIA_H) + wl)


def _tee_lp(P, seq, k, N):
    """Log-weights of the hypotheses of the k-th hole of the route (given the previous green)."""
    node = seq[k]
    if k == 0:
        return P["z0"][node]
    if k == 9 and N == 18:
        return P["zu"][seq[k - 1], node]
    return P["zt"][seq[k - 1], node]


def _coverage(pb, P, seq, N):
    """How many holes of the route use each complex, with each hole's best hypothesis."""
    cnt = np.zeros(pb.cov.shape[2])
    for k, node in enumerate(seq):
        cnt += pb.cov[node, int(np.argmax(_tee_lp(P, seq, k, N)))]
    return cnt


def _card_pos(hk, pars, yards, N):
    """pos[j, k]: log-likelihood ratio of node j being card hole k (straight length vs card yards; par)."""
    pos = np.zeros((len(hk), N))
    for j, hs in enumerate(hk):
        if not hs:
            continue
        D = np.array([h["D"] for h in hs])
        fs = np.array([h["score"] for h in hs])
        lw = fs - _lse(fs)
        base, pp = length_loglik(D)
        for k in range(N):
            ll = np.zeros(len(hs))
            if yards and k < len(yards) and yards[k]:
                Y = float(yards[k])
                sd = 0.05 * Y + 12
                z = np.where(D > Y, (D - Y) / sd, (D - Y) / (2.0 * sd))      # dog-legs: straight < measured
                ll += np.log(0.9 * np.exp(-0.5 * z ** 2) / (sd * 2.5) + 0.1 / 600) + math.log(600) - base
            elif pars and k < len(pars) and pars[k]:
                p = min(max(int(pars[k]), 3), 5)
                ll += np.log(np.maximum(pp[p - 3], 1e-3) / PAR_PI[p])
            pos[j, k] = _lse(lw + ll)
    return np.clip(pos, -20.0, 10.0)


def _assemble(sc, geo, pb, br, marg, pw, N, pars, yards, temp, price, debug, runs):
    G = geo.G
    seq = br["best"]
    st_l, _ = br["se"]
    holes = []
    for k, node in enumerate(seq):
        gi = pb.keep[node]
        hs = pb.hk[node]
        lp = _tee_lp(br["parts"], seq, k, N) / temp
        ph = np.exp(lp - _lse(lp))
        hi = int(np.argmax(ph))
        h = hs[hi]
        cx = geo.cx[h["k"]]
        p_num = float(marg[node, k])
        holes.append(dict(number=k + 1, green=sc.greens[gi]["id"], green_xy=[float(x) for x in G[gi]],
                          tee_complex=cx["id"], tee=sc.tees[cx["boxes"][0]]["id"],
                          tee_xy=[float(x) for x in h["tee"]],
                          boxes=[sc.tees[b]["id"] for b in cx["boxes"]], length_yd=round(h["D"], 1),
                          p_par=[round(float(x), 3) for x in h["ppar"]], p_number=round(p_num, 3),
                          p_tee=round(float(ph[hi]), 3), confidence=round(p_num * float(ph[hi]), 3),
                          walk_in_yd=round(float(pb.wd[seq[k - 1]][node][hi]), 1) if k > 0 else None,
                          form_score=round(h["score"], 2), feat={a: round(b, 2) for a, b in h["f"].items()}))
    pars_inf = infer_pars([h["p_par"] for h in holes], N)
    for h, p in zip(holes, pars_inf):
        h["par"] = p
    used = {pb.keep[n] for n in seq}
    out = dict(schema="course_structure/1", status="ok", n_holes=N, holes=holes,
               practice_greens=[sc.greens[i]["id"] for i in range(len(sc.greens)) if i not in used],
               clubhouse=dict(xy=[float(x) for x in br["H"]["c"]], how=br["H"]["how"],
                              p=round(float(pw[runs.index(br)]), 3)),
               total_par=int(sum(pars_inf)), card_used=bool(pars or yards),
               p_route=round(float(np.exp(min(0.0, br["best_score"] - br["logZ"]))), 4))
    if debug:
        out["debug"] = dict(marg=marg, keep=pb.keep, runs=[(r["H"]["how"], r["logw"]) for r in runs], price=price,
                            mats=br.get("mats"), seq=seq, best_score=br["best_score"])
    return out


def infer_pars(pp, N):
    """Par per hole: par posteriors + a prior on the number of par 3s / 5s (~N x 4.2 / 18 and 3.8 / 18, i.e. total
    par ~70-72 for 18)."""
    n = len(pp)
    if n == 0:
        return []
    lp = np.log(np.maximum(np.array(pp, float), 1e-6))
    exp3, exp5 = N * 4.2 / 18, N * 3.8 / 18
    d3 = lp[:, 0] - lp[:, 1]
    d5 = lp[:, 2] - lp[:, 1]
    best = None
    for n3 in range(0, n + 1):
        idx3 = list(np.argsort(-d3)[:n3])
        rest_order = [i for i in np.argsort(-d5) if i not in idx3]
        for n5 in range(0, n + 1 - n3):
            rest = rest_order[:n5]
            s = d3[idx3].sum() + d5[rest].sum() - 0.5 * ((n3 - exp3) / 1.3) ** 2 - 0.5 * ((n5 - exp5) / 1.3) ** 2
            if best is None or s > best[0]:
                best = (s, idx3, rest)
    par = [4] * n
    for i in best[1]:
        par[i] = 3
    for i in best[2]:
        par[i] = 5
    return par


def _solve_large(sc, hyps, geo, keep, N, pars, yards, temp, clubs):
    """27 / 36 holes: loops of 9 from the clubhouse, greedy (best hole by formation + walk at each step), confidence
    from the local soft-max. Exact inference is 2^27; reported apart in the eval."""
    G = geo.G
    Hc = clubs + hub_candidates(sc, geo, hyps)
    c = Hc[0]["c"]
    left = set(keep)
    used_cx = set()
    holes = []
    prev = None
    k = 0
    while left and k < N:
        cands = []
        for gi in left:
            for h in hyps[gi]:
                if h["k"] in used_cx:
                    continue
                xy = geo.cx[h["k"]]["xy"]
                if prev is None or k % 9 == 0:
                    wl = float(anchor_ll(np.hypot(*(xy - c).T).min()))
                else:
                    wl = float(walk_ll(max(1.0, np.hypot(*(xy - G[prev]).T).min() - geo.gr_r[prev])))
                cands.append((h["score"] + wl, gi, h))
        if not cands:
            break
        cands.sort(key=lambda r: -r[0])
        s0 = np.array([r[0] for r in cands]) / temp
        p = np.exp(s0 - _lse(s0))
        _, gi, h = cands[0]
        cx = geo.cx[h["k"]]
        holes.append(dict(number=k + 1, green=sc.greens[gi]["id"], green_xy=[float(x) for x in G[gi]],
                          tee_complex=cx["id"], tee=sc.tees[cx["boxes"][0]]["id"], tee_xy=[float(x) for x in h["tee"]],
                          boxes=[sc.tees[b]["id"] for b in cx["boxes"]], length_yd=round(h["D"], 1),
                          p_par=[round(float(x), 3) for x in h["ppar"]], p_number=round(float(p[0]), 3), p_tee=1.0,
                          confidence=round(float(p[0]), 3), walk_in_yd=None, form_score=round(h["score"], 2), feat={}))
        left.discard(gi)
        used_cx.add(h["k"])
        prev = gi
        k += 1
    for h, p in zip(holes, infer_pars([h["p_par"] for h in holes], N)):
        h["par"] = p
    used = {h["green"] for h in holes}
    return dict(schema="course_structure/1", status="ok_greedy", n_holes=N, holes=holes,
                practice_greens=[g["id"] for g in sc.greens if g["id"] not in used],
                clubhouse=dict(xy=[float(x) for x in c], how=Hc[0]["how"], p=None),
                total_par=int(sum(h["par"] for h in holes)), card_used=bool(pars or yards), p_route=None)


def route_score(mats, seq):
    """Log-score of a node sequence under (trans, turn, start, end) from solve(return_debug=True)."""
    trans, turn, start, end = mats
    s = start[seq[0]] + end[seq[-1]]
    for k in range(1, len(seq)):
        tr = turn if (turn is not None and k == 9) else trans
        s += tr[seq[k - 1], seq[k]]
    return float(s)
