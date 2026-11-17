"""Structured learning of the routing objective's weights (zero_tap/joint/solve2.py), on the routing bench's courses.

The solver's cost of a routing y is linear in a weight vector theta (one weight per cost group below, the solver
parameters they map to in THETA_PARAMS):  cost(y) = theta . phi(y).  On every wrong train course the true routing
cost more than the chosen one (the search is fine, the objective is not), so theta is fitted so that the true
routing y* beats the solver's alternatives by their hole Hamming loss (margin rescaling, structured SVM):

    min_theta  mu/2 |theta - theta0|^2 + 1/n sum_courses max_y [ Delta(y, y*) - theta.(phi(y) - phi(y*)) ]_+

y* = the cheapest routing whose every hole is right where the candidates allow it (positions without a right
candidate are free); the inner max is loss-augmented decoding (the solver itself with every wrong option made
Delta cheaper), the constraints of each round are kept (cutting planes) and theta refitted on all of them.

    python3 route_struct.py check --slugs a,b         phi(y) . theta0 == the solver's own cost
    python3 route_struct.py learn --split train+big --folds 5 --out cache/val/struct/run1
        -> per state fold: theta fitted on the other folds' courses -> fold params (json), all-course params
    then route_bench eval with ROUTER_PARAMS=<fold params> on each fold's courses (out-of-fold validation)

Course inputs: the bench prep pickles + score overrides (ROUTE_BENCH_SC*, out-of-fold for train), as route_bench.run_one
loads them.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]

GROUPS = ["h", "dg", "dt", "vt", "vg", "miss", "obr", "c", "w", "nowalk", "wm", "s", "v", "x", "r"]
XG = os.environ.get("ROUTE_STRUCT_X", "g_map,g_small,g_club_mid,t_low,card_rel,par_bad,vt_p3,vg_p3,not_top_t,not_top_g,"
                    "ph_lo")
GROUPS += ["x:" + k for k in XG.split(",") if k]
THETA_PARAMS = dict(h="w_h", dg="w_dg", dt="w_dt", vt="c_vt", vg="c_vg", miss="c_miss", obr="w_obr", c="w_c", w="w_w",
                    nowalk="c_nowalk", wm="walk_miss", s="w_s", x="w_x", r="reuse_cost")
V_PARAMS = ("v_base", "v_max", "w_ob", "w_onob", "w_cov", "w_covl", "w_tree", "c_vv", "start_v")   # v1 divides


def base_params(extra=None):
    import route_scene as RS
    RS._mods()
    import solve2 as S2
    P = dict(S2.DEF2)
    P.update(RS.V1_PARAMS)
    P.update(RS.V2_PARAMS)
    P.update(extra or {})
    P.pop("no_margins", None)
    return P


def theta_of(P):
    xw = P.get("xw") or {}
    return np.array([float(xw.get(g[2:], 0.0)) if g.startswith("x:") else float(P[THETA_PARAMS[g]]) if g != "v"
                     else 1.0 for g in GROUPS])


def params_of(theta, P0):
    """theta -> solver params (P0's, the cost groups scaled); the 'v' group scales every virtual-geometry term"""
    P = dict(P0)
    P["xw"] = dict(P0.get("xw") or {})
    for k, g in enumerate(GROUPS):
        if g.startswith("x:"):
            P["xw"][g[2:]] = float(theta[k])
        elif g == "v":
            a = float(theta[k])
            for q in V_PARAMS:
                P[q] = P0[q] * a
            P["v1"] = P0["v1"] / max(a, 1e-6)
        else:
            P[THETA_PARAMS[g]] = float(theta[k])
    return P


def delta_params(theta, P0):
    """the solver params of theta as a ROUTER_PARAMS dict (only what differs from the defaults)"""
    P = params_of(theta, P0)
    out = {k: round(v, 5) for k, v in P.items() if isinstance(v, float) and abs(v - P0.get(k, np.nan)) > 1e-9}
    xw = {k: round(v, 5) for k, v in P["xw"].items() if abs(v) > 1e-9}
    if xw:
        out["xw"] = xw
    return out


# ----------------------------------------------------------------------------- course inputs
def load(c, ver, sc_dir):
    """(x, d) as route_bench.run_one prepares them for router v2"""
    import route_bench as RB
    import route_learn as RL
    import route_scene as RS
    RS._mods()
    pp = RB.prep_path(c["slug"], "fast", 0, "v2", ver)
    if not os.path.exists(pp):
        return None
    x, pd = pickle.load(open(pp, "rb"))
    if pd is None:
        return None
    d = dict(pd[0])
    q = os.path.join(sc_dir, c["slug"] + ".pkl") if sc_dir else None
    if q and os.path.exists(q):
        d["sc"] = dict(d["sc"], **pickle.load(open(q, "rb")))
    sc0 = RB.rd(RB.scene_path(c["slug"], ver))
    pv = ver.split("_", 1)[1]
    d["_maps"] = RL.bench_maps(c["slug"], sc0, pv).bind(d["co"]["pj"])
    Pb = RB.bench_probs(c["slug"], pv)
    if Pb is not None:
        d["_maps"].green, d["_maps"].tee = Pb[1], Pb[2]
        sca, _ = RL.augment_scene(sc0, Pb)
        d["_gattr"], d["_tattr"] = RL.obj_attrs(d, sca, d["_maps"])
    return x, d


def correct(pr, d, truth):
    """[N, C] bool: option c at position i is hole i+1 right (labels as route_learn.labels: green within 20 yd of the
    line's end, a tee box within 40 yd of its first 60 %); VT / VG count when their detected end is right"""
    import route_learn as RL
    import solve2 as S2
    lab = RL.labels(d, truth)
    g2h, t2h = lab["g2h"], lab["t2h"]
    N, C = pr.N, len(pr.cand)
    Cor = np.zeros((N, C), bool)
    for c, (k, t, g) in enumerate(pr.cand):
        for i in range(N):
            h = i + 1
            if k == S2.REAL:
                Cor[i, c] = g2h[g] == h and h in t2h[t]
            elif k == S2.VT:
                Cor[i, c] = g2h[g] == h
            elif k == S2.VG:
                Cor[i, c] = h in t2h[t]
    return Cor


# ----------------------------------------------------------------------------- decoding
def _patch(pr, offset):
    """add offset [N, C] to the card cost table (every search reads it through solve2.tables)"""
    if offset is None:
        return
    orig = pr.__class__.card_cost.__get__(pr)
    pr.card_cost = lambda: orig() + offset
    pr._spots = {k: v for k, v in pr._spots.items() if not (isinstance(k, tuple) and k[0] == "tab")}


def decode(d, card, P, offset=None, kstar=None, keep=1):
    """solve2.solve with an extra per-(position, option) cost. kstar: force the tee set (None: the two-pass rule).
    keep > 1: pr.alts = the keep best routings of the plain and the priced beam (constraints for the learner).
    -> (cost, seq, pr)"""
    import solve2 as S2
    pr = S2.Problem2(d, card, P)
    _patch(pr, offset)
    if kstar is not None and pr.Y is not None:
        pr.kstar = kstar
        _patch(pr, offset)
    res = S2.search(pr)
    if not res:
        return None, [], pr
    if kstar is None and pr.R is not None and pr.P["two_pass"] and len(pr.Y) > 1:
        cost, seq = res[0]
        real = [(i, c) for i, c in enumerate(seq) if c < pr.real]
        if len(real) >= pr.N // 2:
            tot = [np.median([pr.R[k, i, c] for i, c in real]) for k in range(len(pr.Y))]
            pr.kstar = int(np.argmin(tot))
            _patch(pr, offset)
            res = S2.search(pr)
    cost, seq = res[0]
    if keep > 1:
        alts = S2.beam2(pr, keep=keep)
        if pr.P.get("lag_iters", 0) > 0:
            alts += S2.beam2(pr, keep=keep, price=S2.lagrange(pr))
        seen, pr.alts = set(), []
        for _, s in alts:
            if tuple(s) not in seen:
                seen.add(tuple(s))
                pr.alts.append(s)
    return cost, seq, pr


def phi(pr, seq):
    """cost groups of a routing (theta . phi == the solver's cost of seq), from pr's own tables (unpatched)"""
    import solve as S1
    import solve2 as S2
    P = pr.P
    f = dict.fromkeys(GROUPS, 0.0)
    co = pr.d["co"]
    Gp = np.clip(co["Gp"], 0.03, 0.97)
    Tp = np.clip(np.array([t["p"] for t in co["T"]]), 0.03, 0.97) if pr.nt else np.zeros(0)
    lg = np.log(Gp / (1 - Gp))
    lt = np.log(Tp / (1 - Tp)) if pr.nt else np.zeros(0)
    cc = pr.__class__.card_cost(pr)
    ct_ = pr.card_term()
    XF = {g[2:]: pr.extra()[g[2:]] for g in GROUPS if g.startswith("x:")}
    Tm = [None] + [pr.trans(i) for i in range(1, pr.N)]
    st = {i: pr.start_cost(i) for i in range(0, pr.N, pr.loop)}
    en = {i: pr.end_cost(i) for i in range(pr.loop - 1, pr.N, pr.loop)}
    ng, nt, E = pr.ng, pr.nt, pr.E
    pw = np.zeros((ng, nt))
    for (g, t), p in zip(pr.d["wp"], pr.d["sc"]["pw"]):
        pw[g, t] = p
    nlw = S1._nl(pw)
    ps, pe = pr.ps, pr.pe

    def start_f(i, c):
        k, t, g = pr.cand[c]
        v = float(st[i][c])
        if k in (S2.REAL, S2.VG):
            f["s"] += float(S1._nl(ps[t], 1e-3))
        elif k == S2.VT and pr.club is not None and pr.spots() is not None:
            f["v"] += v
        elif k == S2.VT and pr.spots() is not None:
            f["s"] += 3.0
            f["v"] += v - P["w_s"] * 3.0
        else:
            f["s"] += 3.0
        return v

    def end_f(i, e):
        v = float(en[i][e])
        if 1 <= e <= ng:
            f["s"] += float(S1._nl(pe[e - 1], 1e-3))
        elif ng + 1 <= e <= ng + nt and pr.spots() is not None:
            if pr.club is not None:
                f["v"] += v
            else:
                f["s"] += 3.0
                f["v"] += v - P["w_s"] * 3.0
        else:
            f["s"] += 3.0
        return v

    def trans_f(i, e, c):
        k, t, g = pr.cand[c]
        v = float(Tm[i][e, c])
        if k == S2.MISS or e == 0 or e == E - 1 or pr.spots() is None and not (1 <= e <= ng and k in (S2.REAL, S2.VG)):
            f["wm"] += 1.0
        elif 1 <= e <= ng and k in (S2.REAL, S2.VG):
            a = P["w_w"] * nlw[e - 1, t]
            if a < P["c_nowalk"]:
                f["w"] += float(nlw[e - 1, t])
            else:
                f["nowalk"] += 1.0
        else:
            f["v"] += v
        return v
    total = 0.0
    last = 0
    used_t = np.uint64(0)
    for i, c in enumerate(seq):
        k, t, g = pr.cand[c]
        if k == S2.REAL:
            f["h"] += float(S1._nl(pr.ph[(t, g)]))
            f["dg"] -= float(lg[g])
            f["dt"] -= float(lt[t])
            f["obr"] += float(pr.ob_real[c])
            total += float(pr.base[c])
        elif k == S2.VT:
            f["vt"] += 1.0
            f["dg"] -= float(lg[g])
            total += float(pr.base[c])
        elif k == S2.VG:
            f["vg"] += 1.0
            f["dt"] -= float(lt[t])
            total += float(pr.base[c])
        else:
            f["miss"] += 1.0
            total += float(pr.base[c])
        if P["w_c"]:
            f["c"] += float(ct_[i, c]) / P["w_c"]
        for k2, F2 in XF.items():
            f["x:" + k2] += float(F2[i, c])
        total += float(cc[i, c])
        if i == 0:
            total += start_f(0, c)
        else:
            a = float(Tm[i][last, c])
            if i % pr.loop == 0 and float(en[i - 1][last] + st[i][c]) < a:
                total += end_f(i - 1, last) + start_f(i, c)
            else:
                total += trans_f(i, last, c)
        if pr.reuse is not None and (used_t & pr.tbit[c]) != 0:
            f["r"] += 1.0
            total += pr.reuse
        used_t |= pr.tbit[c]
        last = int(pr.endi[c])
    total += end_f(pr.N - 1, last)
    nx = 0
    for a in range(len(seq)):
        for b in range(a + 1, len(seq)):
            nx += int(pr.X[seq[a], seq[b]])
    f["x"] = float(nx)
    total += P["w_x"] * nx
    return np.array([f[g] for g in GROUPS]), total


def hamming(Cor, seq):
    return float(sum(not Cor[i, c] for i, c in enumerate(seq) if Cor[i].any()))


def truth_offset(Cor):
    """restrict each position to its right options (free where it has none)"""
    import solve2 as S2
    off = np.where(Cor, 0.0, S2.BIG)
    off[~Cor.any(1)] = 0.0
    return off


# ----------------------------------------------------------------------------- per course work
_CACHE = {}
KEEP = int(os.environ.get("ROUTE_STRUCT_KEEP", "8"))


def course_rows(c, ver, sc_dir, theta, P0, lam=1.0):
    """under theta: the decoded routing, the loss-augmented one and the constrained truth, as phi rows.
    -> dict(slug, phi_true, rows=[(phi, delta)], decoded_delta, n)"""
    key = c["slug"]
    if key not in _CACHE:
        ld = load(c, ver, sc_dir)
        _CACHE[key] = ld
    ld = _CACHE[key]
    if ld is None:
        return None
    x, d = ld
    if x.get("card") is None or len(x["truth"]) != int(x["n"]):
        return None
    P = params_of(theta, P0)
    cost, seq, pr = decode(d, x["card"], P)
    if not seq:
        return None
    Cor = correct(pr, d, x["truth"])
    ks = pr.kstar
    ct, tseq, prt = decode(d, x["card"], P, truth_offset(Cor), kstar=ks)
    if not tseq:
        return None
    off = np.where(Cor, 0.0, -lam)
    off[~Cor.any(1)] = 0.0
    ca, aseq, pra = decode(d, x["card"], P, off, kstar=ks, keep=KEEP)
    out = dict(slug=key, n=int(x["n"]), rows=[], decoded_delta=hamming(Cor, seq), n_right_cand=int(Cor.any(1).sum()))
    pt, _ = phi(prt, tseq)
    out["phi_true"] = pt
    prx = pr
    for s in [seq] + list(getattr(pra, "alts", [aseq])):
        if s:
            ph, _ = phi(prx, s)              # phi under the unpatched problem (kstar as decoded)
            out["rows"].append((ph, hamming(Cor, s)))
    return out


def _job(a):
    c, ver, sc_dir, theta, P0, lam = a
    try:
        return course_rows(c, ver, sc_dir, theta, P0, lam)
    except Exception as e:                                           # noqa: BLE001
        return dict(slug=c["slug"], error=repr(e)[:200])


# ----------------------------------------------------------------------------- fitting
def fit_theta(W, theta0, mu=0.05, fixed=(), tau=0.25):
    """W: {slug: (phi_true, [(phi, delta)])}; smoothed hinge (softplus, temperature tau) over each course's worst
    constraint (log-sum-exp), L2 to theta0, theta >= 0 (L-BFGS-B)"""
    from scipy.optimize import minimize
    items = [(pt, np.array([r[0] for r in rows]), np.array([r[1] for r in rows])) for pt, rows in W.values() if rows]
    n = len(items)
    free = np.array([g not in fixed for g in GROUPS])
    sc = np.maximum(np.abs(theta0), 0.5)

    def obj(z):
        th = theta0.copy()
        th[free] = z * sc[free]
        L = 0.5 * mu * np.sum(((th - theta0) / sc) ** 2)
        G = mu * (th - theta0) / sc ** 2
        for pt, Ph, De in items:
            m = De - (Ph - pt[None, :]) @ th                              # violation of each constraint
            mm = np.max(m)
            e = np.exp((m - mm) / tau)
            lse = mm + tau * np.log(e.sum())                              # smooth max over constraints
            w = e / e.sum()
            sp = tau * np.logaddexp(0.0, lse / tau)                       # smooth hinge
            ds = 1.0 / (1.0 + np.exp(-lse / tau))
            L += sp / n
            G += ds * (-(w @ (Ph - pt[None, :]))) / n
        return L, (G * sc)[free]
    z0 = (theta0 / sc)[free]
    r = minimize(obj, z0, jac=True, method="L-BFGS-B", bounds=[(0.0, None)] * int(free.sum()),
                 options=dict(maxiter=500))
    th = theta0.copy()
    th[free] = r.x * sc[free]
    return th, float(r.fun)


def run_rounds(cs, ver, sc_dir, P0, rounds=6, mu=0.05, lam=1.0, procs=3, log=print, fixed=()):
    from multiprocessing import Pool
    theta0 = theta_of(P0)
    theta = theta0.copy()
    W = {}
    hist = []
    with Pool(procs) as pool:
        for rnd in range(rounds):
            t = time.time()
            rs = pool.map(_job, [(c, ver, sc_dir, theta, P0, lam) for c in cs], chunksize=1)
            rs = [r for r in rs if r and "error" not in r]
            dd = sum(r["decoded_delta"] for r in rs)
            nh = sum(r["n"] for r in rs)
            for r in rs:
                pt, rows = W.get(r["slug"], (None, []))
                W[r["slug"]] = (r["phi_true"], rows + r["rows"])        # truth under the newest theta
            hist.append(dict(round=rnd, theta=theta.round(4).tolist(), wrong_holes_vs_right_cand=dd, holes=nh,
                             courses=len(rs), sec=round(time.time() - t, 1)))
            log(json.dumps(hist[-1]))
            theta_new, L = fit_theta(W, theta0, mu, fixed)
            if np.max(np.abs(theta_new - theta)) < 1e-3:
                theta = theta_new
                break
            theta = theta_new
    return theta, hist


def cmd_check(a):
    import route_bench as RB
    P0 = base_params()
    cs = [c for c in RB.courses("all") if c["slug"] in a.slugs.split(",")]
    for c in cs:
        x, d = load(c, a.ver, a.sc)
        cost, seq, pr = decode(d, x["card"], P0)
        ph, tot = phi(pr, seq)
        th = theta_of(P0)
        print(c["slug"], "solver", round(cost, 4), "phi-total", round(tot, 4), "theta.phi", round(float(th @ ph), 4))


def cmd_learn(a):
    import route_bench as RB
    P0 = base_params(json.loads(a.start or "{}"))
    cs = [c for c in RB.courses(a.split) if c.get("card")]
    os.makedirs(a.out, exist_ok=True)
    states = sorted({c["state"] for c in cs})
    fold = {s: i % a.folds for i, s in enumerate(states)}
    res = dict(groups=GROUPS, theta0=theta_of(P0).tolist(), folds={}, fold_of_state=fold)
    fixed = tuple(x for x in a.fixed.split(",") if x)

    def sc_dir_of(c):
        return (a.sc_big or a.sc) if RB.is_big(c["slug"]) else a.sc
    which = range(a.folds) if a.folds > 1 else []
    for i in list(which) + ["all"]:
        if a.only and str(i) not in a.only.split(","):
            continue
        tr = [c for c in cs if i == "all" or fold[c["state"]] != i]
        global _CACHE
        _CACHE = {}
        th, hist = run_rounds_mixed(tr, a.ver, sc_dir_of, P0, a.rounds, a.mu, a.lam, a.procs, fixed)
        res["folds"][str(i)] = dict(theta=th.tolist(), params=delta_params(th, P0), hist=hist,
                                    slugs=[c["slug"] for c in cs if i != "all" and fold[c["state"]] == i])
        json.dump(res, open(os.path.join(a.out, "struct.json"), "w"), indent=1)
        print("fold", i, json.dumps(res["folds"][str(i)]["params"]), flush=True)


def _job2(a):
    c, ver, sc_dir, theta, P0, lam = a
    try:
        return course_rows(c, ver, sc_dir, theta, P0, lam)
    except Exception as e:                                           # noqa: BLE001
        return dict(slug=c["slug"], error=repr(e)[:200])


def run_rounds_mixed(cs, ver, sc_dir_of, P0, rounds, mu, lam, procs, fixed=()):
    from multiprocessing import Pool
    theta0 = theta_of(P0)
    theta = theta0.copy()
    W = {}
    hist = []
    with Pool(procs) as pool:
        for rnd in range(rounds):
            t = time.time()
            rs = pool.map(_job2, [(c, ver, sc_dir_of(c), theta, P0, lam) for c in cs], chunksize=2)
            errs = [r for r in rs if r and "error" in r]
            rs = [r for r in rs if r and "error" not in r]
            dd = sum(r["decoded_delta"] for r in rs)
            nh = sum(r["n_right_cand"] for r in rs)
            for r in rs:
                pt, rows = W.get(r["slug"], (None, []))
                W[r["slug"]] = (r["phi_true"], rows + r["rows"])
            hist.append(dict(round=rnd, theta=[round(float(v), 4) for v in theta], wrong=dd, of=nh, courses=len(rs),
                             errors=len(errs), sec=round(time.time() - t, 1)))
            print(json.dumps(hist[-1]), errs[:2], flush=True)
            theta_new, L = fit_theta(W, theta0, mu, fixed)
            done = np.max(np.abs(theta_new - theta)) < 1e-3
            theta = theta_new
            if done:
                break
    # cutting-plane iterates oscillate: keep the one with the fewest wrong holes on its own training courses
    b = min(hist, key=lambda h: (h["wrong"], h["round"]))
    return np.array(b["theta"], float), hist


def cmd_evalfolds(a):
    """route_bench eval of each fold's courses with that fold's params (out-of-fold), merged -> a.out/eval_oof.json;
    --use all: every course with the all-course params (test)"""
    import subprocess
    import route_bench as RB
    S = json.load(open(os.path.join(a.out, "struct.json")))
    tmp = os.path.join(a.out, "_ev")
    os.makedirs(tmp, exist_ok=True)
    rs = []
    jobs = []
    if a.use == "all":
        cs = [c["slug"] for c in RB.courses(a.split) if c.get("card")]
        jobs.append(("all", cs, S["folds"]["all"]["params"]))
    else:
        for k, v in S["folds"].items():
            if k != "all":
                keep = {c["slug"] for c in RB.courses(a.split)}
                jobs.append((k, [s for s in v["slugs"] if s in keep], v["params"]))
    for k, slugs, params in jobs:
        if not slugs:
            continue
        o = os.path.join(tmp, f"{a.split}_{k}.json")
        env = dict(os.environ, ROUTER_PARAMS=json.dumps(dict(json.loads(a.start or "{}"), **params)))
        for sl in (slugs[i:i + 400] for i in range(0, len(slugs), 400)):
            subprocess.run([sys.executable, os.path.join(HERE, "route_bench.py"), "eval", "--scene", "fast", "--router", "v2",
                            "--card-only", "--prep", "--ver", a.ver, "--split", a.split, "--slugs", ",".join(sl),
                            "--procs", str(a.procs), "--out", o], env=env, check=True, capture_output=True)
            rs += json.load(open(o))["courses"]
    S2 = RB.summarise(rs)
    print(json.dumps({k: S2[k] for k in ("courses", "errors", "hole_acc", "all_right")}))
    json.dump(dict(summary=S2, courses=rs), open(os.path.join(a.out, f"eval_{a.split}_{a.use}.json"), "w"), default=float)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--use", default="oof")
    ap.add_argument("cmd")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--split", default="train")
    ap.add_argument("--ver", default="feae37f33_d0+yall")
    ap.add_argument("--sc", default=os.path.join(HERE, "cache", "val", "sc_split", "cv"))
    ap.add_argument("--sc-big", default="")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--only", default="")
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--mu", type=float, default=0.5)
    ap.add_argument("--lam", type=float, default=1.0)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--fixed", default="")
    ap.add_argument("--start", default="")
    ap.add_argument("--out", default=os.path.join(HERE, "cache", "val", "struct", "run"))
    a = ap.parse_args()
    if a.cmd == "check":
        cmd_check(a)
    elif a.cmd == "learn":
        cmd_learn(a)
    elif a.cmd == "evalfolds":
        cmd_evalfolds(a)
