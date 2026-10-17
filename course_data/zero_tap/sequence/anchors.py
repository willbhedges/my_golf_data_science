"""Anchors of the round: where it starts (the clubhouse) and which loop is the front nine.

clubhouse_candidates()  every plausible clubhouse point (tagged clubhouses, buildings, car parks, "hubs" where greens
                        and hole starts meet) scored by a softmax ranker fitted on dev courses: the target is the
                        candidate nearest tee 1 and the last green of the true route. Features: tags, building size
                        and neighbourhood (houses vs one large building), car parks, golf features around it, the
                        course's address street (OSM addr:street of the course), the boundary.
NineModel               front / back nine for 18-hole routes: antisymmetric logistic regression (no intercept) on cues
                        that loop A is the front nine: route score difference, tee 1 / green 18 nearer the
                        clubhouse (expected over the clubhouse posterior), tee 1 nearer the practice green, range,
                        car park, the largest building and the address street, par-by-number cues (hole 1 / 10 / 18
                        par 3 rates), front-nine length.
Weights: anchors_params.json (fit_anchors.py, dev courses only).
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(CD, "structure"))
import solver as V                                                   # noqa: E402

PARAMS = os.environ.get("ZT_ANCHORS_PARAMS", os.path.join(HERE, "anchors_params.json"))
ROAD_HW = ("primary", "secondary", "tertiary", "residential", "unclassified", "service", "trunk", "living_street")


# ----------------------------------------------------------------------------- inputs
def roads_from_fc(fc, proj):
    """[(name lower, polyline yards)] of named roads (+ unnamed service roads as '')."""
    out = []
    for f in fc.get("features", []):
        p, g = f.get("properties", {}), f.get("geometry") or {}
        if p.get("highway") in ROAD_HW and g.get("type") == "LineString":
            out.append((str(p.get("name", "")).lower().strip(), proj.ring(g["coordinates"])))
    return out


def addr_street(course):
    t = (course or {}).get("tags") or {}
    s = t.get("addr:street") or ""
    return s.lower().strip() or None


def _norm_street(s):
    s = s.lower()
    for a, b in ((" road", " rd"), (" street", " st"), (" drive", " dr"), (" avenue", " ave"), (" lane", " ln"),
                 (" boulevard", " blvd"), (" highway", " hwy"), (" parkway", " pkwy"), (" court", " ct"),
                 ("north ", "n "), ("south ", "s "), ("east ", "e "), ("west ", "w ")):
        s = s.replace(a, b)
    return s.strip()


def _pl_dist(p, line):
    a, b = line[:-1], line[1:]
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab ** 2).sum(1), 1e-9), 0, 1)
    return float(np.hypot(*(a + ab * t[:, None] - p).T).min())


def street_lines(roads, street):
    if not street:
        return []
    s = _norm_street(street)
    return [ln for nm, ln in roads if nm and len(ln) >= 2 and _norm_street(nm) == s]


# ----------------------------------------------------------------------------- clubhouse
CLUB_FEATS = ("named", "building", "parking", "hub", "log_area", "small", "near_named", "d_park", "n_park",
              "d_green", "d_tee", "ends", "n_bld", "d_street", "has_street", "outside", "area_rank1", "hub_w",
              "d_service")


def _raw(sc, geo, hyps):
    cands = []
    for c in sc.clubhouse:
        if c["how"] == "named":
            cands.append(dict(c=np.asarray(c["c"], float), src="named", area=0.0))
    feats = np.array([g["c"] for g in sc.greens] + [t["c"] for t in sc.tees]).reshape(-1, 2)
    for b in sc.buildings:
        if b["area"] < 60 or b["area"] > 12000:
            continue
        if len(feats) and np.hypot(*(feats - b["c"]).T).min() > 350:
            continue
        cands.append(dict(c=np.asarray(b["c"], float), src="building", area=float(b["area"])))
    for p in sc.parking:
        if len(feats) and np.hypot(*(feats - p).T).min() > 400:
            continue
        cands.append(dict(c=np.asarray(p, float), src="parking", area=0.0))
    for h in V.hub_candidates(sc, geo, hyps, k=8):
        cands.append(dict(c=np.asarray(h["c"], float), src="hub", area=0.0, hub_w=h["w"]))
    return cands


def club_features(sc, geo, hyps, cands, roads=(), street=None):
    named = [c["c"] for c in cands if c["src"] == "named"]
    bld = np.array([b["c"] for b in sc.buildings]).reshape(-1, 2)
    park = np.array(sc.parking).reshape(-1, 2)
    G = geo.G
    T = geo.C
    sl = street_lines(roads, street)
    serv = [ln for nm, ln in roads if len(ln) >= 2]
    big = sorted([c for c in cands if c["src"] == "building"], key=lambda c: -c["area"])
    top_area = big[0]["area"] if big else 0.0
    X = []
    for c in cands:
        p = c["c"]
        f = dict.fromkeys(CLUB_FEATS, 0.0)
        f[c["src"]] = 1.0
        if c["src"] == "building":
            f["log_area"] = math.log(max(c["area"], 30) / 500.0)
            f["small"] = float(c["area"] < 180)
            f["area_rank1"] = float(c["area"] >= top_area - 1e-6)
        f["near_named"] = float(any(np.hypot(*(p - q)) < 60 for q in named))
        dpk = np.hypot(*(park - p).T) if len(park) else np.array([1e4])
        f["d_park"] = math.log1p(dpk.min() / 50.0)
        f["n_park"] = min(3, int((dpk < 150).sum())) / 3.0
        f["d_green"] = math.log1p(max(0.0, (np.hypot(*(G - p).T) - geo.gr_r).min()) / 50.0) if len(G) else 3.0
        f["d_tee"] = math.log1p(np.hypot(*(T - p).T).min() / 50.0) if len(T) else 3.0
        ng = int((np.hypot(*(G - p).T) < 160).sum()) if len(G) else 0
        nt = int((np.hypot(*(T - p).T) < 160).sum()) if len(T) else 0
        f["ends"] = (min(ng, 4) + min(nt, 4)) / 8.0
        f["n_bld"] = math.log1p(int((np.hypot(*(bld - p).T) < 100).sum()) if len(bld) else 0)
        if sl:
            f["has_street"] = 1.0
            f["d_street"] = math.log1p(min(_pl_dist(p, ln) for ln in sl) / 50.0)
        if serv:
            f["d_service"] = math.log1p(min(_pl_dist(p, ln) for ln in serv) / 50.0)
        if sc.boundary:
            import scene as S
            f["outside"] = float(not S._inside(p, sc.boundary)) * min(1.0, S._dist_to_rings(p, sc.boundary) / 100.0)
        f["hub_w"] = c.get("hub_w", 0.0) * 25
        X.append([f[k] for k in CLUB_FEATS])
    return np.array(X).reshape(-1, len(CLUB_FEATS))


def clubhouse_candidates(sc, geo, hyps, roads=(), street=None, model=None, k=8, return_all=False):
    """[{c, w, how}] for the route DP: ranker probabilities (model weights) or the structure defaults (no model).
    Near-duplicate points (< 35 yds) are merged, keeping the higher score."""
    if model is None:
        model = load_models().get("club")
    if model is None:
        return list(sc.clubhouse) + V.hub_candidates(sc, geo, hyps)
    cands = _raw(sc, geo, hyps)
    if not cands:
        return V.hub_candidates(sc, geo, hyps)
    X = club_features(sc, geo, hyps, cands, roads, street)
    w = np.array([model.get(f, 0.0) for f in CLUB_FEATS])
    s = X @ w
    p = np.exp(s - s.max())
    p /= p.sum()
    order = np.argsort(-p)
    out = []
    for i in order:
        c = cands[i]
        if any(np.hypot(*(c["c"] - o["c"])) < 35 for o in out):
            continue
        out.append(dict(c=c["c"], w=float(max(p[i], 1e-4)), how=c["src"]))
        if len(out) >= k:
            break
    if return_all:
        return out, cands, X, p
    return out


# ----------------------------------------------------------------------------- front / back nine
NINE_FEATS = ("dp", "t1_club", "g18_club", "t1_practice", "t1_range", "t1_parking", "front_len", "t1_bigbld",
              "t1_street", "p3_1v10", "p3_18v9", "p5_1v10", "t1_service", "g18_bigbld")


def _slog(v, s=30.0):
    return float(np.sign(v) * math.log1p(abs(v) / s))


def nine_features(sc, geo, pb, br, seq, Hc, pw, runs, dp, roads=(), street=None):
    parts = br["parts"]
    tees, lens, pp = [], [], []
    for k, node in enumerate(seq):
        lp = V._tee_lp(parts, seq, k, 18)
        h = pb.hk[node][int(np.argmax(lp))]
        tees.append(np.asarray(h["tee"]))
        lens.append(h["D"])
        pp.append(np.asarray(h["ppar"], float))
    G = geo.G
    A_t, B_t = tees[0], tees[9]
    A_l, B_l = G[pb.keep[seq[17]]], G[pb.keep[seq[8]]]

    def d(p, q):
        return float(np.hypot(*(np.asarray(p) - np.asarray(q))))

    def dmin(p, pts):
        return min((d(p, q) for q in pts), default=None)
    x = dict.fromkeys(NINE_FEATS, 0.0)
    x["dp"] = float(np.clip(dp, -30, 30))
    # expected over the clubhouse posterior
    Hs = [(float(w), r["H"]["c"]) for w, r in zip(pw, runs)]
    x["t1_club"] = sum(w * _slog(d(B_t, c) - d(A_t, c)) for w, c in Hs)
    x["g18_club"] = sum(w * _slog(d(B_l, c) - d(A_l, c)) for w, c in Hs)
    used = {pb.keep[n] for n in seq}
    practice = [G[i] for i in range(len(G)) if i not in used]
    if practice:
        x["t1_practice"] = _slog(dmin(B_t, practice) - dmin(A_t, practice))
    rng = [np.mean(r, 0) for r in sc.ranges]
    if rng:
        x["t1_range"] = _slog(dmin(B_t, rng) - dmin(A_t, rng))
    if len(sc.parking):
        x["t1_parking"] = _slog(dmin(B_t, sc.parking) - dmin(A_t, sc.parking))
    x["front_len"] = (sum(lens[:9]) - sum(lens[9:])) / 300.0
    bl = sorted(sc.buildings, key=lambda b: -b["area"])
    bl = [b["c"] for b in bl if b["area"] >= 250][:3]
    if bl:
        x["t1_bigbld"] = _slog(dmin(B_t, bl) - dmin(A_t, bl))
        x["g18_bigbld"] = _slog(dmin(B_l, bl) - dmin(A_l, bl))
    sl = street_lines(roads, street)
    if sl:
        x["t1_street"] = _slog(min(_pl_dist(B_t, ln) for ln in sl) - min(_pl_dist(A_t, ln) for ln in sl), 60.0)
    serv = [ln for nm, ln in roads if len(ln) >= 2]
    if serv:
        x["t1_service"] = _slog(min(_pl_dist(B_t, ln) for ln in serv) - min(_pl_dist(A_t, ln) for ln in serv), 60.0)
    x["p3_1v10"] = float(pp[9][0] - pp[0][0])
    x["p3_18v9"] = float(pp[17][0] - pp[8][0])
    x["p5_1v10"] = float(pp[0][2] - pp[9][2])
    return x


class NineModel:
    def __init__(self, w, roads=(), street=None):
        self.w = w
        self.roads, self.street = roads, street

    def with_context(self, roads, street):
        return NineModel(self.w, roads, street)

    def prob(self, sc, geo, pb, br, seq, Hc, pw, runs, dp):
        x = nine_features(sc, geo, pb, br, seq, Hc, pw, runs, dp, self.roads, self.street)
        z = sum(self.w.get(k, 0.0) * x[k] for k in NINE_FEATS)
        return 1 / (1 + math.exp(-max(-30, min(30, z)))), x


_MODELS = None


def load_models(path=None):
    global _MODELS
    if _MODELS is not None and path is None:
        return _MODELS
    out = {}
    p = path or PARAMS
    if os.path.exists(p):
        js = json.load(open(p))
        out["club"] = js.get("club_w")
        if js.get("nine_w"):
            out["nine"] = NineModel(js["nine_w"])
    if path is None:
        _MODELS = out
    return out
