"""joint routing v2: the card as the sequence, with missing detections inferred where the card says a hole must be.

Same local evidence as solve.py (hole / walk / start / end models, crossing count, card residual per position), but a
hole whose tee or green was not detected is no longer a free placeholder: its missing end is placed by the card.

Options per position i (card yardage y_i, sets as solve.card_sets):
  real (t, g)   detected tee complex t -> detected green g: hole + card + detection terms (as solve.py)
  VT(g)         green g detected, tee not: the tee lies on the ring [RING_LO, RING_HI] * y_i around g (doglegs make
                the straight distance shorter than the card), and must be a short walk from the previous green
  VG(t)         tee t detected, green not: the green lies on the ring around t, a short walk from the next tee
  MISS          nothing detected for this hole (fixed cost; the walks around it are not scored)

The walk into position i depends on how position i-1 ended (state "last"):
  green g'           real or VT hole: walk model (real tee) / ring gap |D(g', g) vs ring(y_i)| (VT)
  pending VG(t')     the green of hole i-1 is on the ring around t': ring gap of the next tee, or of the next VT
                     ring (two annuli)
  unknown (MISS)     walk_miss
Loops start / end at the clubhouse (start / end models; virtual ends by their ring gap to the clubhouse).

Search: beam over positions, state (greens used, tees used, last), as solve.beam; deterministic (stable sorts,
first-occurrence dedup). `margins` = per-position min-marginals (forbid that position's green, or its tee for VG).
"""
from __future__ import annotations

import numpy as np

import solve as S1

BIG = 1e6
DEF2 = dict(S1.DEF, K=18, beam=3000, tee_reuse=1, c_vt=4.0, c_vg=5.0, c_miss=9.0, c_vv=2.0,
            ring_lo=0.82, ring_hi=1.03, v_base=0.4, v0=25.0, v1=45.0, v_max=9.0, start_v=2.5,
            card_tol=0.12, ph_card=0.002, reuse_cost=1.5, lag_iters=60, lag_step=1.0, w_tree=0.0,
            n_bear=24, r_virt=0.95, w_cov=3.0, cov_min=0.35, par3_yd=250.0, w_ob=4.0, w_onob=3.0, w_obr=4.0, w_covl=0.0,
            w_pr=0.0, set_corr=0.0)

REAL, VT, VG, MISS = 0, 1, 2, 3


