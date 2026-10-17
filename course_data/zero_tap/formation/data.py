"""Courses, inputs, tee candidates and pair features for the hole-formation pair model.

A course instance = one input scene (OSM features with every hole hint hidden, or a blind perception scene),
its tee-complex candidates (the structure solver's complexes plus fairway-end virtual tees), and one feature row per
(green, candidate) pair 70-700 yds apart. Truth (from the hidden OSM golf=hole ways) marks, per true hole, its
green and every candidate that would count as "formed" (structure/eval.py tee_ok).
"""
from __future__ import annotations

import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(CD, "structure"), os.path.join(CD, "platform")]
import scene as S                                                    # noqa: E402
import solver as V                                                   # noqa: E402

INPUTS = os.path.join(HERE, "inputs")
YD = 0.9144

# ----------------------------------------------------------------------------------------------- course lists
# Splits. The structure study's held-out states (AR CT DE IA ID MO NC NE NJ NV PA WA) are the test states here:
# nothing is fitted or tuned on them. Everything else is in the 12 dev states (CA GA IL KY MA ME MN MS NH UT WI WY).
# The generalize study's own test courses (validation_set.json split "test", dev states) are kept out of training
# and reported apart. Model selection uses cross-validation grouped by state on the dev training courses.
HELDOUT_STATES = {"AR", "CT", "DE", "IA", "ID", "MO", "NC", "NE", "NJ", "NV", "PA", "WA"}


def zero_tap_bench():
    """Workstream D's benchmark (course_data/zero_tap/bench*), when it exists: {slug: split}."""
    for p in (os.path.join(CD, "zero_tap", "bench", "courses.json"), os.path.join(CD, "zero_tap", "bench.json")):
        if os.path.exists(p):
            try:
                obj = json.load(open(p))
                cs = obj.get("courses", obj) if isinstance(obj, dict) else obj
                return {c["slug"]: c.get("split") for c in cs if isinstance(c, dict) and "slug" in c}
            except Exception:                                        # noqa: BLE001
                return {}
    return {}


def courses():
    out = []
    sets = json.load(open(os.path.join(CD, "structure", "sets.json")))
    for c in sets["courses"]:
        d = os.path.join(CD, "structure", "data", c["slug"])
        p = os.path.join(d, "osm.geojson.gz")
        if not os.path.exists(p):
            continue
        out.append(dict(slug=c["slug"], state=c["state"], osm=p, course=os.path.join(d, "course.json"),
                        split="heldout" if c["state"] in HELDOUT_STATES else "train", src="structure"))
    vs = {c["slug"]: c for c in json.load(open(os.path.join(CD, "generalize", "validation_set.json")))["courses"]}
    gdir = os.path.join(CD, "generalize", "courses")
    for s in sorted(os.listdir(gdir)):
        d = os.path.join(gdir, s)
        p = os.path.join(d, "osm_golf.geojson")
        if not os.path.exists(p) or not os.path.exists(os.path.join(d, "course.json")):
            continue
        v = vs.get(s, {})
        st = v.get("state") or s.rsplit("_", 1)[-1].upper()
        out.append(dict(slug=s, state=st, osm=p, course=os.path.join(d, "course.json"),
                        split="gtest" if v.get("split") == "test" else "train", src="generalize"))
    return out


# ----------------------------------------------------------------------------------------------- inputs
def perception_scene_obj(slug):
    for p in (os.path.join(INPUTS, slug, "scene.json.gz"), os.path.join(CD, "perception", "scenes", slug, "scene.json.gz")):
        if os.path.exists(p):
            with gzip.open(p, "rt") as fh:
                return json.load(fh)
    return None


def load_card(slug):
    """The chosen web card (scorecard/1) or None."""
    for p in (os.path.join(INPUTS, slug, "scorecard.json"), os.path.join(CD, "generalize", "courses", slug, "scorecard.json")):
        if not os.path.exists(p):
            continue
        obj = json.load(open(p))
        cards = obj.get("cards") or []
        if not cards:
            continue
        ch = obj.get("chosen")
        pick = next((c for c in cards if c["source"] == ch), cards[0])
        return pick["card"]
    return None