def _corridor():
    """this directory's corridor.py, loaded by path: course_data/truth/ has a corridor.py too, and whichever directory
    is first on sys.path (a tier A build puts truth/ there) would win a plain import"""
    import importlib.util
    import os
    import sys
    m = sys.modules.get("joint_corridor")
    if m is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "corridor.py")
        spec = importlib.util.spec_from_file_location("joint_corridor", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        sys.modules["joint_corridor"] = m
    return m


def consistent_sets(Y, min_corr=0.5):
    """drop tee sets whose hole-by-hole yardages do not follow the card's other sets (correlation with their median
    < min_corr): a set listed in another order (derryfield_nh's web card holds one) fits wrong holes at every
    position, and the card cost takes the best set per position"""
    if Y is None or len(Y) < 3 or not min_corr:
        return Y
    keep = []
    for k in range(len(Y)):
        med = np.median(np.delete(Y, k, axis=0), axis=0)
        c = np.corrcoef(Y[k], med)[0, 1] if np.std(Y[k]) > 0 and np.std(med) > 0 else 1.0
        keep.append(c >= min_corr)
    return Y[np.asarray(keep)] if any(keep) else Y


def ring_gap(D, y, lo, hi):
    """distance from a point at D to the annulus [lo*y, hi*y] around the other point"""
    return np.maximum(0.0, np.maximum(lo * y - D, D - hi * y))


def annuli_gap(D, y1, y2, lo, hi):
    """min distance between the annuli [lo, hi]*y1 and [lo, hi]*y2 around two points D apart"""
    a1, b1, a2, b2 = lo * y1, hi * y1, lo * y2, hi * y2
    return np.maximum.reduce([np.zeros_like(D), D - b1 - b2, a1 - D - b2, a2 - D - b1])


class Problem2:
    def __init__(self, d, card=None, params=None):
        P = dict(DEF2)
        P.update(params or {})
        self.P = P
        self.d = d
        co, geo, sc = d["co"], d["geo"], d["sc"]
        self.N = N = int(d["kind"])
        self.loop = 9 if N % 9 == 0 else N
        ng, nt = len(co["G"]), len(co["T"])
        self.ng, self.nt = ng, nt
        self.Y = consistent_sets(S1.card_sets(card, N), P.get("set_corr", 0.0))
        cp = (card or {}).get("par") or []
        self.card_par = [int(cp[i % len(cp)]) if cp[i % len(cp)] else None for i in range(N)] if cp else None
        self._xf = None
        ph = {(int(t), int(g)): float(p) for (t, g), p in zip(d["hp"], sc["ph"])}
        self.ph = ph
        # real candidates: per green its K best tees, anything decent, and (with a card) any pair whose play length
        # fits some position's yardage within card_tol
        ys = np.unique(self.Y.ravel()) if self.Y is not None else np.zeros(0)
        cand = []
        for g in range(ng):
            ts = sorted(((p, t) for (t, gg), p in ph.items() if gg == g), reverse=True)
            for r, (p, t) in enumerate(ts):
                keep = (r < P["K"] and p >= P["ph_min"]) or p >= 0.2
                if not keep and len(ys) and p >= P["ph_card"]:
                    L = float(geo["P"][t, g])
                    keep = bool(np.any(np.abs(ys - L) <= P["card_tol"] * ys))
                if keep:
                    cand.append((REAL, t, g))
        if ng > 63 or nt > 63:
            raise ValueError("too many candidates")
        self.real = len(cand)
        cand += [(VT, -1, g) for g in range(ng)]
        cand += [(VG, t, -1) for t in range(nt)]
        cand.append((MISS, -1, -1))
        self.cand = cand
        C = len(cand)
        self.typ = np.array([k for k, t, g in cand])
        self.ct = np.array([t for k, t, g in cand])
        self.cg = np.array([g for k, t, g in cand])
        one = np.uint64(1)
        self.gbit = np.array([one << np.uint64(g) if g >= 0 else np.uint64(0) for k, t, g in cand], np.uint64)
        tb = [one << np.uint64(t) for t in range(nt)]
        ids = [str(tt.get("id")) for tt in co["T"]]
        pos = {v: j for j, v in enumerate(ids)}
        for j, v in enumerate(ids):                  # a split complex's halves (route_scene.split_complex): the whole
            if "/" in v and v.rsplit("/", 1)[0] in pos:   # complex clashes with each half, the halves not with each other
                tb[pos[v.rsplit("/", 1)[0]]] |= one << np.uint64(j)
        self.tbit = np.array([tb[t] if t >= 0 else np.uint64(0) for k, t, g in cand], np.uint64)
        self.reuse = float(P["reuse_cost"]) if P.get("tee_reuse") else None   # a complex may serve 2+ holes, at a cost
        Gp = np.clip(co["Gp"], 0.03, 0.97)
        Tp = np.clip(np.array([t["p"] for t in co["T"]]), 0.03, 0.97) if nt else np.zeros(0)
        lg = np.log(Gp / (1 - Gp))
        lt = np.log(Tp / (1 - Tp)) if nt else np.zeros(0)
        base = np.zeros(C)
        for c, (k, t, g) in enumerate(cand):
            if k == REAL:
                base[c] = P["w_h"] * S1._nl(ph[(t, g)]) - P["w_dg"] * lg[g] - P["w_dt"] * lt[t]
            elif k == VT:
                base[c] = P["c_vt"] - P["w_dg"] * lg[g]
            elif k == VG:
                base[c] = P["c_vg"] - P["w_dt"] * lt[t]
            else:
                base[c] = P["c_miss"]
        pp = sc.get("pp")                                              # route_learn practice-green model
        if P["w_pr"] and pp is not None and len(pp) == ng:
            cost_pr = -np.log(np.clip(1.0 - np.asarray(pp, float), 0.02, 1.0))
            for c, (k, t, g) in enumerate(cand):
                if g >= 0:
                    base[c] += P["w_pr"] * cost_pr[g]
        self.rast = _corridor().Raster(co)
        Tc0 = geo["Tc"]
        if self.real:
            rt = np.array([t for k, t, g in cand[:self.real]])
            rg = np.array([g for k, t, g in cand[:self.real]])
            self.ob_real = self.rast.frac(Tc0[rt], co["G"][rg], self.rast.obst)
            base[:self.real] += P["w_obr"] * self.ob_real
            self.tree_real = self.rast.frac(Tc0[rt], co["G"][rg], self.rast.tree, 0.15, 0.85)
            base[:self.real] += P["w_tree"] * self.tree_real
        self.base = base
        self._spots = {}
        # geometry
        G = co["G"]
        Tc = geo["Tc"]
        self.Dgg = np.hypot(G[:, None, 0] - G[None, :, 0], G[:, None, 1] - G[None, :, 1])
        self.Dtt = np.hypot(Tc[:, None, 0] - Tc[None, :, 0], Tc[:, None, 1] - Tc[None, :, 1]) if nt else np.zeros((0, 0))
        self.Dtg = geo["D"]                                            # [t, g]
        club = co.get("club")
        self.club = None if club is None else np.asarray(club, float)
        self.Dcg = np.hypot(G[:, 0] - club[0], G[:, 1] - club[1]) if club is not None else None
        self.Dct = np.hypot(Tc[:, 0] - club[0], Tc[:, 1] - club[1]) if (club is not None and nt) else None
        # walk model between real greens and tee complexes
        pw = np.zeros((ng, nt))
        for (g, t), p in zip(d["wp"], sc["pw"]):
            pw[g, t] = p
        self.wn = np.minimum(P["w_w"] * S1._nl(pw), P["c_nowalk"]) if nt else np.zeros((ng, 0))
        self.ps = np.asarray(sc["ps"], float)
        self.pe = np.asarray(sc["pe"], float)
        # end index of each option: 0 none, 1..ng green, ng+1..ng+nt pending VG at tee, E-1 unknown
        self.E = E = 1 + ng + nt + 1
        self.endi = np.array([1 + g if k in (REAL, VT) else (1 + ng + t if k == VG else E - 1)
                              for k, t, g in cand], np.int64)
        # crossings between real candidates
        X = np.zeros((C, C), np.uint8)
        for a in range(self.real):
            _, ta, ga = cand[a]
            for b in range(a + 1, self.real):
                _, tb, gb = cand[b]
                if ta == tb or ga == gb:
                    continue
                if S1.segs_cross(Tc[ta], G[ga], Tc[tb], G[gb]):
                    X[a, b] = X[b, a] = 1
        self.X = X
        self.R = None
        if self.Y is not None:
            K = len(self.Y)
            R = np.full((K, N, C), np.nan)
            for c in range(self.real):
                _, t, g = cand[c]
                pb = geo["Pbox"][t][g]
                if pb is None:
                    pb = np.array([geo["P"][t, g]])
                R[:, :, c] = np.min(np.abs(pb[None, None, :] - self.Y[:, :, None]), axis=2)
            self.R = R
        self.kstar = None

    # ---------------------------------------------------------------- per-position tables
    def ygeom(self):
        """card yardage per position used to place virtual ends: the chosen tee set, else the median set"""
        if self.Y is None:
            return None
        if self.kstar is not None:
            return self.Y[self.kstar]
        return np.median(self.Y, axis=0)

    def wpar(self, gap):
        P = self.P
        return np.minimum(P["v_base"] + np.maximum(0.0, gap - P["v0"]) / P["v1"], P["v_max"])

    def card_cost(self):
        """[N, C] per-(position, option) cost: the card term + the weighted extra features (P['xw'], route_struct)"""
        cc = self.card_term()
        xw = self.P.get("xw") or {}
        if xw:
            F = self.extra()
            for k, w in xw.items():
                if w and k in F:
                    cc = cc + float(w) * F[k]
        return cc

    def extra(self):
        """extra per-(position, option) features [N, C] (cached): learned weights P['xw'] (route_struct.py)"""
        if getattr(self, "_xf", None) is None:
            self._xf = extra_features(self)
        return self._xf

    def card_term(self):
        C = len(self.cand)
        if self.R is None:
            return np.zeros((self.N, C))
        r = np.min(self.R, axis=0)
        if self.kstar is not None:
            r = np.minimum(self.R[self.kstar], r + self.P["set_slack"])
        cc = self.P["w_c"] * S1.card_llr(r, self.P)
        return np.where(np.isnan(r), 0.0, cc)

    def spots(self):
        """virtual tee / green spots per (object, position, bearing) on the card ring, with a corridor cost:
        fairway cover short of cov_min on a par 4 / 5 line, line over obstacles, spot on an obstacle.
        -> dict(vt=[ng, N, B, 2], vtc=[ng, N, B], vg=[nt, N, B, 2], vgc=[nt, N, B]) (cached per tee set)"""
        key = self.kstar
        if key in self._spots:
            return self._spots[key]
        P = self.P
        y = self.ygeom()
        if y is None:
            self._spots[key] = None
            return None
        B = int(P["n_bear"])
        ang = 2 * np.pi * np.arange(B) / B
        U = np.c_[np.cos(ang), np.sin(ang)]                              # [B, 2]
        r = P["r_virt"] * np.asarray(y, float)                         # [N]
        off = r[:, None, None] * U[None, :, :]                         # [N, B, 2]
        R = self.rast
        need = np.where(np.asarray(y) >= P["par3_yd"], P["cov_min"], 0.0)[None, :, None]

        def cost(A, S):                                                # A [n, 1, 1, 2] object, S [n, N, B, 2] spot
            c = P["w_ob"] * R.frac(S, A, R.obst) + P["w_onob"] * R.at(S, R.obst) + \
                P["w_tree"] * R.frac(S, A, R.tree, 0.15, 0.85)
            if R.has_fair:
                fr = R.frac(S, A, R.fair)
                c = c + P["w_cov"] * np.maximum(0.0, need - fr) + P["w_covl"] * (need > 0) * (1.0 - fr)
            return c
        G = self.d["co"]["G"]
        Tc = self.d["geo"]["Tc"]
        vt = G[:, None, None, :] + off[None]
        vg = Tc[:, None, None, :] + off[None] if self.nt else np.zeros((0,) + off.shape)
        out = dict(vt=vt, vtc=cost(G[:, None, None, :], vt),
                   vg=vg, vgc=cost(Tc[:, None, None, :], vg) if self.nt else np.zeros(vg.shape[:3]))
        self._spots[key] = out
        return out

    def start_cost(self, i):
        """[C] cost of option c starting a loop at position i"""
        P = self.P
        sp = self.spots()
        out = np.full(len(self.cand), P["w_s"] * 3.0)
        rT = np.nonzero((self.typ == REAL) | (self.typ == VG))[0]
        out[rT] = P["w_s"] * S1._nl(self.ps[self.ct[rT]], 1e-3)
        rV = np.nonzero(self.typ == VT)[0]
        if sp is not None and self.club is not None:
            S = sp["vt"][self.cg[rV], i]                                # [n, B, 2]
            dc = np.hypot(*(S - self.club).transpose(2, 0, 1))
            out[rV] = P["start_v"] + np.min(sp["vtc"][self.cg[rV], i] + self.wpar(dc), axis=1)
        elif sp is not None:
            out[rV] = P["w_s"] * 3.0 + np.min(sp["vtc"][self.cg[rV], i], axis=1)
        return out

    def end_cost(self, i):
        """[E] cost of ending a loop at position i in each end state"""
        P = self.P
        sp = self.spots()
        out = np.full(self.E, P["w_s"] * 3.0)
        out[1:1 + self.ng] = P["w_s"] * S1._nl(self.pe, 1e-3)
        if sp is not None and self.nt:
            if self.club is not None:
                dc = np.hypot(*(sp["vg"][:, i] - self.club).transpose(2, 0, 1))
                out[1 + self.ng:1 + self.ng + self.nt] = P["start_v"] + np.min(sp["vgc"][:, i] + self.wpar(dc), axis=1)
            else:
                out[1 + self.ng:1 + self.ng + self.nt] = P["w_s"] * 3.0 + np.min(sp["vgc"][:, i], axis=1)
        return out

    def trans(self, i):
        """[E, C] walk cost into position i (i >= 1) from each end state of position i - 1"""
        P = self.P
        ng, nt, E = self.ng, self.nt, self.E
        C = len(self.cand)
        sp = self.spots()
        Tm = np.full((E, C), P["walk_miss"])
        typ, ct, cg = self.typ, self.ct, self.cg
        rT = np.nonzero((typ == REAL) | (typ == VG))[0]
        rV = np.nonzero(typ == VT)[0]
        G = self.d["co"]["G"]
        Tc = self.d["geo"]["Tc"]
        Tm[1:1 + ng][:, rT] = self.wn[:, ct[rT]]
        if sp is not None:
            # real green g' -> virtual tee spot of VT(g) at i
            S = sp["vt"][cg[rV], i]                                     # [nv, B, 2]
            dd = np.hypot(G[:, None, None, 0] - S[None, :, :, 0], G[:, None, None, 1] - S[None, :, :, 1])
            Tm[1:1 + ng][:, rV] = np.min(sp["vtc"][cg[rV], i][None] + self.wpar(dd), axis=2)
            if nt:
                # pending virtual green of VG(t') at i - 1 -> real tee t
                Sg = sp["vg"][:, i - 1]                                 # [nt, B, 2]
                Tu = Tc[ct[rT]]                                         # [nr, 2]
                dd = np.hypot(Sg[:, None, :, 0] - Tu[None, :, None, 0], Sg[:, None, :, 1] - Tu[None, :, None, 1])
                Tm[1 + ng:1 + ng + nt][:, rT] = np.min(sp["vgc"][:, i - 1][:, None, :] + self.wpar(dd), axis=2)
                # ... -> virtual tee spot of VT(g): both ends virtual
                dd = np.hypot(Sg[:, None, :, None, 0] - S[None, :, None, :, 0],
                              Sg[:, None, :, None, 1] - S[None, :, None, :, 1])          # [nt, nv, B, B]
                c2 = sp["vgc"][:, i - 1][:, None, :, None] + sp["vtc"][cg[rV], i][None, :, None, :] + self.wpar(dd)
                Tm[1 + ng:1 + ng + nt][:, rV] = P["c_vv"] + c2.min(axis=(2, 3))
        Tm[0, :] = P["walk_miss"]
        return Tm


XFEATS = ("g_map", "g_small", "g_club_mid", "t_low", "card_rel", "par_bad", "vt_p3", "vg_p3", "not_top_t",
          "not_top_g", "ph_lo")


def extra_features(pr):
    """{name: [N, C]} candidate / position features the base objective lacks (0 where they do not apply):
    g_map        the green is a U-Net map green (route_learn.augment_scene), real or VT option
    g_small      green area < 250 m2 (practice / false greens)
    g_club_mid   green within 100 yd of the clubhouse at a position that does not end a loop (practice greens)
    t_low        tee complex detector p < 0.4 (real / VG)
    card_rel     |play length - card| / card (best tee set, capped 0.5), real options
    par_bad      card par 3 with a play length > 260 yd, or par >= 4 under 200 yd (real)
    vt_p3, vg_p3 a virtual tee / green on a card par 3
    not_top_t    the tee is not the green's best-scored tee (hole model), not_top_g: the green not the tee's best
    ph_lo        hole model p < 0.05 (real)"""
    d = pr.d
    co, geo = d["co"], d["geo"]
    N, C = pr.N, len(pr.cand)
    typ, ct, cg = pr.typ, pr.ct, pr.cg
    F = {k: np.zeros((N, C)) for k in XFEATS}
    ga = d.get("_gattr")
    hasg = cg >= 0
    if ga is not None and len(ga) == pr.ng:
        gm = np.nan_to_num(ga[:, 2]) > 0
        gs = np.nan_to_num(ga[:, 1], nan=1e9) < 250
        F["g_map"][:] = np.where(hasg, gm[np.maximum(cg, 0)], False)[None]
        F["g_small"][:] = np.where(hasg, gs[np.maximum(cg, 0)], False)[None]
    if pr.Dcg is not None:
        near = pr.Dcg < 100
        ends = np.zeros(N, bool)
        ends[pr.loop - 1::pr.loop] = True
        F["g_club_mid"][~ends] = np.where(hasg, near[np.maximum(cg, 0)], False)[None]
    if pr.nt:
        tp = np.array([t["p"] for t in co["T"]])
        hast = (ct >= 0) & (typ != VT)
        F["t_low"][:] = np.where(hast, tp[np.maximum(ct, 0)] < 0.4, False)[None]
    real = np.arange(C) < pr.real
    if pr.real:
        rt, rg = ct[:pr.real], cg[:pr.real]
        L = geo["P"][rt, rg]
        y = pr.ygeom()
        if pr.R is not None:
            with np.errstate(all="ignore"):
                r = np.nanmin(pr.R, axis=0)[:, :pr.real]                # [N, real] yd
            F["card_rel"][:, :pr.real] = np.minimum(np.nan_to_num(r / np.maximum(pr.Y.min(0), 1.0)[:, None], nan=0.0), 0.5)
        pars = pr.card_par
        if pars is not None:
            for i in range(N):
                p = pars[i]
                if p == 3:
                    F["par_bad"][i, :pr.real] = L > 260
                elif p and p >= 4:
                    F["par_bad"][i, :pr.real] = L < 200
        phv = np.array([pr.ph[(int(t), int(g))] for t, g in zip(rt, rg)])
        F["ph_lo"][:, :pr.real] = (phv < 0.05)[None]
        Ph = np.zeros((pr.nt, pr.ng))
        for (t, g), p in pr.ph.items():
            Ph[t, g] = p
        F["not_top_t"][:, :pr.real] = (Ph[rt, rg] < Ph[:, rg].max(0) - 1e-9)[None]
        F["not_top_g"][:, :pr.real] = (Ph[rt, rg] < Ph[rt, :].max(1) - 1e-9)[None]
    if pr.card_par is not None:
        p3 = np.array([pr.card_par[i] == 3 for i in range(N)])
        F["vt_p3"][p3] = (typ == VT)[None]
        F["vg_p3"][p3] = (typ == VG)[None]
    return F


def tables(pr):
    """per-position tables shared by the searches: card cost [N, C], transitions [N] of [E, C] (None at 0), start
    costs at loop starts, end costs at loop ends"""
    key = ("tab", pr.kstar)
    if key not in pr._spots:
        N = pr.N
        cc = pr.card_cost()
        Tm = [None] + [pr.trans(i) for i in range(1, N)]
        st = {i: pr.start_cost(i) for i in range(0, N, pr.loop)}
        en = {i: pr.end_cost(i) for i in range(pr.loop - 1, N, pr.loop)}
        pr._spots[key] = (cc, Tm, st, en)
    return pr._spots[key]


def viterbi(pr, price, fix=None, forbid=None):
    """the routing problem without the used-once constraints (and without crossings): exact DP over positions with
    state = how the previous hole ended. price [C] is added to every option (Lagrange multipliers).
    -> (cost, [cand per position])"""
    N, C, E = pr.N, len(pr.cand), pr.E
    cc, Tm, st, en = tables(pr)
    V = None
    back = []
    for i in range(N):
        step = pr.base + cc[i] + price + _mask(pr, i, fix, forbid)
        if i == 0:
            new = st[0] + step
            arg = np.zeros(C, np.int64)
        else:
            M = V[:, None] + Tm[i]
            if i % pr.loop == 0:
                M = np.minimum(M, (V + en[i - 1])[:, None] + st[i][None, :])
            arg = np.argmin(M, axis=0)
            new = M[arg, np.arange(C)] + step
        back.append(arg)
        V = np.full(E, BIG * 100)
        np.minimum.at(V, pr.endi, new)
        best_c = np.full(E, -1, np.int64)
        order = np.lexsort((np.arange(C), new))
        for c in order[::-1]:
            best_c[pr.endi[c]] = c
        back[-1] = (arg, best_c)
    V = V + en[N - 1]
    e = int(np.argmin(V))
    cost = float(V[e])
    seq = []
    for i in range(N - 1, -1, -1):
        arg, best_c = back[i]
        c = int(best_c[e])
        seq.append(c)
        e = int(arg[c])
    return cost, seq[::-1]


def _mask(pr, i, fix, forbid):
    C = len(pr.cand)
    allow = np.ones(C, bool)
    if fix and i in fix:
        f = fix[i]
        if isinstance(f, tuple) and f[0] == "g":
            allow = pr.cg == f[1]
        elif isinstance(f, tuple) and f[0] == "c":
            allow = np.arange(C) == f[1]
        else:
            allow = pr.ct == f
        if not allow.any():
            allow = np.ones(C, bool)
    for (pi, kind, j) in forbid or ():
        if pi == i:
            allow &= (pr.cg != j) if kind == "g" else (pr.ct != j)
    return np.where(allow, 0.0, BIG)


def lagrange(pr, iters=None, fix=None, forbid=None):
    """subgradient on green (and, without tee reuse, tee) prices so the relaxed DP uses every green at most once.
    -> option price vector [C] (used by beam2 to rank partial routings by their cost to the rest of the course)"""
    P = pr.P
    iters = int(P["lag_iters"] if iters is None else iters)
    lam = np.zeros(pr.ng)
    mu = np.zeros(pr.nt)
    gi = np.where(pr.cg >= 0, pr.cg, 0)
    ti = np.where(pr.ct >= 0, pr.ct, 0)
    hasg = pr.cg >= 0
    hast = (pr.ct >= 0) & (pr.typ != VT)
    step0 = float(P["lag_step"])
    best = None
    for it in range(iters):
        price = np.where(hasg, lam[gi], 0.0) + (np.where(hast, mu[ti], 0.0) if pr.reuse is None else 0.0)
        cost, seq = viterbi(pr, price, fix, forbid)
        ng_use = np.bincount([pr.cg[c] for c in seq if pr.cg[c] >= 0], minlength=pr.ng)
        nt_use = np.bincount([pr.ct[c] for c in seq if pr.ct[c] >= 0 and pr.typ[c] != VT], minlength=pr.nt)
        dual = cost - lam.sum() - (mu.sum() if pr.reuse is None else 0.0)
        if best is None or dual > best[0]:
            best = (dual, price.copy())
        sg = ng_use - 1.0
        st = nt_use - 1.0
        if np.all(sg <= 0) and (pr.reuse is not None or np.all(st <= 0)):
            break
        a = step0 / (1.0 + it * 0.1)
        lam = np.maximum(0.0, lam + a * sg)
        mu = np.maximum(0.0, mu + a * st)
    return best[1]


def topk(v, k):
    """indices of the k smallest values of v, ties broken by index (deterministic; the C port selects the same set)"""
    if k >= len(v):
        return np.arange(len(v))
    thr = v[np.argpartition(v, k - 1)[k - 1]]
    lo = np.nonzero(v < thr)[0]
    eq = np.nonzero(v == thr)[0]
    return np.concatenate([lo, eq[:k - len(lo)]])


def beam2(pr, fix=None, forbid=None, beam_w=None, keep=1, price=None):
    """Beam over positions, state (greens used, tees used, last end). States are ranked by cost + price of the
    options used (Lagrange prices from `lagrange`: what taking a green now costs the rest of the course), and
    scored by their true cost. fix {pos: ('c', cand) | ('g', green) | tee}; forbid {(pos, 'g'|'t', index)}.
    -> [(true cost, [cand index per position])] best first"""
    P = pr.P
    B = beam_w or P["beam"]
    N, C = pr.N, len(pr.cand)
    cc, Tm, st, en = tables(pr)
    fr = _fastroute()
    if fr is not None:
        return _beam_c(fr, pr, B, keep, price, cc, Tm, st, en, fix, forbid)
    gm = np.zeros(1, np.uint64)
    tm = np.zeros(1, np.uint64)
    last = np.zeros(1, np.int64)
    rank = np.zeros(1)
    true = np.zeros(1)
    pz = np.zeros(C) if price is None else price
    acc = np.zeros((1, C), np.uint8)
    back = []
    wx = P["w_x"]
    K1 = np.uint64(0x9E3779B97F4A7C15)
    K2 = np.uint64(0xC2B2AE3D27D4EB4F)
    for i in range(N):
        step = pr.base + cc[i] + _mask(pr, i, fix, forbid)
        if i == 0:
            tr = st[0][None, :]
        else:
            tr = Tm[i][last]
            if i % pr.loop == 0:
                tr = np.minimum(tr, en[i - 1][last][:, None] + st[i][None, :])
        add = step[None, :] + tr + wx * acc
        tclash = (tm[:, None] & pr.tbit[None, :]) != 0
        if pr.reuse is not None:
            add = add + pr.reuse * tclash
            bad = (gm[:, None] & pr.gbit[None, :]) != 0
        else:
            bad = ((gm[:, None] & pr.gbit[None, :]) != 0) | tclash
        add = np.where(bad, BIG * 10, add)
        tru = (true[:, None] + add).ravel()
        flat = (rank[:, None] + add + pz[None, :]).ravel()
        idx = topk(flat, min(len(flat), B * 4))
        idx = idx[tru[idx] < BIG]
        if not len(idx):
            return []
        idx = idx[np.lexsort((idx, flat[idx]))]                     # rank, then index: deterministic ties
        par, c = idx // C, idx % C
        ngm, ntm = gm[par] | pr.gbit[c], tm[par] | pr.tbit[c]
        nl = pr.endi[c]
        key = (ngm * K1) ^ (ntm * K2) ^ nl.astype(np.uint64)
        _, first = np.unique(key, return_index=True)
        first = np.sort(first)[:B]
        fi = idx[first]
        par, c = par[first], c[first]
        gm, tm, last = ngm[first], ntm[first], nl[first]
        rank, true = flat[fi], tru[fi]
        acc = acc[par] + pr.X[c]
        back.append((par, c))
    score = true + en[N - 1][last]
    out = []
    for j in np.argsort(score, kind="stable")[:keep]:
        seq, k = [], int(j)
        for par, c in reversed(back):
            seq.append(int(c[k]))
            k = int(par[k])
        out.append((float(score[j]), seq[::-1]))
    return out


_FR = []


def _fastroute():
    """the C beam (platform/fastc/routing) unless GOLF_FASTC=0 or it cannot be built"""
    import os
    import sys
    if not _FR:
        d = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "platform",
                         "fastc", "routing")
        if d not in sys.path:
            sys.path.insert(0, d)
        try:
            import fastroute
            _FR.append(fastroute if fastroute.lib() is not None else None)
        except Exception:                                            # noqa: BLE001
            _FR.append(None)
    if _FR[0] is None or os.environ.get("GOLF_FASTC", "1") == "0":
        return None
    return _FR[0]


def _beam_c(fr, pr, B, keep, price, cc, Tm, st, en, fix, forbid):
    N, C, E = pr.N, len(pr.cand), pr.E
    step = np.stack([pr.base + cc[i] + _mask(pr, i, fix, forbid) for i in range(N)])
    T = np.zeros((N, E, C))
    for i in range(1, N):
        T[i] = Tm[i]
    S = np.zeros((N, C))
    for i, v in st.items():
        S[i] = v
    En = np.zeros((N, E))
    for i, v in en.items():
        En[i] = v
    return fr.beam(N, C, E, B, pr.loop, step, T, S, En, pr.gbit, pr.tbit, pr.endi, pr.X, price, pr.reuse,
                   pr.P["w_x"], keep)


def search(pr, fix=None, forbid=None, beam_w=None):
    """the plain beam and the Lagrange-priced beam; the lower true cost wins (plain first on a tie)"""
    r = beam2(pr, fix, forbid, beam_w)
    if pr.P.get("lag_iters", 0) > 0:
        price = lagrange(pr, fix=fix, forbid=forbid)
        r2 = beam2(pr, fix, forbid, beam_w, price=price)
        if r2 and (not r or r2[0][0] < r[0][0] - 1e-9):
            r = r2
    return r


def solve(d, card=None, params=None, fix=None):
    pr = Problem2(d, card, params)
    res = search(pr, fix)
    if not res:
        return dict(cost=None, seq=[], holes=[], pr=pr)
    if pr.R is not None and pr.P["two_pass"] and len(pr.Y) > 1:
        cost, seq = res[0]
        real = [(i, c) for i, c in enumerate(seq) if c < pr.real]
        if len(real) >= pr.N // 2:
            tot = [np.median([pr.R[k, i, c] for i, c in real]) for k in range(len(pr.Y))]
            pr.kstar = int(np.argmin(tot))
            res = search(pr, fix)
    cost, seq = res[0]
    return dict(cost=cost, seq=seq, holes=[pr.cand[c] for c in seq], pr=pr)