def card_sets(card):
    """scorecard/1 -> (pars or None, yards array n_holes x n_sets (sets sorted long -> short), set names)."""
    if not card or not card.get("tee_sets"):
        return None, None, []
    sets = []
    for name, s in card["tee_sets"].items():
        y = s.get("yards") or []
        if y and all(isinstance(v, (int, float)) and v for v in y):
            sets.append((sum(y), name, list(map(float, y))))
    if not sets:
        return None, None, []
    n = max(len(s[2]) for s in sets)
    sets = [s for s in sets if len(s[2]) == n]
    sets.sort(key=lambda s: -s[0])
    Y = np.array([s[2] for s in sets]).T
    pars = card.get("par")
    pars = [int(p) for p in pars] if pars and len(pars) == n and all(str(p).isdigit() for p in pars) else None
    return pars, Y, [s[1] for s in sets]


def card_from_truth(truth):
    """Stand-in card from the hidden OSM ways (one 'back' set = mapped line length; pars when tagged)."""
    pars = [h["par"] for h in truth]
    return dict(schema="scorecard/1", par=pars if all(pars) else None,
                tee_sets={"back": dict(yards=[round(h["length"]) for h in truth])})


class Aux:
    """aux.npz layers (aux_build.py) sampled in the scene's yard frame."""

    def __init__(self, path, proj):
        z = np.load(path)
        self.z = {k: z[k] for k in z.files}
        from pyproj import Transformer
        self.tf = Transformer.from_crs("EPSG:4326", str(self.z["crs"]), always_xy=True)
        t = self.z["transform"]
        self.res, self.x0, self.y1 = float(t[0]), float(t[2]), float(t[5])
        self.proj = proj
        H, W = self.z["fw"].shape
        self.H, self.W = H, W
        dtm = self.z["dtm"].astype(np.float32) / 10.0
        dtm[self.z["dtm"] == -32768] = np.nan
        self.dtm = dtm
        self.fw = self.z["fw"].astype(np.float32) / 255.0
        self.te = self.z["te"].astype(np.float32) / 255.0
        self.gr = self.z["gr"].astype(np.float32) / 255.0
        self.tree = self.z["tree"].astype(np.float32) / 255.0
        sd = self.z["sdeg"].astype(np.float32)
        self.sok = sd != 255
        self.srad = np.radians(90.0 - sd)                      # stripe axis as a math angle (undirected)
        self.scoh = self.z["scoh"].astype(np.float32) / 255.0 * self.sok
        self.lidar = bool(self.z.get("lidar", True))

    def rc(self, xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        lon, lat = self.proj.inv(xy[:, 0], xy[:, 1])
        X, Y = self.tf.transform(lon, lat)
        r = (self.y1 - np.asarray(Y)) / self.res - 0.5
        c = (np.asarray(X) - self.x0) / self.res - 0.5
        return r, c

    def sample(self, arr, xy):
        r, c = self.rc(xy)
        ri = np.clip(np.round(r).astype(int), 0, self.H - 1)
        ci = np.clip(np.round(c).astype(int), 0, self.W - 1)
        inside = (r >= -0.5) & (r < self.H - 0.5) & (c >= -0.5) & (c < self.W - 0.5)
        v = arr[ri, ci].astype(np.float64)
        return np.where(inside, v, np.nan)


def load_aux(slug, proj):
    p = os.path.join(INPUTS, slug, "aux.npz")
    if not os.path.exists(p):
        return None
    try:
        return Aux(p, proj)
    except Exception:                                                # noqa: BLE001
        return None


# ----------------------------------------------------------------------------------------------- candidates
def add_virtual_tees(sc, geo, min_sep=40.0, back=15.0):
    """Fairway-end virtual tees: for each green, the far end of each fairway that touches it (the structure solver's
    'cones'), pushed `back` yds beyond the fairway end, when no candidate is within `min_sep` yds. Raises the
    candidate ceiling for holes whose tee boxes are not mapped / not detected."""
    added = 0
    C = geo.C if len(geo.C) else np.zeros((0, 2))
    G = geo.G
    new = []
    for gi, cones in enumerate(geo.cones):
        for e_f, d in cones:
            p = np.asarray(e_f, float) + back * np.asarray(d, float)
            D = float(np.hypot(*(p - G[gi])))
            if D < V.L_MIN or D > V.L_MAX:
                continue
            allc = np.vstack([C] + [np.array([q["c"]]) for q in new]) if (len(C) or new) else np.zeros((0, 2))
            if len(allc) and np.hypot(*(allc - p).T).min() < min_sep:
                continue
            if len(G) and np.hypot(*(G - p).T).min() < 30:
                continue
            new.append(dict(id=f"v{len(new)}", boxes=[], xy=p[None, :], c=p, axis=math.atan2(-d[1], -d[0]),
                            axis_w=0.3, conf=0.3, virtual=True, src_green=gi))
    for q in new:
        # a stand-in tee box in the scene, so code that reads complexes' boxes (structure solver) works unchanged
        sc.tees.append(dict(id=f"vt{len(sc.tees)}", c=q["c"], ring=None, area=0.0, axis=q["axis"], elong=1.0,
                            conf=q["conf"], virtual=True))
        q["boxes"] = [len(sc.tees) - 1]
        geo.cx.append(q)
        added += 1
    if added:
        geo.C = np.array([c["c"] for c in geo.cx], float).reshape(-1, 2)
        geo._corr = None
    return added


# ----------------------------------------------------------------------------------------------- features
BASE = V.FEATS
EXTRA = ("D", "pp3", "pp5", "cx_conf", "cx_n", "cx_axis_w", "virtual", "g_conf",
         "base", "base_gap_g", "base_rank_g", "base_gap_k", "base_rank_k", "n_cand_g",
         "near_other_g", "this_g_rank_from_k", "path_ratio", "g_axis_al", "g_el", "v_own")
AUXF = ("a_ok", "a_fw_mean", "a_fw_min", "a_fw_end", "a_tree_mean", "a_tree_max", "a_lc", "a_stripe", "a_stripe_w",
        "a_dz", "a_ridge", "a_valley", "a_te_k")
CARDF = ("c_ok", "c_back_res", "c_back_abs", "c_sets_frac", "c_n_close", "c_par_ll")
FEATS = BASE + EXTRA + AUXF + CARDF


def _aux_lc(aux, geo, cell=None):
    """Least-cost line of play on the aux grid (cost 1 + 2.5 (1 - p_fairway) + 3 tree share), per (green, cand):
    cost / straight distance."""
    from skimage.graph import MCP_Geometric
    cost = 1.0 + 2.5 * (1.0 - np.nan_to_num(aux.fw)) + 3.0 * np.nan_to_num(aux.tree) + 2.0 * np.nan_to_num(aux.gr)
    nG, nC = len(geo.G), len(geo.C)
    out = np.full((nG, nC), np.nan)
    rg, cg = aux.rc(geo.G)
    rk, ck = aux.rc(geo.C)
    H, W = cost.shape
    rk = np.clip(np.round(rk).astype(int), 0, H - 1)
    ck = np.clip(np.round(ck).astype(int), 0, W - 1)
    for gi in range(nG):
        r, c = int(round(rg[gi])), int(round(cg[gi]))
        if not (0 <= r < H and 0 <= c < W):
            continue
        m = MCP_Geometric(cost, fully_connected=True)
        cum, _ = m.find_costs([(r, c)])
        out[gi] = cum[rk, ck] * aux.res / YD
    return out


def pair_features(sc, geo, aux=None, card=None, clubs=None):
    """-> list of dicts {gi, k, tee, D, f: {FEATS}} for every (green, candidate) 70-700 yds apart."""
    clubs = sc.clubhouse if clubs is None else clubs
    hs = V.features(sc, geo, clubs)
    if not hs:
        return []
    nG, nC = len(geo.G), len(geo.C)
    base = np.full((nG, nC), -np.inf)
    for h in hs:
        h["base"] = sum(V.FORM_W.get(k, 0.0) * h["f"][k] for k in BASE)
        base[h["gi"], h["k"]] = h["base"]
    best_g = base.max(1)
    best_k = base.max(0)
    rank_g = (-base).argsort(1).argsort(1)
    rank_k = (-base).argsort(0).argsort(0)
    ncg = np.isfinite(base).sum(1)
    # distance from each candidate to the greens (edge), for "which green is this tee next to / pointing at"
    Gr = geo.gr_r
    dKG = np.hypot(geo.C[:, None, 0] - geo.G[None, :, 0], geo.C[:, None, 1] - geo.G[None, :, 1])
    near_edge = dKG - Gr[None, :]
    lc = None
    if aux is not None:
        try:
            lc = _aux_lc(aux, geo)
        except Exception:                                            # noqa: BLE001
            lc = None
    pars, Y, _ = card_sets(card) if card else (None, None, [])
    cc = geo.corridor_costs() if geo.has_fw else None
    g_axes = [S.long_axis(g["ring"]) if g.get("ring") is not None and len(g["ring"]) >= 4 else (None, 1.0)
              for g in sc.greens]
    out = []
    for h in hs:
        gi, k = h["gi"], h["k"]
        cx = geo.cx[k]
        f = dict(h["f"])
        D = h["D"]
        f.update(D=D / 100.0, pp3=float(h["ppar"][0]), pp5=float(h["ppar"][2]), cx_conf=float(cx.get("conf", 1.0)),
                 cx_n=float(len(cx["xy"])), cx_axis_w=float(cx.get("axis_w", 0.0)), virtual=float(bool(cx.get("virtual"))),
                 g_conf=float(sc.greens[gi].get("p_hole", sc.greens[gi].get("conf", 1.0))),
                 base=h["base"], base_gap_g=h["base"] - best_g[gi], base_rank_g=float(min(rank_g[gi, k], 10)),
                 base_gap_k=h["base"] - best_k[k], base_rank_k=float(min(rank_k[gi, k], 10)), n_cand_g=float(ncg[gi]))
        ne = near_edge[k].copy()
        ne[gi] = np.inf
        f["near_other_g"] = float(min(ne.min(), 400.0)) / 100.0
        # how many greens are nearer the candidate than this one (a tee's own green is rarely the nearest)
        f["this_g_rank_from_k"] = float(min((near_edge[k] < near_edge[k, gi]).sum(), 10))
        f["path_ratio"] = float(min(3.0, cc[gi, k] / D - 1.0)) if cc is not None and np.isfinite(cc[gi, k]) else 0.0
        # greens are usually built long along the line of approach
        gax, gel = g_axes[gi]
        if gax is not None:
            t = np.asarray(h["tee"], float)
            ang = math.atan2(geo.G[gi][1] - t[1], geo.G[gi][0] - t[0])
            f["g_axis_al"] = float(math.cos(2 * (ang - gax)) * min(1.0, max(0.0, (gel - 1.0) / 0.5)))
        else:
            f["g_axis_al"] = 0.0
        f["g_el"] = float(min(gel, 3.0))
        # a fairway-end virtual tee made from this green's own fairway
        f["v_own"] = float(bool(cx.get("virtual")) and cx.get("src_green") == gi)
        # imagery / lidar along the straight line of play
        if aux is not None:
            t, g = np.asarray(h["tee"], float), geo.G[gi]
            s = np.linspace(0.1, 0.9, 33)
            pts = t[None, :] + s[:, None] * (g - t)[None, :]
            fw = aux.sample(aux.fw, pts)
            tr = aux.sample(aux.tree, pts)
            ok = np.isfinite(fw)
            if ok.mean() > 0.6:
                fwv = np.nan_to_num(fw, nan=0.0)
                win = np.convolve(fwv, np.ones(5) / 5, "valid")
                ang = math.atan2(g[1] - t[1], g[0] - t[0])
                sr = aux.sample(aux.srad, pts)
                sw = np.nan_to_num(aux.sample(aux.scoh, pts))
                al = np.cos(2 * (np.nan_to_num(sr) - ang))
                z = aux.sample(aux.dtm, np.vstack([t, pts, g]))
                zt, zg, zl = z[0], z[-1], z[1:-1]
                lin = zt + s * (zg - zt)
                dz = zl - lin
                f.update(a_ok=1.0, a_fw_mean=float(fwv.mean()), a_fw_min=float(win.min()),
                         a_fw_end=float(fwv[-8:].mean()), a_tree_mean=float(np.nan_to_num(tr).mean()),
                         a_tree_max=float(np.convolve(np.nan_to_num(tr), np.ones(5) / 5, "valid").max()),
                         a_lc=float(min(4.0, lc[gi, k] / D - 1.0)) if lc is not None and np.isfinite(lc[gi, k]) else 1.0,
                         a_stripe=float((al * sw).sum() / max(sw.sum(), 1e-6)) if sw.sum() > 0.5 else 0.0,
                         a_stripe_w=float(min(sw.sum(), 10.0)),
                         a_dz=float(np.clip((zt - zg) / YD, -40, 40)) if np.isfinite(zt) and np.isfinite(zg) else 0.0,
                         a_ridge=float(np.clip(np.nanmax(dz) / YD, 0, 40)) if np.isfinite(dz).any() else 0.0,
                         a_valley=float(np.clip(-np.nanmin(dz) / YD, 0, 40)) if np.isfinite(dz).any() else 0.0,
                         a_te_k=float(np.nanmax(aux.sample(aux.te, cx["xy"]))) if len(cx["xy"]) else 0.0)
        # scorecard: each pair's lengths vs the card's per-hole, per-tee-set yardages
        if Y is not None:
            boxes = np.asarray(cx["xy"], float)
            for kk in h.get("cover", []):
                if kk != k:
                    boxes = np.vstack([boxes, geo.cx[kk]["xy"]])
            g = geo.G[gi]
            u = (g - h["tee"]) / max(D, 1e-6)
            rel = boxes - g
            along = -(rel @ u)                              # distance from the green back along the line
            lat = np.abs(rel[:, 0] * u[1] - rel[:, 1] * u[0])
            dists = along[lat < 25]
            yb = Y[:, 0]
            res = yb - D                                    # card measures the line of play: >= straight (dog-legs)
            # robust per-hole fit: back tee within a few yards, every other set's yardage matched by some box
            sco = -np.abs(np.clip(res, -1e9, 0)) / 6.0 - np.clip(res - 8.0, 0, None) / 20.0
            best = int(np.argmax(sco))
            fr = 0.0
            if Y.shape[1] > 1 and len(dists):
                ys = Y[best]
                m = [bool((np.abs(dists - y) <= 12).any() or (dists.max() < y + 12 and abs(D - y) <= 12)) for y in ys]
                fr = float(np.mean(m))
            par_ll = 0.0
            if pars is not None:
                pp = h["ppar"]
                par_ll = float(math.log(max(pp[[3, 4, 5].index(pars[best])] if pars[best] in (3, 4, 5) else 0.01, 1e-3)))
            f.update(c_ok=1.0, c_back_res=float(np.clip(res[best], -100, 100)) / 10.0,
                     c_back_abs=float(min(np.abs(res).min(), 100.0)) / 10.0, c_sets_frac=fr,
                     c_n_close=float(min((np.abs(res - 6) <= 15).sum(), 6)), c_par_ll=par_ll)
        for name in AUXF + CARDF:
            f.setdefault(name, 0.0)
        out.append(dict(gi=gi, k=k, tee=h["tee"], D=D, cover=h.get("cover", [k]), f=f))
    return out


# ----------------------------------------------------------------------------------------------- instances
class Instance:
    pass


def osm_scene(e):
    fc = S.load_fc(e["osm"])
    course = json.load(open(e["course"])) if os.path.exists(e["course"]) else {}
    sc = S.scene_from_osm(fc, course.get("boundary"))
    truth = S.truth_from_osm(fc, sc.proj)
    refs = [h["ref"] for h in truth]
    N = len(refs) if refs and len(set(refs)) == len(refs) and sorted(refs) == list(range(1, len(refs) + 1)) else None
    return sc, truth, N


def build(e, mode="osm", card_mode="none", use_aux=True, virtual=True):
    """-> Instance (sc, geo, pairs, truth labels) or None. mode: osm | perc | degraded. card_mode: none | web | truth."""
    sc0, truth, N = osm_scene(e)
    if N not in (9, 18):
        return None
    if mode == "osm":
        sc = sc0
    elif mode == "degraded":
        import random
        sc = S.degrade(sc0, random.Random(f"zt-{e['slug']}"), level=1.0)
    else:
        obj = perception_scene_obj(e["slug"])
        if obj is None:
            return None
        sc = S.scene_from_perception(obj, proj=sc0.proj)
    if not sc.greens or not sc.tees:
        return None
    card = None
    if card_mode == "web":
        card = load_card(e["slug"])
        if card is None:
            return None
    elif card_mode == "truth":
        card = card_from_truth(truth)
    geo = V.Geo(sc)
    nv = add_virtual_tees(sc, geo) if virtual else 0
    aux = load_aux(e["slug"], sc.proj) if use_aux else None
    pairs = pair_features(sc, geo, aux, card)
    inst = Instance()
    inst.slug, inst.state, inst.split, inst.mode, inst.card_mode = e["slug"], e["state"], e["split"], mode, card_mode
    inst.sc, inst.geo, inst.pairs, inst.truth, inst.N, inst.n_virtual = sc, geo, pairs, truth, N, nv
    inst.has_aux = aux is not None
    # truth: per true hole, its green and the acceptable candidates
    import eval as E                                                 # structure/eval.py
    R = geo.gr_r
    inst.true_g = []
    inst.ok = set()
    for t in truth:
        gi = E.true_green(geo.G, R, t["green"])
        inst.true_g.append(gi)
    for p in pairs:
        for j, t in enumerate(truth):
            if inst.true_g[j] == p["gi"] and E.tee_ok(p["tee"], list(geo.cx[p["k"]]["xy"]), t):
                inst.ok.add((p["gi"], p["k"]))
    inst.y = np.array([int((p["gi"], p["k"]) in inst.ok) for p in pairs])
    inst.X = np.array([[p["f"][n] for n in FEATS] for p in pairs], float) if pairs else np.zeros((0, len(FEATS)))
    return inst