def margins(sol, fix=None, beam_w=400):
    pr = sol["pr"]
    out = []
    for i, c in enumerate(sol["seq"]):
        k, t, g = pr.cand[c]
        if k == MISS:
            out.append(0.0)
            continue
        fb = {(i, "g", int(g))} if g >= 0 else {(i, "t", int(t))}
        r = beam2(pr, fix, forbid=fb, beam_w=beam_w)
        if pr.P.get("lag_iters", 0) > 0:
            pz = sol.get("price")
            if pz is None:
                pz = sol["price"] = lagrange(pr, fix=fix)
            r2 = beam2(pr, fix, forbid=fb, beam_w=beam_w, price=pz)
            if r2 and (not r or r2[0][0] < r[0][0]):
                r = r2
        out.append(max(0.0, r[0][0] - sol["cost"]) if r else 99.0)
    return out


def place_virtual(sol):
    """Coordinates (local yd) of the virtual ends: the spot (card ring x bearing) the solver's cost picks given the
    neighbouring hole (previous green for a VT, next tee for a VG; the clubhouse at a loop start / end).
    -> {pos: dict(tee=(x, y)) | dict(green=(x, y))}"""
    pr = sol["pr"]
    co, geo = pr.d["co"], pr.d["geo"]
    G, Tc = co["G"], geo["Tc"]
    sp = pr.spots()
    seq = [pr.cand[c] for c in sol["seq"]]
    N = len(seq)
    out = {}
    if sp is None:
        return out
    for i, (k, t, g) in enumerate(seq):
        if k == VT:
            S, c = sp["vt"][g, i], sp["vtc"][g, i]
            prev = None
            if i % pr.loop and i > 0:
                kp, tp, gp = seq[i - 1]
                prev = G[gp] if gp >= 0 else (out.get(i - 1, {}).get("green"))
            elif pr.club is not None:
                prev = pr.club
            w = pr.wpar(np.hypot(*(S - np.asarray(prev)).T)) if prev is not None else 0.0
            out[i] = dict(tee=tuple(S[int(np.argmin(c + w))]))
        elif k == VG:
            S, c = sp["vg"][t, i], sp["vgc"][t, i]
            nxt = None
            if (i + 1) % pr.loop and i + 1 < N:
                kn, tn, gn = seq[i + 1]
                if tn >= 0:
                    nxt = Tc[tn]
                elif gn >= 0:
                    nxt = G[gn]
            elif pr.club is not None:
                nxt = pr.club
            w = pr.wpar(np.hypot(*(S - np.asarray(nxt)).T)) if nxt is not None else 0.0
            out[i] = dict(green=tuple(S[int(np.argmin(c + w))]))
    return out


REFINE = dict(g_thr=0.3, g_lo=0.70, g_hi=1.08, g_mid=0.93, t_thr=0.3, t_lo=0.80, t_hi=1.10, t_mid=0.97, w_dist=3.0,
              w_fair=0.3, sep_used=18.0, fend_ext=15.0, fend_lo=0.65, fend_hi=1.02, tstart_back=25.0, vt=False)
# vt False: virtual tees stay on the card ring (route_bench train: moving them onto P(tee) / fairway starts lost 4
# holes and won 1; the tee tolerance is loose, the ring spot is at the card's distance)


def refine_virtual(sol, virt, M, params=None):
    """Move the virtual ends place_virtual put on the card ring onto image evidence (route_learn.Maps M bound to the
    course projection, with its P(green) / P(tee) channels): a virtual green goes to the strongest P(green) spot at
    card distance from its tee (>= g_thr), else to the end of a fairway centreline at card distance (pushed
    fend_ext yd beyond it); a virtual tee to the strongest P(tee) spot at card distance from its green, else to the
    far end of a fairway pointing at the green (tstart_back yd behind it). Spots within sep_used yd of a green /
    tee the routing uses elsewhere are skipped. -> {pos: dict(tee=..) | dict(green=..)} (copy, kind 'anchor' noted)"""
    P = dict(REFINE, **(params or {}))
    pr = sol["pr"]
    if M is None or pr.Y is None:
        return virt
    co, geo = pr.d["co"], pr.d["geo"]
    G, Tc = np.asarray(co["G"], float), np.asarray(geo["Tc"], float)
    y = pr.ygeom()
    seq = [pr.cand[c] for c in sol["seq"]]
    usedG = np.array([G[g] for k, t, g in seq if g >= 0]).reshape(-1, 2)
    usedT = np.array([Tc[t] for k, t, g in seq if t >= 0]).reshape(-1, 2)
    ends = []
    for f in co.get("fair") or []:
        cl = np.asarray(f.get("cl") if f.get("cl") is not None else [], float).reshape(-1, 2)
        if len(cl) >= 2 and np.hypot(*(cl[-1] - cl[0])) > 40:
            ends.append((cl[0], cl[-1]))
    ang = np.radians(np.arange(0, 360, 4.0))
    U = np.c_[np.cos(ang), np.sin(ang)]
    out = dict(virt)

    def evidence(o, yi, which, lo, hi, mid, thr, used):
        rs = np.arange(lo * yi, hi * yi + 1e-6, 4.0)
        S = o[None, None, :] + rs[:, None, None] * U[None, :, :]       # [R, A, 2]
        if getattr(M, which, None) is None:
            return None
        pv = M.sample(S, which)
        sc = pv - P["w_dist"] * np.maximum(0.0, np.abs(rs / yi - mid) - 0.06)[:, None]
        if which == "green":
            fr = _line_mean(M, np.broadcast_to(o, S.shape), S, "fair")
            sc = sc + P["w_fair"] * fr
        if len(used):
            dd = np.min(np.hypot(S[..., None, 0] - used[:, 0], S[..., None, 1] - used[:, 1]), -1)
            sc = np.where(dd < P["sep_used"], -9.0, sc)
            pv = np.where(dd < P["sep_used"], 0.0, pv)
        j = np.unravel_index(int(np.argmax(np.where(pv >= thr, sc, -9.0))), sc.shape)
        if pv[j] < thr:
            return None
        c = S[j]
        # weighted centroid of the blob around the best spot
        off = np.stack(np.meshgrid(np.arange(-12, 13, 3.0), np.arange(-12, 13, 3.0)), -1).reshape(-1, 2)
        Q = c + off
        w = M.sample(Q, which)
        w = np.where(w >= 0.6 * pv[j], w, 0.0)
        return tuple((Q * w[:, None]).sum(0) / max(w.sum(), 1e-6)) if w.sum() > 0 else tuple(c)

    for i, (k, t, g) in enumerate(seq):
        v = virt.get(i) or {}
        yi = float(y[i])
        if k == VG and "green" in v:
            o = Tc[t]
            q = evidence(o, yi, "green", P["g_lo"], P["g_hi"], P["g_mid"], P["g_thr"], usedG)
            if q is None and ends:
                best = None
                for a, b in ends:
                    for s0, s1 in ((a, b), (b, a)):           # s1: the end away from the tee
                        D = float(np.hypot(*(s1 - o)))
                        if np.hypot(*(s0 - o)) < D and P["fend_lo"] * yi <= D <= P["fend_hi"] * yi:
                            u = (s1 - s0) / max(np.hypot(*(s1 - s0)), 1.0)
                            e = s1 + P["fend_ext"] * u
                            if len(usedG) and np.min(np.hypot(*(usedG - e).T)) < P["sep_used"]:
                                continue
                            sc = abs(D / yi - 0.9)
                            if best is None or sc < best[0]:
                                best = (sc, tuple(e))
                q = best[1] if best else None
            if q is not None:
                out[i] = dict(green=q, anchor=True)
        elif k == VT and "tee" in v and P["vt"]:
            o = G[g]
            q = evidence(o, yi, "tee", P["t_lo"], P["t_hi"], P["t_mid"], P["t_thr"], usedT)
            if q is None and ends and yi >= 250:
                best = None
                for a, b in ends:
                    for s0, s1 in ((a, b), (b, a)):           # s0: the end away from the green
                        D0, D1 = float(np.hypot(*(s0 - o))), float(np.hypot(*(s1 - o)))
                        if D0 > D1 and D1 < 0.45 * yi and 0.45 * yi <= D0 <= 0.95 * yi:
                            u = (s0 - s1) / max(np.hypot(*(s0 - s1)), 1.0)
                            e = s0 + P["tstart_back"] * u
                            if len(usedT) and np.min(np.hypot(*(usedT - e).T)) < P["sep_used"]:
                                continue
                            sc = abs(float(np.hypot(*(e - o))) / yi - 0.95)
                            if best is None or sc < best[0]:
                                best = (sc, tuple(e))
                q = best[1] if best else None
            if q is not None:
                out[i] = dict(tee=q, anchor=True)
    return out


def _line_mean(M, A, B, which, ns=12):
    s = np.linspace(0.15, 0.85, ns)
    Pt = A[..., None, :] + (B - A)[..., None, :] * s[:, None]
    return M.sample(Pt, which).mean(-1)
